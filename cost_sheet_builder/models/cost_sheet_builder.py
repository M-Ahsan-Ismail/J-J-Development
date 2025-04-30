from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CostSheetBuilder(models.Model):
    _name = 'cost.sheet.builder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cost Sheet Builder'

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string="Priority", default='1')

    name = fields.Char(string="Cs No", required=True, readonly=True, default='New')
    link_with_opportunity = fields.Many2one('crm.lead', string="Link with Opportunity", required=True, tracking=True,
                                            help='Create opportunity first and link it with cost sheet')
    customer_id = fields.Many2one('res.partner', string="Customer", related='link_with_opportunity.partner_id',
                                  readonly=True, store=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.user.company_id.id,
        readonly=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_approve', 'Submitted To Approve'),
        ('approve', 'Approved'),
        ('quotation', 'Quotation'),
        ('reject', 'rejected'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')

    email = fields.Char(string="Email Address", related='link_with_opportunity.email_from', readonly=True,
                        tracking=True)
    tag_ids = fields.Many2many('crm.tag', string="Tags", related='link_with_opportunity.tag_ids', readonly=True,
                               tracking=True)
    style = fields.Char(string="Style", tracking=True)
    cost_line_ids = fields.One2many('cost.sheet.lines', 'cost_sheet_id', string="Cost Lines", required=True)
    sale_order_ids = fields.Many2many('sale.order', string="Quotation/Sale Order", copy=False, )
    related_sale_orders_count = fields.Integer('Count of Sales Orders', compute='_compute_relevant_sale_orders',
                                               store=True)
    state_sale_orders = fields.Integer('Actual Sales Orders', compute='_compute_relevant_sale_orders',
                                       store=True)
    state_quotation = fields.Integer('Quotations Count', compute='_compute_relevant_sale_orders',
                                     store=True)
    total_cost = fields.Float('Total Cost', compute='_compute_quantity_and_unit_cost')
    reject_reason = fields.Text('Rejection Reason', tracking=True)
    active = fields.Boolean(default=True,
                            help="If you uncheck the active field, it will disable the record rule without deleting it (if you delete a native record rule, it may be re-created when you reload the module).")

    @api.depends('cost_line_ids.total_cost')
    def _compute_quantity_and_unit_cost(self):
        for record in self:
            record.total_cost = sum(x.total_cost for x in record.cost_line_ids if x.total_cost)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cost.sheet.builder') or '/'
        return super(CostSheetBuilder, self).create(vals)

    def unlink(self):
        for record in self:
            if any(x.state == 'sale' for x in record.sale_order_ids):
                sale_order_names = [x.name for x in record.sale_order_ids if x.state == 'sale']
                raise UserError(
                    _('You cannot unlink sale orders: %s') % ', '.join(sale_order_names))
        return super(CostSheetBuilder, self).unlink()

    def action_save(self):
        self.write({'state': 'draft'})

    def action_submit(self):
        self.write({'state': 'submit_to_approve'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_reject(self):
        self.write({'state': 'reject'})

    def convert_to_quotation(self):
        for record in self:
            if any(x for x in record.sale_order_ids):
                raise UserError('Record all ready exists.')

            else:
                if record.state == 'approve':
                    # Validate required fields
                    if not record.customer_id:
                        raise UserError(_("No customer specified for cost sheet '%s'.") % record.name)
                    if not record.cost_line_ids:
                        raise UserError(_("No cost lines found for cost sheet '%s'.") % record.name)

                    # Prepare sale order lines from cost_line_ids
                    order_lines = []
                    for line in record.cost_line_ids:
                        if not line.product_id:
                            raise UserError(_("Product missing in cost line for cost sheet '%s'.") % record.name)
                        # Optional validation for invalid lines
                        if not line.quantity or line.unit_cost <= 0:
                            continue
                        order_lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.quantity,
                            'price_unit': line.unit_cost,
                            'name': line.product_id.name,
                        }))

                    # Check if any valid lines were added
                    if not order_lines:
                        raise UserError(
                            _("No valid cost lines (with positive quantity and unit cost) found for cost sheet '%s'.") % record.name)

                    # Create sale order
                    sale_order = self.env['sale.order'].create({
                        'relevant_cost_sheet_id': record.id,
                        'partner_id': record.customer_id.id,
                        'date_order': fields.Datetime.now(),
                        'order_line': order_lines,
                    })
                    # Add sale order to Many2many field
                    record.sale_order_ids |= sale_order
                    if record.sale_order_ids:
                        record.update({'state': 'quotation'})
                    # # Show notification
                    record.message_post(
                        body=f"✅ Sale order {sale_order.name} created for cost sheet {record.name}.",
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment')
                else:
                    raise UserError('State must be approve.')

    def action_adjust_quotation(self):
        quotation_ids = self.env['sale.order'].search([
            ('state', '=', 'draft'),
            ('relevant_cost_sheet_id', '=', self.id)
        ])

        adjusted_orders = []

        if quotation_ids:
            print(f'Ids: {quotation_ids}')
            for x in quotation_ids:
                x.order_line.unlink()
                adjusted_orders.append(x.name)

                for rec in self.cost_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': x.id,
                        'product_id': rec.product_id.id,
                        'product_uom_qty': rec.quantity,
                        'price_unit': rec.unit_cost,
                        'product_template_id': rec.product_id.id,
                    })

            sale_orders = ", ".join(adjusted_orders)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f"Sale order(s) {sale_orders} adjusted successfully!",
                    'type': 'success',
                    'sticky': False,
                }
            }

    def cancel_button(self):
        for order in self.sale_order_ids:
            sale_orders = [x.name for x in self.sale_order_ids if x.state == 'sale']
            if order.state == 'sale':
                raise UserError(_("You are not allowed to cancel posted Sale order '%s'") % sale_orders)
            else:
                order.state = 'cancel'
        self.write({'state': 'cancel'})
        self.active = False

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'active': True})

    @api.depends('sale_order_ids', 'sale_order_ids.state')
    def _compute_relevant_sale_orders(self):
        for x in self:
            x.related_sale_orders_count = len(x.sale_order_ids)
            x.state_sale_orders = len([i for i in x.sale_order_ids if i.state == 'sale'])
            x.state_quotation = len([i for i in x.sale_order_ids if i.state == 'draft'])

    def action_view_related(self):
        return {
            'name': 'Related Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('relevant_cost_sheet_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_related_sale_orders(self):
        return {
            'name': 'Related Sale Orders',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('relevant_cost_sheet_id', '=', self.id), ('state', '=', 'sale')],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }


class CostSheetLines(models.Model):
    _name = 'cost.sheet.lines'
    _description = 'Cost Sheet Lines'

    cost_sheet_id = fields.Many2one('cost.sheet.builder', string="Cost Sheet", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", required=True, tracking=True)
    quantity = fields.Float(string="Quantity", required=False, tracking=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", related='product_id.uom_id', readonly=True,
                             tracking=True)
    unit_cost = fields.Float(string="Unit Cost", required=False, tracking=True)
    total_cost = fields.Float(string="Total Cost", compute='_compute_total_cost', store=True, tracking=True)

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            if line.quantity > 0 and line.unit_cost >= 0:
                line.total_cost = line.quantity * line.unit_cost
            else:
                line.total_cost = 0.0
