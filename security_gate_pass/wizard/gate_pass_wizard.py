from odoo import fields, models, api
import datetime

class Genrate_Gate_Pass_Wizard(models.TransientModel):
    _name = 'gate.pass'
    _description = 'Gate Pass Wizard'


    plot_no = fields.Char(string="Plot No")
    driver_name = fields.Many2one('res.partner', string='Driver')
    visit_date = fields.Date(string="Date Time Out", default=datetime.datetime.now())
    vehicle_number = fields.Char(string="Vehicle Number")
    created_by = fields.Char(
        string="Created By",
        default=lambda self: self.env.user.name
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company.name
    )

    visitor_purpose = fields.Char(string="Purpose")
    gate_pass_type = fields.Selection([('inward', 'Inward'), ('outward', 'Outward'), ], string="Select Pass Type",
                                      default=None)

    def create_visitor_info(self):
        for visitor in self:
            related_picking = self.env['stock.picking'].browse(self._context.get('active_id'))
            print('Id: ', related_picking)

            Lines_Data = []
            for row in related_picking.move_ids_without_package:
                Lines_Data.append((0, 0, {'products': row.product_id.name,
                                          'qty': row.quantity,
                                          }))

            vals = {
                'gate_pass_type': visitor.gate_pass_type,
                'plot_no': visitor.plot_no if visitor.plot_no else False,
                'driver_name': visitor.driver_name.name if visitor.driver_name else False,
                'visit_date': visitor.visit_date if visitor.visit_date else False,
                'vehicle_number': visitor.vehicle_number if visitor.vehicle_number else False,
                'created_by': visitor.created_by if visitor.created_by else False,
                'company_id': visitor.company_id.id if visitor.company_id else False,
                'visitor_purpose': visitor.visitor_purpose if visitor.visitor_purpose else False,
                'line_ids': Lines_Data
            }

            new_visitor = self.env['visitor.info'].create(vals)
            related_picking.write({
                'related_gate_pass_entry': [(4, new_visitor.id)]
            })


