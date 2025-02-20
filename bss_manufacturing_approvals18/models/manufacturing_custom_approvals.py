from odoo import fields, models, _
from odoo.exceptions import UserError

class ManufacturingOrderApprovals(models.Model):
    _inherit = 'mrp.production'
    _description = 'Custom Approvals'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('submit_for_approval', 'Submit For Approval'),
        ('manager_approval', 'Verified'),
        ('ceo_approval', 'Approved'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")

    def submit_for_approval(self):
        for rec in self:
            rec.state = 'submit_for_approval'

            # Find users with the 'mrp_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_manufacturing_approvals18.manufacturing_approval_level1')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('mrp.production'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the Manufacturing Order: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_manager_approval(self):
        for rec in self:
            rec.write({'state': 'manager_approval'})
            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'mrp.production'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Manufacturing Order has been verified by the {self.env.user.name}."))

            # Find users with the 'mrp_approval_level1' access right
            group_level2 = self.env.ref(
                'bss_manufacturing_approvals18.manufacturing_approval_level2')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('mrp.production'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the Manufacturing Order: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_ceo_approved(self):
        for rec in self:
            rec.write({'state': 'ceo_approval'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'mrp.production'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Manufacturing Order has been approved by the {self.env.user.name}."))

    def action_start(self):
        res = super(ManufacturingOrderApprovals, self).action_start()
        for rec in self:
            rec.write({'state': 'progress'})
        return res

    reserve_visible = fields.Boolean(default=True)  # Ensure it starts as True
    unreserve_visible = fields.Boolean(default=False)  # Start as False

    def do_unreserve(self):
        res = super(ManufacturingOrderApprovals, self).do_unreserve()

        for record in self:
            record.reserve_visible = True  # Keep Check Availability visible
            record.unreserve_visible = False  # Hide Unreserve button after clicking

        return res

    def action_assign(self):
        res = super(ManufacturingOrderApprovals, self).action_assign()

        for record in self:
            record.reserve_visible = False  # Hide Check Availability after clicking
            record.unreserve_visible = True  # Show Unreserve button

        return res





#
# class WorkOrderApprovals(models.Model):
#     _inherit = 'mrp.workorder'
#
#     state = fields.Selection([
#         ('pending', 'Waiting for another WO'),
#         ('waiting', 'Waiting for components'),
#         ('submit_for_approval', 'Submit For Approval'),
#         ('manager_approval', 'Manager Approval'),
#         ('ceo_approval', 'CEO Approval'),
#         ('ready', 'Ready'),
#         ('progress', 'In Progress'),
#         ('done', 'Finished'),
#         ('cancel', 'Cancelled')], string='Status',
#         compute='_compute_state', store=True,
#         default='pending', copy=False, readonly=True, recursive=True, index=True)
#
#     def submit_for_approval(self):
#         for rec in self:
#             pass
#             rec.state = 'submit_for_approval'
#
#     def button_manager_approval(self):
#         for rec in self:
#             pass
#             rec.write({'state': 'manager_approval'})
#
#     def button_ceo_approved(self):
#         for rec in self:
#             pass
#             rec.write({'state': 'ceo_approval'})
