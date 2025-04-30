from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Sale_Order_Inherit(models.Model):
    _inherit = 'sale.order'

    relevant_cost_sheet_id = fields.Many2one('cost.sheet.builder', string="Cost ID")
    related_cost_sheet_count = fields.Integer(compute='_compute_relevant_cost_sheet')

    @api.depends('relevant_cost_sheet_id')
    def _compute_relevant_cost_sheet(self):
        for x in self:
            x.related_cost_sheet_count = len(x.relevant_cost_sheet_id)

    def action_view_related(self):
        return {
            'name': 'Related Cost Sheet',
            'res_model': 'cost.sheet.builder',
            'view_mode': 'list,form',
            'domain': [('sale_order_ids', 'in', self.ids)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
