from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError


class SaleCustomApprovals(models.Model):
    _inherit = 'sale.order'
    _description = 'Custom Sale Approvasls'

    SALE_ORDER_STATE = [
        ('draft', "Quotation"),
        ('manager_approval', 'Manager Approval'),
        ('ceo_approval', 'CEO Approval'),
        ('sent', "Quotation Sent"),
        ('sale', "Sales Order"),
        ('cancel', "Cancelled"),
    ]
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    def action_manager_approval(self):
        for x in self:
            x.state = 'manager_approval'

    def action_ceo_approval(self):
        for x in self:
            x.state = 'ceo_approval'
