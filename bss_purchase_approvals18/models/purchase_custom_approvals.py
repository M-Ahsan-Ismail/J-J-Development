from odoo import fields, models, _
from odoo.exceptions import UserError


class PurchaseCustomApprovals(models.Model):
    _inherit = 'purchase.order'
    _description = 'Custom Approvals'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('waiting', 'Submit for Approval'),
        ('to approve', 'To Approve'),
        ('manager_approval', 'Verified'),
        ('ceo_approval', 'Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def action_waiting_approval(self):
        for move in self:
            move.state = 'waiting'

            # Find users with the 'purchase_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_purchase_approvals18.purchase_approval_level1')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': move.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('purchase.order'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the RFQ: %s') % move.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # move.purchase_approval_email_notify(move, user, approval_level=1)


    def button_manager_approval(self):
        for order in self:
            order.write({'state': 'manager_approval'})
            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'purchase.order'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The order has been verified by the {self.env.user.name}."))

            # Find users with the 'purchase_approval_level2' access right
            group_level2 = self.env.ref(
                'bss_purchase_approvals18.purchase_approval_level2')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': order.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('purchase.order'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the RFQ: %s') % order.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # order.purchase_approval_email_notify(order, user, approval_level=2)

    def button_ceo_approved(self):
        for order in self:
            order.write({'state': 'ceo_approval'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'purchase.order'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The order has been approved by the {self.env.user.name}."))

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'ceo_approval']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def purchase_approval_email_notify(self, order, user, approval_level=1):
        # Build the URL as a clickable link
        str_url = f'<a href="/odoo/purchase/{order.id}">{order.name}</a>'

        # Build the email body using the user's name and the link
        body = (
            "Dear {},"
            "<br><br>"
            "Hope this mail finds you well. Please review and approve the RFQ: {}"
            "<br><br>"
            "Kind Regards"
            "<br>"
            "{}"
        ).format(user.name, str_url, order.create_uid.name)

        # Get the sender email from the order creator's partner
        sender = order.create_uid.partner_id.email

        # Set the subject based on the approval level
        subject = f'Level-{approval_level} Approval Needed: {order.name}'

        mail_values = {
            'model': 'purchase.order',
            'res_id': order.id,
            'subject': subject,
            'body_html': body,
            'email_from': sender,
            'email_to': user.email,  # assuming user.email is a string
            'reply_to': sender,
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
