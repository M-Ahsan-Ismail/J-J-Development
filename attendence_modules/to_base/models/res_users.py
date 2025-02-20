from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    # this field is for the SaaS to charge instances having marketplace users. See the module viin_marketplace
    # marketplace_merchant = fields.Boolean(
    #     default=False, string='Marketplace Merchant User', store=True,
    #     help="External user with limited access to marketplace merchant functionalities"
    #     )

    @api.depends('groups_id')
    def _compute_marketplace_merchant(self):
        self.marketplace_merchant = False
