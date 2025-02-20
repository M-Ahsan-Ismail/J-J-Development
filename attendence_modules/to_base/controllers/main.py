from contextlib import closing

import psycopg2

import odoo
from odoo import http
from odoo.service.db import _initialize_db
from odoo.http import request
from odoo import _


class Database(http.Controller):
    @http.route('/api/saas/initialize_database', type='json', auth='none')
    def create(self, **kw):  # pylint: disable=method-required-super
        master_pwd = request.dispatcher.jsonrequest.get('master_pwd')
        name = request.dispatcher.jsonrequest.get('name')
        lang = request.dispatcher.jsonrequest.get('lang')
        password = request.dispatcher.jsonrequest.get('password')
        secure = odoo.tools.config.verify_admin_password(master_pwd)
        if secure:
            db = odoo.sql_db.db_connect('postgres')
            with closing(db.cursor()) as cr:
                cr.execute("SELECT datname FROM pg_database WHERE datname = %s",
                           (name,), log_exceptions=False)
                if not cr.fetchall():
                    return {'status': False, 'message': _('Database does not exist in server.')}
            if odoo.tools.config['unaccent']:
                try:
                    db = odoo.sql_db.db_connect(name)
                    with closing(db.cursor()) as cr:
                        cr.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
                        # pylint: disable=invalid-commit
                        cr.commit()
                except psycopg2.Error as e:
                    return {'status': False, 'message': e}
            demo = bool(request.dispatcher.jsonrequest.get('demo'))
            login = request.dispatcher.jsonrequest.get('login')
            country_code = request.dispatcher.jsonrequest.get('country_code', False)
            phone = request.dispatcher.jsonrequest.get('phone')
            _initialize_db(id, name, demo, lang, password, login, country_code, phone)
            return {'status': True}
        return {'status': False, 'message': _('Master password is not correct.')}
