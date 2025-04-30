from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    requester = fields.Char('Requester', readonly=True)

    po_request_id = fields.Many2one('po.request', readonly=True)
    po_request_count = fields.Integer('Count', readonly=True, compute='_compute_po_request_count')

    @api.depends('po_request_id')
    def _compute_po_request_count(self):
        for x in self:
            x.po_request_count = self.env['po.request'].search_count([('name', '=', x.po_request_id.name)])

    def action_view_related_po(self):
        return {
            'name': 'Related Po',
            'res_model': 'po.request',
            'view_mode': 'list,form',
            'domain': [('name', '=', self.po_request_id.name)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
