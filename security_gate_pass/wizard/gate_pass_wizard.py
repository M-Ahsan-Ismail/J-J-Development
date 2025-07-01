from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
import datetime

class Genrate_Gate_Pass_Wizard(models.TransientModel):
    _name = 'gate.pass'
    _description = 'Gate Pass Wizard'

    plot_no = fields.Char(string="Plot No")
    driver_name = fields.Many2one('res.partner', string='Driver')
    visit_date = fields.Datetime(string="Date Time Out", default=lambda self: fields.Datetime.now())
    vehicle_number = fields.Char(string="Vehicle Number")
    created_by = fields.Char(
        string="Created By",
        default=lambda self: self.env.user.name
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company.id,
        readonly=True,
    )
    visitor_purpose = fields.Char(string="Purpose")

    gate_pass_type = fields.Selection(
        [('inward', 'Inward'), ('outward', 'Outward')],
        string="Select Pass Type",
        default=lambda self: self._default_gate_pass_type()
    )

    # Rizwan
    store_incharge_id = fields.Many2one('res.users', 'Store Incharge')
    guard_id = fields.Many2one('res.partner', 'Guard')
    received_by = fields.Many2one('res.partner', 'Received By')

    def _default_gate_pass_type(self):
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        if picking.picking_type_id.code == 'incoming':
            return 'inward'
        return 'outward'

    def create_visitor_info(self):
        for wizard in self:
            pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids', []))
            if not pickings:
                raise ValidationError("No pickings selected.")
            if pickings.mapped('related_gate_pass_entry'):
                raise UserError('Gate pass Already Mapped.')

            all_lines = []
            labels = []

            for picking in pickings:
                for move in picking.move_ids_without_package:
                    all_lines.append((0, 0, {
                        'product_id': move.product_id.id,
                        'qty': move.quantity,
                        'product_uom': move.product_uom.id,
                    }))
                # Manually create the label type
                label = f"WH/IN/{picking.name}" if wizard.gate_pass_type == 'inward' else f"WH/OUT/{picking.name}"
                labels.append(label)

                if wizard.gate_pass_type == 'inward':
                    # Prevent duplicate inward
                    existing_inward = picking.related_gate_pass_entry.filtered(
                        lambda r: r.gate_pass_type == 'inward'
                    )
                    if existing_inward:
                        raise ValidationError(f"Inward Gate Pass already exists for {picking.name}")

            visitor_vals = {
                'gate_pass_type': wizard.gate_pass_type,
                'plot_no': wizard.plot_no,
                'driver_name': wizard.driver_name.name if wizard.driver_name else False,
                'visit_date': wizard.visit_date,
                'vehicle_number': wizard.vehicle_number,
                'created_by': wizard.created_by,
                'company_id': wizard.company_id.id,
                'visitor_purpose': wizard.visitor_purpose,
                'line_ids': all_lines,
                'label_type': ", ".join(labels),
                'store_incharge_id': wizard.store_incharge_id.id,
                'guard_id': wizard.guard_id.id,
                'received_by': wizard.received_by.id,
            }

            new_visitor = self.env['visitor.info'].create(visitor_vals)

            for picking in pickings:
                picking.write({
                    'related_gate_pass_entry': [(4, new_visitor.id)]
                })
