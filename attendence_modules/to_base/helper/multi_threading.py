import logging
import math
import os
import threading
import time

from threading import Thread

from odoo import models, registry, _
from odoo.models import PREFETCH_MAX
from odoo.tools import config
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropagatingThread(Thread):
    """This Thread extension helps:
    - return join() by the result of the `_target()`
    - raise error in threading mode
    """

    def run(self):
        self.exc = None
        try:
            self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super(PropagatingThread, self).join(timeout)
        if self.exc:
            raise self.exc
        return self.ret


class Threading:
    """ Decorate a record-style method to run the method into multiple threading

        class SomeModel(models.Model):

            @Threading()
            def method_1(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50)
            def method_2(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50, threaded_by='field')
            def method_3(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50, threaded_by='field.subfield')
            def method_3(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50, threaded_by='field', auto_commit=True)
            def method_4(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50, threaded_by='field', max_batch_size=1000)
            def method_5(self, *args, **kwargs):
                ...

            @Threading(db_connection_percentage=50, threaded_by='field', max_threads_per_threaded=8, auto_commit=True, max_batch_size=1)
            def method_6(self, *args, **kwargs):
                ...

    Known issues:
        - Multi-thread will be disabled in test mode. In other words, multi-threading will not be able to test

    @TODO: implement thread pool to optimize resource. For example,
        1. we have 2000 records to process
        2. max threads is 10, it means each thread is assigned to process 200 records

        The problem here is some tasks could get done sooner and we will have new available threads while
        other records still in queue in other remaining threads.
        If we have thread pool, we can reassign the remaining records for new available threads
    """

    def __init__(
            self,
            db_connection_percentage=None,
            threaded_by=None,
            max_threads_per_threaded=1,
            auto_commit=False,
            max_batch_size=None,
            timeout=None,
            flush=True
            ):
        """
        :param db_connection_percentage float: (optional) percentage of max db connection which is used to calculate number of threads.
            Default value is 10, that means 10% of the max db connections (but not exceed cpu count + 4) will be used for threading.
            For example, by default, Odoo starts with 64 connections as the max db connection. By passing 10 as
            db_connection_percentage, max. number of threads to be created will be 7, (taken from `math.ceil(64*10/100)`). But if the
            server has only 1 cpu, the number of threads will become 5 instead of 7.
        :param threaded_by str: Many2one relational field whose recordset will get threaded instead of the orginal records.
            Sub-field syntax (e.g. 'order_id.partner_id.country_id') is also supported
        :param max_threads_per_threaded int: when theading by the field specified in threaded_by,
            we can also set maximum threads for each threaded_by group. By default, max_threads_per_threaded is 1, it means that
            all the records of a single group run on a single thread only.
        :param auto_commit bool: if given with True value, cr.commit() will be called right after the the `method` is executed
        :param max_batch_size int: max number of records to process at once in the same thread. Default value is PREFETCH_MAX
        :param timeout int
        """
        # setup properties from the given arguments
        if db_connection_percentage and (db_connection_percentage < 0 or db_connection_percentage > 80):
            raise ValidationError(_("db_connection_percentage should be greater than or equal to 0 and less than or equal to 80"))
        self.db_connection_percentage = db_connection_percentage
        self.threaded_by = threaded_by
        self.max_threads_per_threaded = max_threads_per_threaded or 1
        if not isinstance(self.max_threads_per_threaded, int):
            raise ValidationError(_("max_threads_per_threaded must be an integer."))
        self.auto_commit = auto_commit
        self.max_batch_size = max_batch_size or PREFETCH_MAX
        self.timeout = timeout
        # other properties
        self.total_records = 0
        self.threading_groups = 0
        self.processed = 0
        self.ignore_error = False
        self.flush = flush

    def __call__(self, method):

        def _invalidate_records_cache(records, res_model_name, res_record_ids):
            records = records.env[res_model_name].browse(res_record_ids)
            records.invalidate_recordset()
            return records

        def validate_field(obj, field):
            """Validate if the given `field` which could be sub-field syntax
            (e.g. `order_id.partner_id.country_id`) is valid for the given model `obj`
            """
            field_split = field.split('.', 1)
            field_split_count = len(field_split)
            if field_split_count == 2:
                field, sub_field = field_split
            elif field_split_count == 1:
                field = field_split[0]
                sub_field = False
            else:
                return False
            if obj._fields.get(field):
                if obj._fields.get(field).type != 'many2one':
                    raise ValidationError(
                        _("Progamming Error! The field `%s` is not a Many2one field of the model %s's")
                        % (field, obj._name)
                        )
                if sub_field:
                    return validate_field(obj[field], sub_field)
                else:
                    return True
            else:
                raise ValidationError(
                    _("Progamming Error! The field `%s` is not a field of the model %s's")
                    % (field, obj._name)
                    )

        def _get_max_available_db_conn():
            db_registry = registry(self.dbname)
            while True:
                try:
                    with db_registry.cursor() as cr:
                        cr.execute(
                            "SELECT COUNT(*) FROM pg_stat_activity WHERE datname=%s AND state != %s",
                            (self.dbname, 'idle')
                            )
                        nbr_non_idle_connections = cr.fetchone()[0]
                    return config['db_maxconn'] - nbr_non_idle_connections
                except Exception:
                    time.sleep(1)

        def _set_max_threads():
            db_maxconn = _get_max_available_db_conn()
            # We use max_cpu_workers for default max_threads
            max_cpu_workers = (os.cpu_count() or 1) + 4 - threading.active_count()
            # ensure max_cpu_workers is greater than or equal to 1
            max_cpu_workers = max(max_cpu_workers, 1)
            if not self.db_connection_percentage:
                # limit max_threads to 10% max db connections but not more than max_cpu_workers
                self.max_threads = min(max_cpu_workers, math.ceil(db_maxconn * 0.1))
            else:
                if self.db_connection_percentage < 0 or self.db_connection_percentage > 80:
                    raise ValidationError(_("db_connection_percentage should be greater than or equal to 0 and less than or equal to 80"))
                # limit max_threads to db_connection_percentage% max db connections but not more than max_cpu_workers
                self.max_threads = min(max_cpu_workers, math.ceil(db_maxconn * self.db_connection_percentage / 100))
            # limit max_threads to 32 to avoid consuming surprisingly large resource
            self.max_threads = min(32, self.max_threads) or 1

        def _prepare_theading_groups(recordset):
            """Group records in the given recordset so that each group will run on a single thread
            while the self.max_threads and self.threaded_by and self.max_threads_per_threaded are respected.
            """
            _set_max_threads()
            threading_groups = []
            splittor = recordset.env['to.base'].splittor
            if self.threaded_by and validate_field(recordset, self.threaded_by):
                split_groups = recordset.mapped(self.threaded_by)
                split_groups_count = len(split_groups) or 1
                # Make sure total threads by all group will not exceed self.max_threads
                max_threads_per_threaded = min(self.max_threads_per_threaded, (self.max_threads // split_groups_count) or 1)
                batch_count = (split_groups_count // self.max_threads) + 1  # +1 for roundup
                for group in splittor(split_groups, batch_count):
                    grouped_records = recordset.filtered(lambda r: r.mapped(self.threaded_by).id in group.ids)
                    grouped_batch_count = (len(grouped_records) // max_threads_per_threaded) + 1  # +1 for roundup
                    for smaller_grouped_records in splittor(grouped_records, grouped_batch_count):
                        threading_groups.append(smaller_grouped_records)
            else:
                batch_count = (len(recordset) // self.max_threads) + 1  # +1 for roundup
                for smaller_recordset in splittor(recordset, batch_count):
                    threading_groups.append(smaller_recordset)
            return threading_groups

        def _execute(recordset, *args, **kwargs):
            rec_model = False
            rec_ids = []
            with recordset.pool.cursor() as cr:
                env = recordset.env(cr=cr)
                recordset = recordset.with_env(env)
                for records in env['to.base'].splittor(recordset, self.max_batch_size, flush=self.flush):
                    try:
                        with env.cr.savepoint(flush=self.flush):
                            res = method(records, *args, **kwargs)
                            if isinstance(res, models.Model):
                                if not rec_model:
                                    rec_model = res._name
                                rec_ids += res.ids
                        if self.auto_commit:
                            env.cr.commit()
                        self.processed += len(records)
                        _logger.debug("Finished multi-threading executing `%s` for %s/%s records", method, self.processed, self.total_records)
                    except Exception as e:
                        if self.auto_commit:
                            env.cr.rollback()
                        _logger.error("Error occurred when multi-threading executing %s. Here is debugging info: %s", method, str(e))
                        if not self.ignore_error:
                            raise
            if not rec_model:
                rec_model = recordset._name
            return recordset.env[rec_model].browse(rec_ids)

        def threaded(recordset, *args, **kwargs):
            """
            :param records: the recordset to be executed by the wrapped instance method in multi-threads mode
            :param args: arbitrary arguments given by the wrapped instance method. For example,

                @Threading()
                def instance_method(self, *args):
                    ...

            :param kwargs: keywords arguments given by the wrapped instance method. For example,

                @Threading()
                def instance_method(self, *kwargs):
                    ...
            """
            self.dbname = recordset._cr.dbname
            self.res_model = recordset._name

            self.total_records = len(recordset)
            self.ignore_error = recordset._context.get('ignore_error') or False

            # distributes records in the given recordset into threading_groups for multi-thread operation
            threading_groups = _prepare_theading_groups(recordset)
            self.threading_groups = len(threading_groups)
            # disable multi-threading if there is only one threading group or in test_mode
            # In the test environment, running multi-threading will lead to many unpredictable
            # cursor and savepoint related errors
            test_mode = getattr(threading.current_thread(), 'testing', False) or recordset.env.registry.in_test_mode()
            if self.threading_groups <= 1 or test_mode:
                if self.threading_groups <= 1:
                    _logger.debug("There is only %s threading group. Multi-threading is disabled.", self.threading_groups)
                if test_mode:
                    _logger.debug("Multi-threading is not supported in test mode and is disabled.")
                return method(recordset, *args, **kwargs)
            _logger.debug(
                "Starting the %s threads to process %s %s records",
                self.threading_groups,
                self.total_records,
                recordset._name
                )
            jobs = []
            for records in threading_groups:
                thread_name = "Threaded processing %s %s records" % (len(records), records._name)
                t = PropagatingThread(
                    name=thread_name,
                    target=_execute,
                    args=(records, *args),
                    kwargs=kwargs,
                    daemon=True
                    )
                t.start()
                _logger.debug(
                    "The thread `%s` has been started to process %s %s records",
                    thread_name,
                    len(records),
                    records._name
                    )
                jobs.append(t)
            # wait for all threads to finish
            res_record_ids = []
            res_model_name = False
            for j in jobs:
                res = j.join(self.timeout)
                if isinstance(res, models.Model):
                    res_record_ids += res.ids
                    if not res_model_name:
                        res_model_name = res._name
            if res_model_name:
                return _invalidate_records_cache(recordset, res_model_name, res_record_ids)
            else:
                return _invalidate_records_cache(recordset, recordset._name, recordset.ids)

        return threaded
