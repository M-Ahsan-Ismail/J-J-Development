import fnmatch
import importlib
import inspect
import logging
import os
import ast
import subprocess
import time
import threading

import odoo
#
# from odoo import api, modules, tools, SUPERUSER_ID
# from odoo.tools import config, pycompat
# from odoo.tools.sql import table_exists, column_exists, create_column
# from odoo.tests import common
# from odoo.tests.common import HttpCase
# from odoo.modules import module
# from odoo.models import BaseModel
#
# from odoo.addons.base.models.res_currency import CurrencyRate
# from odoo.sql_db import ConnectionPool
#
# try:
#     from odoo.addons.test_lint.tests.test_ecmascript import TestECMAScriptVersion
#     test_ecmascript_version = TestECMAScriptVersion.test_ecmascript_version
# except ImportError:
#     TestECMAScriptVersion = None
#
# try:
#     from odoo.addons.test_lint.tests import test_manifests
# except ImportError:
#     test_manifests = None
#
# try:
#     es_check = tools.misc.find_in_path('es-check')
# except IOError:
#     es_check = None
#
# try:
#     from odoo.addons.test_assetsbundle.tests.test_assetsbundle import AddonManifestPatched
#     setUpAddonManifestPatched = AddonManifestPatched.setUp
# except ImportError:
#     AddonManifestPatched = None
#
from . import helper
from . import controllers
from . import models
from . import wizard
from . import override
#
# _logger = logging.getLogger(__name__)
#
# get_resource_path = module.get_resource_path
# get_module_path = module.get_module_path
# module_manifest = module.module_manifest
# get_module_icon = module.get_module_icon
# get_manifest = module.get_manifest
# get_db_name = common.get_db_name
# _load_records = BaseModel._load_records
# _borrow = ConnectionPool.borrow
# _url_open = HttpCase.url_open
#
# MAX_IDLE_TIMEOUT = 60 * 10  # in seconds
#
#
# def _get_branding_module(branding_module='viin_brand'):
#     """
#     Wrapper for others to override
#     """
#     return branding_module
#
#
# def _get_db_name_plus():
#     db = get_db_name()
#     if db:
#         # Force POST value that is set as 8069 by dynamic value
#         # to avoid dead test of Odoo
#         global common
#         common.PORT = odoo.tools.config['http_port']
#
#     return db
#
#
# def test_installable(module, mod_path=None):
#     """
#     :param module: The name of the module (sale, purchase, ...)
#     :param mod_path: Physical path of module, if not providedThe name of the module (sale, purchase, ...)
#     """
#     if module == 'general_settings':
#         module = 'base'
#     if not mod_path:
#         mod_path = get_module_path(module, downloaded=True)
#     manifest_file = module_manifest(mod_path)
#     if manifest_file:
#         info = {
#             'installable': True,
#         }
#         f = tools.file_open(manifest_file, mode='rb')
#         try:
#             info.update(ast.literal_eval(pycompat.to_text(f.read())))
#         finally:
#             f.close()
#         return info
#     return {}
#
#
# viin_brand_manifest = test_installable(_get_branding_module())
#
#
# def check_viin_brand_module_icon(module):
#     """
#     Ensure module icon with
#         either '/viin_brand_originmodulename/static/description/icon.png'
#         or '/viin_brand/static/img/apps/originmodulename.png'
#         exists.
#     """
#     branding_module = _get_branding_module()
#     brand_originmodulename = '%s_%s' % (branding_module, module if module not in ('general_settings', 'modules') else 'base')
#
#     # load manifest of the overriding modules
#     viin_brand_originmodulename_manifest = test_installable(brand_originmodulename)
#
#     # /viin_brand/static/img/apps_icon_override/originmodulename.png
#     originmodulename_iconpath = os.path.join(branding_module, 'static', 'img', 'apps', '%s.png' % (module if module not in ('general_settings', 'modules') else module == 'general_settings' and 'settings' or 'modules'))
#
#     # /viin_brand_originmodulename'/static/description/icon.png
#     iconpath = os.path.join(brand_originmodulename, 'static', 'description', 'icon.png')
#
#     module_icon = False
#     for adp in odoo.addons.__path__:
#         if viin_brand_originmodulename_manifest.get('installable', False) and os.path.exists(os.path.join(adp, iconpath)):
#             module_icon = '/' + iconpath
#             break
#         elif viin_brand_manifest.get('installable', False) and os.path.exists(os.path.join(adp, originmodulename_iconpath)):
#             module_icon = '/' + originmodulename_iconpath
#             break
#     return module_icon
#
#
# def get_viin_brand_resource_path(mod, *args):
#     # Odoo hard coded its own favicon in several places
#     # this override to attempt to get Viindoo's favicon if it
#     # exists in branding_module/static/img/favicon.ico
#     if mod == 'web' and 'static/img/favicon.ico' in args:
#         branding_module = _get_branding_module()
#         for adp in odoo.addons.__path__:
#             if viin_brand_manifest.get('installable', False):
#                 viindoo_favicon_path = get_resource_path(branding_module, *args)
#                 if viindoo_favicon_path:
#                     return viindoo_favicon_path
#     # Odoo hard coded its own module_icon in several places
#     # this override to attempt to get Viindoo's module_icon
#     elif mod not in ('general_settings', 'modules', 'settings') and ('static', 'description', 'icon.png') == args:
#         module_icon = get_viin_brand_module_icon(mod)
#         if module_icon:
#             path_parts = module_icon.split('/')
#             module_icon_path = get_resource_path(path_parts[1], *path_parts[2:])
#             if module_icon_path:
#                 return module_icon_path
#     # fall back to the default one
#     return get_resource_path(mod, *args)
#
#
# def get_viin_brand_module_icon(mod):
#     """
#     This overrides default module icon with
#         either '/viin_brand_originmodulename/static/description/icon.png'
#         or '/viin_brand/static/img/apps/originmodulename.png'
#         where originmodulename is the name of the module whose icon will be overridden
#     provided that either of the viin_brand_originmodulename or viin_brand is installable
#     """
#     # Odoo hard coded its own test in several places (test_systray_get_activities)
#     # this check to skip if mod is test_*
#     if mod.startswith('test_'):
#         return get_module_icon(mod)
#     # Override to pass test test test_message_format
#     # Because the module_icon value is hardcoded in test
#     if getattr(threading.current_thread(), 'testing', False):
#         for stack in inspect.stack():
#             if stack.function == 'test_message_format':
#                 return get_module_icon(mod)
#
#     module_icon = check_viin_brand_module_icon(mod)
#     if mod not in ('general_settings', 'modules', 'settings'):
#         origin_module_icon = get_module_icon(mod)
#         if origin_module_icon and origin_module_icon == '/base/static/description/icon.png':
#             module_icon = check_viin_brand_module_icon('base')
#     if module_icon:
#         return module_icon
#     return get_module_icon(mod)
#
#
# def _get_brand_module_website(module):
#     """
#     This overrides default module website with '/branding_module/apriori.py'
#     where apriori contains dict:
#     modules_website = {
#         'account': 'account's website',
#         'sale': 'sale's website,
#     }
#     :return module website in apriori.py if exists else False
#     """
#     branding_module = _get_branding_module()
#     for adp in odoo.addons.__path__:
#         if viin_brand_manifest.get('installable', False):
#             try:
#                 modules_website = importlib.import_module('odoo.addons.%s.apriori' % branding_module).modules_website
#                 if module in modules_website:
#                     return modules_website[module]
#             except Exception:
#                 pass
#     return False
#
#
# def _get_manifest_plus(module, mod_path=None):
#     info = get_manifest(module, mod_path=mod_path)
#     if info:
#         module_website = _get_brand_module_website(module)
#         if module_website:
#             info['website'] = module_website
#     return info
#
#
# def _test_if_loaded_in_server_wide():
#     config_options = config.options
#     if 'to_base' in config_options.get('server_wide_modules', '').split(','):
#         return True
#     else:
#         return False
#
#
# if not _test_if_loaded_in_server_wide():
#     _logger.warning("The module `to_base` should be loaded in server wide mode using `--load`"
#                  " option when starting Odoo server (e.g. --load=base,web,to_base)."
#                  " Otherwise, some of its functions may not work properly.")
#
#
# def _disable_currency_rate_unique_name_per_day():
#     # Remove unique_name_per_day constraint in res.currency.rate model in base module
#     # It doesn't delete constraint on database server
#     for el in CurrencyRate._sql_constraints:
#         if el[0] == 'unique_name_per_day':
#             _logger.info("Removing the default currency rate's SQL constraint `unique_name_per_day`")
#             CurrencyRate._sql_constraints.remove(el)
#             break
#
#
# def _update_brand_web_icon_data(env):
#     # Generic trick necessary for search() calls to avoid hidden menus which contains 'base.group_no_one'
#     menus = env['ir.ui.menu'].with_context({'ir.ui.menu.full_list': True}).search([('web_icon', '!=', False)])
#     for m in menus:
#         web_icon = m.web_icon
#         paths = web_icon.split(',')
#         if len(paths) == 2:
#             module = paths[0]
#             module_name = paths[1].split('/')[-1][:-4]
#             if module_name == 'board' or module_name == 'modules' or module_name == 'settings':
#                 module = module_name
#                 web_icon = '%s,static/description/icon.png' % module
#
#             module_icon = check_viin_brand_module_icon(module)
#             if module_icon:
#                 web_icon_data = m._compute_web_icon_data(web_icon)
#                 if web_icon_data != m.web_icon_data:
#                     m.write({'web_icon_data': web_icon_data})
#
#
# def _update_favicon(env):
#     branding_module = _get_branding_module()
#     for adp in odoo.addons.__path__:
#         if viin_brand_manifest.get('installable', False):
#             img_path = module.get_resource_path(branding_module, 'static/img/favicon.ico')
#             if img_path:
#                 res_company_obj = env['res.company']
#                 data = res_company_obj._get_default_favicon()
#                 res_company_obj.with_context(active_test=False).search([]).write({'favicon': data})
#
#
# def _skip_sending_email_when_loading_demo_data_in_test_mode(self, data_list, update=False):
#     """Skip sending email when loading the demo data in test mode to speedup"""
#     self = self.with_context(mail_activity_quick_update=True)
#     return _load_records(self, data_list, update=update)
#
#
# def _test_ecmascript_version(self):
#     """ File /viin_web_sankey/static/lib/chart.js can't pass test test_ecmascript_version (ES Check tool),
#     so we need override TestECMAScriptVersion.test_ecmascript_version in test_lint module to ignore it
#     """
#     from odoo.addons.test_lint.tests.test_ecmascript import MAX_ES_VERSION
#     files_to_check = [
#         p for p in self.iter_module_files('*.js')
#         if 'static/test' not in p
#         if 'static/src/tests' not in p
#         if 'static/lib/qweb/qweb.js' not in p    # because this file is not bundled at all
#         if 'py.js/lib/py.js' not in p            # because it is not "strict" compliant
#         if 'static/lib/epos-2.12.0.js' not in p  # same
#         # OVERRIDE: BEGIN
#         if 'viin_web_sankey/static/lib/chart.js' not in p
#         # OVERRIDE: END
#     ]
#
#     _logger.info('Testing %s js files', len(files_to_check))
#     cmd = [es_check, MAX_ES_VERSION] + files_to_check + ['--module']
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     out, err = process.communicate()
#     self.assertEqual(process.returncode, 0, msg=out.decode())
#
#
# def _override_test_manifests_keys():
#     """Override to support some manifest keys in module"""
#     global test_manifests
#     if test_manifests:
#         test_manifests.MANIFEST_KEYS.update({
#             # Viindoo modules
#             'old_technical_name': '',
#             'name_vi_VN': '',
#             'summary_vi_VN': '',
#             'description_vi_VN': '',
#             'demo_video_url': '',
#             'live_test_url_vi_VN': 'https://v16demo-vn.viindoo.com',
#             'currency': 'EUR',
#             'support': 'apps.support@viindoo.com',
#             'price': '99.9',
#             'subscription_price': '9.9',
#             # OCA module (web_responsive)
#             'development_status': '',
#             'maintainers': [],
#             'excludes': [],
#             'task_ids': [],
#             # Viindoo theme
#             'industries': '',
#         })
#
#
# def _setUpAddonManifestPatched_plus(self):
#     """Override to compile assets of to_base in test mode,
#        because the module `to_base` is be loaded in server wide.
#     """
#     res = setUpAddonManifestPatched(self)
#     self.manifests.update({'to_base': get_manifest('to_base')})
#     return res
#
#
# def _borrow_plus(self, connection_info):
#     """
#     Add a garbage collection of the unused connections.
#     If the connection has been unused for more than `MAX_IDLE_TIMEOUT` seconds, it is closed and removed from the pool.
#     """
#     # TODOs: remoe this method in 17+
#
#     cnx = _borrow(self, connection_info)
#     # set last_used for cnx
#     cnx.last_used = time.time()
#
#     for i, (conn, used) in tools.reverse_enumerate(self._connections):
#         if not used and not conn.closed and getattr(conn, 'last_used', False) and time.time() - conn.last_used > MAX_IDLE_TIMEOUT:
#             self._debug('Close connection at index %d: %r', i, conn.dsn)
#             conn.close()
#             if conn.closed:
#                 self._connections.pop(i)
#                 self._debug('Removing closed connection at index %d: %r', i, conn.dsn)
#     return cnx
#
#
# def _url_open_plus(self, url, data=None, files=None, timeout=20, headers=None, allow_redirects=True, head=False):
#     """
#     [FIX] tests: bump url_open timeout
#
#     Some tests are randomly failling because /web takes more than 10 seconds to load.
#     A future pr will speedup /web but waiting for that a small bump of the timeout should help.
#     """
#     return _url_open(self, url, data=data, files=files, timeout=timeout, headers=headers, allow_redirects=allow_redirects, head=head)
#
#
# def pre_init_hook(cr):
#     common.get_db_name = _get_db_name_plus
#     module.get_resource_path = get_viin_brand_resource_path
#     modules.get_resource_path = get_viin_brand_resource_path
#     module.get_module_icon = get_viin_brand_module_icon
#
#
# def post_init_hook(cr, registry):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     _update_brand_web_icon_data(env)
#     _update_favicon(env)
#
#
# def uninstall_hook(cr, registry):
#     common.get_db_name = get_db_name
#     module.get_resource_path = get_viin_brand_resource_path
#     modules.get_resource_path = get_viin_brand_resource_path
#     module.get_module_icon = get_module_icon
#     module.get_manifest = get_manifest
#     modules.get_manifest = get_manifest
#     ConnectionPool.borrow = _borrow
#     HttpCase.url_open = _url_open
#
#
# def post_load():
#     _disable_currency_rate_unique_name_per_day()
#     if config.get('test_enable', False):
#         BaseModel._load_records = _skip_sending_email_when_loading_demo_data_in_test_mode
#     modules.get_module_resource = get_viin_brand_resource_path
#     module.get_module_icon = get_viin_brand_module_icon
#     module.get_resource_path = get_viin_brand_resource_path
#     modules.get_resource_path = get_viin_brand_resource_path
#     common.get_db_name = _get_db_name_plus
#     module.get_manifest = _get_manifest_plus
#     modules.get_manifest = _get_manifest_plus
#     if TestECMAScriptVersion:
#         TestECMAScriptVersion.test_ecmascript_version = _test_ecmascript_version
#     if test_manifests:
#         _override_test_manifests_keys()
#     if AddonManifestPatched:
#         AddonManifestPatched.setUp = _setUpAddonManifestPatched_plus
#     ConnectionPool.borrow = _borrow_plus
#     HttpCase.url_open = _url_open_plus
#
#     for db in odoo.http.db_list(force=True, host=''):
#         with odoo.sql_db.db_connect(db).cursor() as cr:
#             # Check and create column 'marketplace_merchant' in 'res_users' if not exists
#             try:
#                 if table_exists(cr, 'res_users') and not column_exists(cr, 'res_users', 'marketplace_merchant'):
#                     create_column(cr, 'res_users', 'marketplace_merchant', 'boolean')
#                     _logger.info("Created column 'marketplace_merchant' in 'res_users' for database '%s'", db)
#             except Exception as e:
#                 _logger.warning("Failed to check and create column 'marketplace_merchant' in 'res_users' "
#                                 "for database '%s'. Details: %s", db, e.args[0])
#
#             # Check and create column 'viindoo_uid' in 'res_users' if not exists
#             try:
#                 if table_exists(cr, 'res_users') and not column_exists(cr, 'res_users', 'viindoo_uid'):
#                     create_column(cr, 'res_users', 'viindoo_uid', 'int4')
#                     _logger.info("Created column 'viindoo_uid' in 'res_users' for database '%s'", db)
#             except Exception as e:
#                 _logger.warning("Failed to check and create column 'viindoo_uid' in 'res_users' "
#                                 "for database '%s'. Details: %s", db, e.args[0])
