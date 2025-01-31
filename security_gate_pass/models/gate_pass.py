from odoo import _, api, fields, models ,_
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError



class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    related_gate_pass_entry = fields.Many2many(
        'visitor.info',
        'stock_visitor_relation', # Name of relation
        'current_model_id',   # for storing current model id
        'related_model_id',   # for storing related model id
        string="Related Gate Pass Entries",
        store=True
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
    _rec_name = 'sequence_gate_pass'

    plot_no = fields.Char(string="Plot No")
    driver_name = fields.Char(string='Driver')
    visit_date = fields.Date(string="Time")
    vehicle_number = fields.Char(string="Vehicle Number")
    created_by = fields.Char(string="Created By")
    company_id = fields.Many2one('res.company', string="Company")
    visitor_purpose = fields.Char(string="Purpose")



    gate_pass_type = fields.Selection([('inward','Inward'),('outward','Outward'),], string="Type")
    related_picking_id = fields.Many2one('stock.picking', 'Related Picking')
    line_ids = fields.One2many('visitor.info.lines', 'visitor_id', 'Lines ID')
    sequence_gate_pass = fields.Char(readonly=True, copy=False, default=lambda self: _('New'))
    label_type = fields.Char(compute='_compute_label_type')

    @api.depends('sequence_gate_pass', 'gate_pass_type')
    def _compute_label_type(self):
        for x in self:
            if x.gate_pass_type == 'inward' and x.sequence_gate_pass:
                x.label_type = f'WH/IN/{x.sequence_gate_pass}'
            elif x.gate_pass_type == 'outward' and x.sequence_gate_pass:
                x.label_type = f'WH/OUT/{x.sequence_gate_pass}'
            else:
                x.label_type = ''

    @api.depends('sequence_gate_pass','gate_pass_type')
    def _compute_label_type(self):
        for record in self:
            if record.gate_pass_type == 'inward' and record.sequence_gate_pass:
                record.label_type = f'WH/IN/{record.sequence_gate_pass}'
            elif record.gate_pass_type == 'outward' and record.sequence_gate_pass:
                record.label_type = f'WH/OUT/{record.sequence_gate_pass}'
            else:
                record.label_type = ''


    count_relevant_inventory = fields.Integer('Count Relevant Inventory',compute='_compute_relevant_inventory')

    @api.depends('related_picking_id')
    def _compute_relevant_inventory(self):
        for x in self:
            relevent_counts = self.env['stock.picking'].search_count([('related_gate_pass_entry', '=', x.id)])
            x.count_relevant_inventory = relevent_counts

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
                print(f"Generated Reference No: {vals['sequence_gate_pass']}")
            elif vals.get('gate_pass_type') == 'outward':
                vals['sequence_gate_pass'] = self.env['ir.sequence'].next_by_code('gate.pass.outward') or _('New')
                print(f"Generated Number: {vals['sequence_gate_pass']}")
        return super(VisitorInfo, self).create(vals)




class VisitorInfoLines(models.Model):
    _name = 'visitor.info.lines'
    _description = 'Visitor lines'

    visitor_id = fields.Many2one('visitor.info', string="Visitor")

    products = fields.Char(string="Product")
    qty = fields.Float(string="Quantity")

