from odoo import models, fields, api, _


class RoutePlaning(models.Model):
    _name = 'route.planing'
    _description = 'Route Planning'
    _rec_name = 'name'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    salesperson_id = fields.Many2one('hr.employee', string='Salesperson', domain=[('is_sales_man', '=', True)])
    # visit_time = fields.Datetime(string='Scheduled Time')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirm', 'Confirmed'), ('in_process', 'In Process'), ('complete', 'Completed'), ],
        string='State',
        default='draft'
    )

    # field_force_id = fields.Many2one('field.force', 'Field Force ID')
    # route.planing
    field_force_ids = fields.One2many('field.force', 'route_plan_id', string='Field Forces')

    # remove field_force_id = fields.Many2one(...)

    line_ids = fields.One2many('planing.lines', 'route_planing_id', string='Planning Lines')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('route.planing') or _('New')
        return super(RoutePlaning, self).create(vals)

    def action_confirm(self):
        self.update({'state': 'confirm'})

    def action_draft(self):
        self.update({'state': 'draft'})

    related_field_force_count = fields.Integer('Count of Field Force', compute='_compute_relevant_field_force',
                                               store=True)

    @api.depends('field_force_ids')
    def _compute_relevant_field_force(self):
        for x in self:
            x.related_field_force_count = len(x.field_force_ids)

    def action_view_related(self):
        return {
            'name': 'Related Field Force',
            'res_model': 'field.force',
            'view_mode': 'list,form',
            'domain': [('route_plan_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.onchange('line_ids')
    def _onchange_is_check_in_state(self):
        if any(x.is_check_in == True for x in self.line_ids):
            self.state = 'in_process'
        if all(l.is_check_in and l.is_check_out for l in self.line_ids):
            self.state = 'complete'


class PlaningLines(models.Model):
    _name = 'planing.lines'
    _description = 'Planning Lines'

    route_planing_id = fields.Many2one('route.planing', string='Route Plan', ondelete='cascade')
    visit_count = fields.Integer('Visit Count', readonly=True, store=True)
    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('is_customer', '=', True)])
    partner_location = fields.Char('Address/Location', readonly=True, store=True)
    is_check_in = fields.Boolean('Check-In', readonly=False)
    is_check_out = fields.Boolean('Check-Out', readonly=False)
    note_desc = fields.Char('Note Description')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        Update partner_location with the full address when partner_id changes in the UI.
        """
        if self.partner_id:
            address_parts = [
                self.partner_id.street or '',
                self.partner_id.street2 or '',
                self.partner_id.city or '',
                self.partner_id.state_id.name if self.partner_id.state_id else '',
                self.partner_id.zip or '',
                self.partner_id.country_id.name if self.partner_id.country_id else ''
            ]
            self.partner_location = ' '.join(filter(None, address_parts))
        else:
            self.partner_location = False

    @api.model
    def create(self, vals):
        """
        Set visit_count based on the number of existing lines for the route_planing_id.
        Also ensure partner_location is set when creating a record.
        """
        if vals.get('route_planing_id'):
            # Count existing lines for the same route_planing_id
            existing_lines = self.env['planing.lines'].search_count([
                ('route_planing_id', '=', vals['route_planing_id'])
            ])
            vals['visit_count'] = existing_lines + 1

        # Handle partner_location
        if vals.get('partner_id') and not vals.get('partner_location'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            address_parts = [
                partner.street or '',
                partner.street2 or '',
                partner.city or '',
                partner.state_id.name if partner.state_id else '',
                partner.zip or '',
                partner.country_id.name if partner.country_id else ''
            ]
            vals['partner_location'] = ' '.join(filter(None, address_parts))

        return super(PlaningLines, self).create(vals)

    def write(self, vals):
        """
        Ensure partner_location is updated when partner_id changes during write.
        """
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            address_parts = [
                partner.street or '',
                partner.street2 or '',
                partner.city or '',
                partner.state_id.name if partner.state_id else '',
                partner.zip or '',
                partner.country_id.name if partner.country_id else ''
            ]
            vals['partner_location'] = ' '.join(filter(None, address_parts))
        return super(PlaningLines, self).write(vals)
