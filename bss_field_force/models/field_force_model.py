from odoo import models, fields, api, _


class FieldForce(models.Model):
    _name = 'field.force'
    _order = 'create_date desc'
    _rec_name = 'name'

    user_id = fields.Many2one('res.users', string='Salesman', required=True, default='Salesman')
    partner_id = fields.Many2one('res.partner', 'Customer', store=True)

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    route_plan_id = fields.Many2one('route.planing', 'Route ID')

    partner_address = fields.Char('Address')
    action_check_in = fields.Selection([('checkin', 'Check In')])
    action_check_out = fields.Selection([('checkout', 'Check Out')])
    latitude_in = fields.Float('Latitude In', digits=(16, 8))
    latitude_out = fields.Float('Latitude Out', digits=(16, 8))
    longitude_in = fields.Float('Longitude In', digits=(16, 8))
    longitude_out = fields.Float('Longitude Out', digits=(16, 8))
    check_in_address = fields.Char('Check In Address')
    check_out_address = fields.Char('Check Out Address')
    check_in_time = fields.Datetime('Check In Time')
    check_out_time = fields.Datetime('Check Out Time')

    total_time_spent = fields.Float('Total Time Spent (hours)', compute='_compute_total_time', store=True,
                                    digits=(12, 2))

    related_route_plan_count = fields.Integer('Count of Route Plans', compute='_compute_relevant_route_plans',
                                              store=True)

    start_location = fields.Html(
        string="Start",
        compute="_compute_map_links",
        sanitize=False
    )
    end_location = fields.Html(
        string="End",
        compute="_compute_map_links",
        sanitize=False
    )

    def _compute_map_links(self):
        for rec in self:
            if rec.latitude_in and rec.longitude_in:
                rec.start_location = f"""
                    <a href="https://www.google.com/maps?q={rec.latitude_in},{rec.longitude_in}" 
                       target="_blank" style="color:#1a73e8; text-decoration:none;">
                       📍 Start
                    </a>
                """
            else:
                rec.start_location = "<span style='color:#999;'>N/A</span>"

            if rec.latitude_out and rec.longitude_out:
                rec.end_location = f"""
                    <a href="https://www.google.com/maps?q={rec.latitude_out},{rec.longitude_out}" 
                       target="_blank" style="color:#d93025; text-decoration:none;">
                       🚩 End
                    </a>
                """
            else:
                rec.end_location = "<span style='color:#999;'>N/A</span>"

    @api.depends('check_in_time', 'check_out_time')
    def _compute_total_time(self):
        for rec in self:
            if rec.check_in_time and rec.check_out_time:
                delta = rec.check_out_time - rec.check_in_time
                rec.total_time_spent = delta.total_seconds() / 3600.0
            else:
                rec.total_time_spent = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('field.force.sequence') or _('New')
        return super(FieldForce, self).create(vals)

    @api.depends('route_plan_id')
    def _compute_relevant_route_plans(self):
        for x in self:
            x.related_route_plan_count = len(x.route_plan_id)

    def action_view_related(self):
        return {
            'name': 'Related Route Plan',
            'res_model': 'route.planing',
            'view_mode': 'list,form',
            'domain': [('field_force_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
