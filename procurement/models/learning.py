from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Procurment(models.Model):
    _inherit = 'po.request'

    approval_request_id = fields.Many2one('approval.request', string='Approval Request ID')

    def create_category_for_approval(self):
        existing_category = self.env['approval.category'].search([('name', '=', 'Procurement Approval')])
        if existing_category:
            return existing_category
        return self.env['approval.category'].create({
            'name': 'Procurement Approval',
            'company_id': self.env.company.id,
            'has_amount': 'no',
            'approval_minimum': 1,
        })

    def submit_to_approve(self):

        Category_id = self.create_category_for_approval()
        print('Approval Category', Category_id)

        request_id = self.env['approval.request'].create({
            'name': f'Procurment {self.name}',
            'category_id': Category_id.id,
            'request_owner_id': self.env.user.id,
            'procurement_id': self.id,
        })
        request_id.action_confirm()  # calling button submit to generate auto activities
        self.write({'approval_request_id': request_id})  # passing its id to our model for linking

        return super(Procurment, self).submit_to_approve()

    approval_request_count = fields.Integer('Approval Request Count', compute='_compute_approval_request_count')

    @api.depends('approval_request_id')
    def _compute_approval_request_count(self):
        Sc = self.env['approval.request'].search_count([('procurement_id', '=', self.id)])
        for x in self:
            x.approval_request_count = Sc

    def action_view_related_approval_requests(self):
        return {
            'name': 'Related Approval Requests',
            'res_model': 'approval.request',
            'view_mode': 'list,form',
            'domain': [('procurement_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class Inherit_Approval_Requests(models.Model):
    _inherit = 'approval.request'

    procurement_id = fields.Many2one('po.request', string='Procurement ID')

    po_request_count = fields.Integer('Po Request Count', compute='_compute_po_request_count')

    @api.depends('procurement_id')
    def _compute_po_request_count(self):
        Sc = self.env['po.request'].search_count([('approval_request_id', '=', self.id)])
        for x in self:
            x.po_request_count = Sc

    def action_view_related_po_requests(self):
        return {
            'name': 'Related Po Requests',
            'res_model': 'po.request',
            'view_mode': 'list,form',
            'domain': [('approval_request_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_approve(self):
        res = super(Inherit_Approval_Requests, self).action_approve()
        for rec in self:
            if rec.procurement_id:
                if not rec.approver_ids:
                    raise ValidationError(_('No approver found.'))
                else:
                    required_approvers = rec.approver_ids.filtered(lambda a: a.required)
                    if required_approvers:
                        if all(approver.status == 'approved' for approver in required_approvers):
                            rec.procurement_id.action_approve()
                    else:
                        if any(approver.status == 'approved' for approver in rec.approver_ids):
                            rec.procurement_id.action_approve()
        return res

    def action_cancel(self):
        for rec in self:
            rec.procurement_id.cancel_button()
        return super(Inherit_Approval_Requests, self).action_cancel()
