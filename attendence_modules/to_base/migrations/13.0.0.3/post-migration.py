from odoo import api, SUPERUSER_ID

from odoo.addons.to_base import _update_brand_web_icon_data


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_brand_web_icon_data(env)
