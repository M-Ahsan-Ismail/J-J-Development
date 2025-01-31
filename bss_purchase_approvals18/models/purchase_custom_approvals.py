from odoo import fields, models


class PurchaseCustomApprovals(models.Model):
    _inherit = 'purchase.order'
    _description = 'Custom Approvals'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('manager_approval', 'Manager Approval'),
        ('ceo_approval', 'CEO Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    def button_manager_approval(self):
        for order in self:
            order.write({'state': 'manager_approval'})
            order.message_subscribe([order.partner_id.id])

    def button_ceo_approved(self):
        for order in self:
            order.write({'state': 'ceo_approval'})
            order.message_subscribe([order.partner_id.id])

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'ceo_approval']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True









