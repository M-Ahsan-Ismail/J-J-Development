from odoo import http

db_filter_core = http.db_filter


def db_filter(dbs, host=None):
    dbs = db_filter_core(dbs, host)
    custom_odoo_dbfilter = http.request and http.request.httprequest.environ.get('HTTP_X_ODOO_DBFILTER', '')
    if custom_odoo_dbfilter:
        return [custom_odoo_dbfilter]
    return dbs


http.db_filter = db_filter
