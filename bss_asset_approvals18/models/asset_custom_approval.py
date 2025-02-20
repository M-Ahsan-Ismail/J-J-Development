from odoo import fields, models, _
from odoo.exceptions import UserError


class AssetApprovals(models.Model):
    _inherit = 'account.asset'
    _description = 'Custom Approvals'

    state = fields.Selection(
        selection=[('model', 'Model'),
                   ('draft', 'Draft'),
                   ('submit_for_approval', 'Submit For Approval'),
                   ('verify', 'Verified'),
                   ('approve', 'Approved'),
                   ('open', 'Running'),
                   ('paused', 'On Hold'),
                   ('close', 'Closed'),
                   ('cancelled', 'Cancelled')],
        string='Status',
        copy=False,
        default='draft',
        readonly=True,
        help="When an asset is created, the status is 'Draft'.\n"
             "If the asset is confirmed, the status goes in 'Running' and the depreciation lines can be posted in the accounting.\n"
             "The 'On Hold' status can be set manually when you want to pause the depreciation of an asset for some time.\n"
             "You can manually close an asset when the depreciation is over.\n"
             "By cancelling an asset, all depreciation entries will be reversed")

    def submit_for_approval(self):
        for rec in self:
            rec.state = 'submit_for_approval'
            # Find users with the 'assets_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_asset_approvals18.asset_approval_verify')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.asset'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the Asset: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_first_approval(self):
        for rec in self:
            rec.write({'state': 'verify'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'account.asset'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Asset has been verified by the {self.env.user.name}."))

            # Find users with the 'asset_approval_level2' access right
            group_level2 = self.env.ref(
                'bss_asset_approvals18.asset_approval_approve')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.asset'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the Asset: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })

    def button_second_approved(self):
        for rec in self:
            rec.write({'state': 'approve'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'account.asset'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Asset has been approved by the {self.env.user.name}."))
