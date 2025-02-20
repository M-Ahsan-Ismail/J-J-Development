from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    for module in env['ir.module.module'].search([('icon', '=like', 'viin_brand/%')]):
        module.write({'icon': '/%s' % module.icon})
