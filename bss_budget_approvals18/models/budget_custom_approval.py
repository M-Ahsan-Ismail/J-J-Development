from odoo import fields, models, _
from odoo.exceptions import UserError


class BudgetAnalyticalApprovals(models.Model):
    _inherit = 'budget.analytic'
    _description = 'Custom Approvals'

    state = fields.Selection(
        string="Status",
        selection=[
            ('draft', "Draft"),
            ('submit_for_approval', "Submit For Approval"),
            ('verify', "verified"),
            ('approve', "approved"),
            ('confirmed', "Open"),
            ('revised', "Revised"),
            ('done', "Done"),
            ('canceled', "Canceled")
        ],
        required=True, default='draft',
        readonly=True,
        copy=False,
        tracking=True,
    )

    def submit_for_approval(self):
        for rec in self:
            rec.state = 'submit_for_approval'

            # Find users with the 'budget_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_budget_approvals18.budget_approval_verify')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users
            print(f'group_level1: {group_level1}')
            print(f'level1_users: {level1_users}')

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('budget.analytic'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the Budget: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_first_approval(self):
        for rec in self:
            rec.write({'state': 'verify'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'budget.analytic'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Budget has been verified by the {self.env.user.name}."))

            # Find users with the 'budget_approval_level2' access right
            group_level2 = self.env.ref(
                'bss_budget_approvals18.budget_approval_approve')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('budget.analytic'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the Budget: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_second_approved(self):
        for rec in self:
            rec.write({'state': 'approve'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'budget.analytic'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Budget has been approved by the {self.env.user.name}."))
