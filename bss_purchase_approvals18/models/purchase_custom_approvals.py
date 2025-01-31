from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError


class PurchaseCustomApprovals(models.Model):
    _inherit = 'purchase.order'
    _description = 'Custom Approvasls'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('manager_approval', 'Manager Approval'),
        ('ceo_approval', 'CEO Approval'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def action_approval_manager(self):
        for x in self:
            x.state = 'manager_approval'

    def action_approval_ceo(self):
        for x in self:
            x.state = 'ceo_approval'



    # def button_draft(self):
    #     res = super(PurchaseCustomApprovals,self).button_draft()
    #     for x in self:
    #         x.state = 'draft'
    #     return res

    # def print_quotation(self):
    #     res = super(PurchaseCustomApprovals,self).print_quotation()
    #     for x in self:
    #         x.state = 'sent'
    #     return res
    #
    def action_rfq_send(self):
        res = super(PurchaseCustomApprovals,self).action_rfq_send()
        for x in self:
            x.state = 'sent'
        return res
    #
    # def button_confirm(self):
    #     res = super(PurchaseCustomApprovals, self).button_confirm()
    #     for order in self:
    #         order.state = 'purchase'
    #     return res
    #
    # def button_cancel(self):
    #     res = super(PurchaseCustomApprovals,self).button_cancel()
    #     for x in self:
    #         x.state = 'cancel'
    #     return res
    #
    # def button_done(self):
    #     res = super(PurchaseCustomApprovals,self).button_done()
    #     for x in self:
    #         x.state = 'done'
    #     return res
