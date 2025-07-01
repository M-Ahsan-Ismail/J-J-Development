from odoo import _, api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    related_gate_pass_entry = fields.Many2many(
        'visitor.info',
        'stock_visitor_relation',  # Name of relation
        'current_model_id',  # for storing current model id
        'related_model_id',  # for storing related model id
        string="Related Gate Pass Entries",
        store=True,
    )

    count_relevant_gate_passes = fields.Integer('Relevant Gate Passes', compute='_compute_relevant_passes')

    @api.depends('related_gate_pass_entry')
    def _compute_relevant_passes(self):
        for x in self:
            relevent_counts = self.env['visitor.info'].search_count([('id', 'in', self.related_gate_pass_entry.ids)])
            x.count_relevant_gate_passes = relevent_counts

    def action_view_related(self):
        return {
            'name': 'Related Gate Passes',
            'res_model': 'visitor.info',  # Change to correct model
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.related_gate_pass_entry.ids)],  # Correct field
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class VisitorInfo(models.Model):
    _name = 'visitor.info'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_gate_pass'
    _description = 'Visitor Info Record'

    plot_no = fields.Char(string="Plot No", tracking=True)
    driver_name = fields.Char(string='Driver', tracking=True)
    visit_date = fields.Datetime(string="Time", tracking=True)
    vehicle_number = fields.Char(string="Vehicle Number", tracking=True)
    created_by = fields.Char(string="Created By", tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id.id,
        readonly=True
    )
    visitor_purpose = fields.Char(string="Purpose", tracking=True)
    gate_pass_type = fields.Selection(
        [('inward', 'Inward'), ('outward', 'Outward')],
        string="Type"
    )
    related_picking_id = fields.Many2one('stock.picking', string='Related Picking (Optional)')
    line_ids = fields.One2many('visitor.info.lines', 'visitor_id', string='Lines')
    sequence_gate_pass = fields.Char(readonly=True, copy=False, default=lambda self: _('New'))
    label_type = fields.Char(string="Label Type")  # filled by wizard manually

    count_relevant_inventory = fields.Integer('Count Relevant Inventory', compute='_compute_relevant_inventory')
    # Rizwan
    store_incharge_id = fields.Many2one('res.users', 'Store Incharge')
    guard_id = fields.Many2one('res.partner', 'Guard')
    received_by = fields.Many2one('res.partner', 'Received By')

    @api.depends('related_picking_id')
    def _compute_relevant_inventory(self):
        for record in self:
            count = self.env['stock.picking'].search_count([('related_gate_pass_entry', '=', record.id)])
            record.count_relevant_inventory = count

    def action_view_related(self):
        return {
            'name': f'Delivery/Receipt {self.id}',
            'res_model': 'stock.picking',
            'view_mode': 'list,form',
            'domain': [('related_gate_pass_entry', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        if vals.get('sequence_gate_pass', _('New')) == _('New'):
            if vals.get('gate_pass_type') == 'inward':
                vals['sequence_gate_pass'] = self.env['ir.sequence'].next_by_code('gate.pass.inward') or _('New')
            elif vals.get('gate_pass_type') == 'outward':
                vals['sequence_gate_pass'] = self.env['ir.sequence'].next_by_code('gate.pass.outward') or _('New')
        return super(VisitorInfo, self).create(vals)

    def unlink(self):
        for record in self:
            record.line_ids.unlink()
        return super().unlink()

class VisitorInfoLines(models.Model):
    _name = 'visitor.info.lines'
    _description = 'Visitor lines'

    visitor_id = fields.Many2one('visitor.info', string="Gate Pass")
    gate_pass_type = fields.Selection(
        [('inward', 'Inward'), ('outward', 'Outward')],
        string="Type"
    )
    product_id = fields.Many2one('product.product',string="Product")
    product_uom = fields.Many2one('uom.uom',string="UOM")
    qty = fields.Float(string="Quantity")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('visitor_id'):
            gatepass = self.env['visitor.info'].search([('id', '=', vals['visitor_id'])])
            res.gate_pass_type = gatepass.gate_pass_type
        return res
