from odoo import fields, models, _, api
from odoo.exceptions import UserError


class AccountPaymentInherited(models.Model):
    _inherit = 'account.payment'

    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('waiting', 'Submit for Approval'),
            ('manager_approval', 'Verified'),
            ('ceo_approval', 'Approved'),
            ('in_process', "In Process"),
            ('paid', "Paid"),
            ('canceled', "Canceled"),
            ('rejected', "Rejected"),
        ],
        required=True,
        default='draft',
        compute='_compute_state', store=True, readonly=False,
        copy=False,
    )

    def action_waiting_approval(self):
        for move in self:
            move.state = 'waiting'

            # Find users with the 'payment_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_payment_approvals.payment_approval_level1')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': move.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.payment'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the Payment: %s') % move.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # move.payment_approval_email_notify(move, user, approval_level=1)
    def action_manager_approval(self):
        for order in self:
            order.write({'state': 'manager_approval'})
            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'account.payment'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The payment has been verified by the {self.env.user.name}."))

            # Find users with the 'payment_approval_level1' access right
            group_level2 = self.env.ref(
                'bss_payment_approvals.payment_approval_level1')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': order.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.payment'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the Payment: %s') % order.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # order.payment_approval_email_notify(order, user, approval_level=1)
    def action_ceo_approval(self):
        for order in self:
            order.write({'state': 'ceo_approval'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'account.payment'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The payment has been approved by the {self.env.user.name}."))
    def payment_approval_email_notify(self, payment, user, approval_level=1):
        # Build the URL as a clickable link
        if payment.payment_type == 'outbound':
            str_url = f'<a href="/odoo/action-{self.env.ref('account.action_account_payments').id}/{payment.id}">{payment.name}</a>'
        else:
            str_url = f'<a href="/odoo/action-{self.env.ref('account.action_account_payments_payable').id}/{payment.id}">{payment.name}</a>'

        # Build the email body using the user's name and the link
        body = (
            "Dear {},"
            "<br><br>"
            "Hope this mail finds you well. Please review and approve the Payment: {}"
            "<br><br>"
            "Kind Regards"
            "<br>"
            "{}"
        ).format(user.name, str_url, payment.create_uid.name)

        # Get the sender email from the order creator's partner
        sender = payment.create_uid.partner_id.email

        # Set the subject based on the approval level
        subject = f'Level-{approval_level} Approval Needed for Payment: {payment.name}'

        mail_values = {
            'model': 'account.payment',
            'res_id': payment.id,
            'subject': subject,
            'body_html': body,
            'email_from': sender,
            'email_to': user.email,  # assuming user.email is a string
            'reply_to': sender,
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

class AccountMOveLine(models.Model):
    _inherit = 'account.move.line'

    has_abnormal_deferred_dates = fields.Date()