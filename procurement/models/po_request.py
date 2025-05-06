from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PoRequest(models.Model):
    _name = 'po.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Po Request Builder'

    color = fields.Integer(string='Color Index', default=7)

    active = fields.Boolean(default=True,
                            help="If you uncheck the active field, it will disable the record rule without deleting it (if you delete a native record rule, it may be re-created when you reload the module).")
    name = fields.Char('Name', readonly=True, copy=False, default=lambda self: _('New'))
    mrp_id = fields.Many2one('mrp.production', string="MRP", index=True)

    po_request_lines = fields.One2many('po.request.line', 'po_request_id', 'Line Ids')

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string="Priority", default='1')

    requester = fields.Char(
        string="Requester",
        tracking=True,
        readonly=True,
        default=lambda self: self.env.user.name)
    department = fields.Char(string='Department', compute='_compute_department')

    # vendor_id = fields.Many2one('res.partner', string="Vendor", tracking=True, )
    request_date = fields.Date('Request Date', default=fields.Date.today())
    scheduled_date = fields.Date('Scheduled Date')
    state = fields.Selection([
        ('draft', 'Draft Request'),
        ('submit_for_approval', 'Submitted for Approval'),
        ('approval', 'Approved'),
        ('reject', 'Rejected'),
        ('req_created', 'Request Created'),
        ('cancel', 'Cancel'),
    ], string='Status')
    purchase_order_ids = fields.Many2many('purchase.order', string="Po")
    related_purchase_orders_count = fields.Integer('Count Po', compute='_compute_relevant_po_orders',
                                                   store=True)
    related_rfq_count = fields.Integer('Count RFQ', compute='_compute_relevant_po_orders',
                                       store=True)

    reject_reason = fields.Text('Rejection Reason', tracking=True)
    total = fields.Float('Total Request Quantity', compute='_compute_total',
                         store=True)

    @api.depends('request_date')
    def _compute_department(self):
        for rec in self:
            if rec.requester:
                rec.department = self.env['hr.employee'].search([('name', '=', rec.requester)]).department_id.name

    @api.depends('purchase_order_ids', 'purchase_order_ids.state')
    def _compute_relevant_po_orders(self):
        for x in self:
            res = len([po for po in x.purchase_order_ids if po.state == 'purchase'])
            x.related_purchase_orders_count = res
            x.related_rfq_count = len([po for po in x.purchase_order_ids if po.state == 'draft'])

    def action_view_related(self):
        return {
            'name': 'Related RFQs',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('po_request_id', '=', self.id), ('state', '=', 'draft')],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_related_purchase_order(self):
        return {
            'name': 'Related Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'domain': [('po_request_id', '=', self.id), ('state', '=', 'purchase')],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_save(self):
        self.write({'state': 'draft'})

    def cancel_button(self):
        self.write({'state': 'cancel', 'active': False})

    def submit_to_approve(self):
        self.write({'state': 'submit_for_approval'})

    def action_approve(self):
        self.write({'state': 'approval'})

    def action_reject(self):
        self.write({'state': 'reject'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'active': True})

    def create_rfq(self):
        self.ensure_one()
        if not self.po_request_lines:
            raise UserError(_("No purchase order lines to create RFQ."))

        for line in self.po_request_lines:
            if not line.vendor_ids:
                raise UserError(_("Vendor is required to create RFQ."))
            if line.request_quantity <= 0:
                raise UserError(_("Quantity is required to create RFQ."))

        # Group lines by vendors
        vendor_lines = {}
        for rec in self.po_request_lines:
            for vendor in rec.vendor_ids:
                if vendor.id not in vendor_lines:
                    vendor_lines[vendor.id] = []
                vendor_lines[vendor.id].append(rec)

        # Create purchase orders for each vendor
        purchase_orders = []
        for vendor_id, lines in vendor_lines.items():
            order_lines = [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.request_quantity,
                    # 'price_unit': line.estimated_cost,
                    'name': line.product_id.name,
                    'discount': line.discount or 0.0,
                })
                for line in lines
            ]

            purchase_order = self.env['purchase.order'].create({
                'partner_id': vendor_id,
                'po_request_id': self.id,
                'order_line': order_lines,
            })
            purchase_orders.append((4, purchase_order.id))

            # Post message for each purchase order created
            self.message_post(
                body=f"Purchase order {purchase_order.name} created for PO {self.name} with vendor {purchase_order.partner_id.name}",
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

        # Update state and link purchase orders
        self.write({
            'state': 'req_created',
            'purchase_order_ids': purchase_orders
        })

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('next.gen.po.request.sequence') or _('New')
            print(f"Generated Reference No: {vals['name']}")
        return super(PoRequest, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state == 'req_created':
                raise UserError(
                    _(f'You cannot unlink confirmed request {record.name}'))
        return super(PoRequest, self).unlink()

    @api.depends('po_request_lines.request_quantity')
    def _compute_total(self):
        for record in self:
            record.total = sum(line.request_quantity for line in record.po_request_lines)


class PoRequestLines(models.Model):
    _name = 'po.request.line'
    _description = 'Po Request Lines'

    color = fields.Integer(string='Color Index', default=4)

    po_request_id = fields.Many2one('po.request', string="Po ID")
    vendor_ids = fields.Many2many('res.partner', string="Vendor", tracking=True)

    product_id = fields.Many2one(
        'product.product', 'Product', tracking=True, )
    request_quantity = fields.Float('Demand')
    estimated_cost = fields.Float('Estimated Cost')
    unit_of_measure = fields.Char('UOM', related='product_id.uom_id.name')
    discount = fields.Float('Discount')
