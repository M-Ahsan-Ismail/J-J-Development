from odoo import fields, models, _
from odoo.exceptions import UserError

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('waiting', 'Submit for Approval'),
    ('manager_approval', 'Verified'),
    ('ceo_approval', 'Approved'),
    ('sale', "Sales Order"),
    ('cancel', "Cancelled"),
]


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    def action_waiting_approval(self):
        for move in self:
            move.state = 'waiting'

            # Find users with the 'sale_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_sale_approvals18.sale_approval_level1')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': move.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('sale.order'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the RFQ: %s') % move.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # move.sale_approval_email_notify(move, user, approval_level=1)

    def button_manager_approval(self):
        for order in self:
            order.write({'state': 'manager_approval'})
            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'sale.order'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The order has been verified by the {self.env.user.name}."))

            # Find users with the 'sale_approval_level1' access right
            group_level2 = self.env.ref(
                'bss_sale_approvals18.sale_approval_level2')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': order.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('sale.order'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the RFQ: %s') % order.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # order.sale_approval_email_notify(order, user, approval_level=2)

    def button_ceo_approved(self):
        for order in self:
            order.write({'state': 'ceo_approval'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'sale.order'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The order has been approved by the {self.env.user.name}."))

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent', 'ceo_approval'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
                not line.display_type
                and not line.is_downpayment
                and not line.product_id
                for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False


    def sale_approval_email_notify(self, order, user, approval_level=1):
        # Build the URL as a clickable link
        str_url = f'<a href="/odoo/sales/{order.id}">{order.name}</a>'

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
            'model': 'sale.order',
            'res_id': order.id,
            'subject': subject,
            'body_html': body,
            'email_from': sender,
            'email_to': user.email,  # assuming user.email is a string
            'reply_to': sender,
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
