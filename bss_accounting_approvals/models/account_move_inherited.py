# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('waiting', 'Submit for Approval'),
            ('manager_approval', 'Verified'),
            ('ceo_approval', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    def action_waiting_approval(self):
        for move in self:
            move.state = 'waiting'
            # Find users with the 'accounting_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_accounting_approvals.accounting_approval_level1')
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': move.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.move'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the document: %s') % move.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # move.accounting_approval_email_notify(move, user, approval_level=1)

    def action_manager_approval(self):
        for order in self:
            order.write({'state': 'manager_approval'})
            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'account.move'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The document has been verified by the {self.env.user.name}."))

            # Find users with the 'accounting_approval_level1' access right
            group_level2 = self.env.ref(
                'bss_accounting_approvals.accounting_approval_level2')  # Replace 'your_module' with the correct module name
            level2_users = group_level2.users

            if not level2_users:
                raise UserError(_("No users are assigned to the 'Second-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level2_users:
                self.env['mail.activity'].create({
                    'res_id': order.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('account.move'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('2nd-Approval Needed'),
                    'note': _('Please review and approve the document: %s') % order.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })
                # order.accounting_approval_email_notify(order, user, approval_level=2)

    def action_ceo_approval(self):
        for order in self:
            order.write({'state': 'ceo_approval'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', order.id),  # Link the activity to this order
                ('res_model', '=', 'account.move'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The document has been approved by the {self.env.user.name}."))

    @api.depends('date', 'auto_post')
    def _compute_hide_post_button(self):
        for record in self:
            record.hide_post_button = record.state != 'ceo_approval' \
                                      or record.auto_post != 'no' and record.date > fields.Date.context_today(record)

    def button_cancel(self):
        # Shortcut to move from posted to cancelled directly. This is useful for E-invoices that must not be changed
        # when sent to the government.
        moves_to_reset_draft = self.filtered(lambda x: x.state == 'posted')
        if moves_to_reset_draft:
            moves_to_reset_draft.button_draft()

        if any(move.state not in ['draft', 'waiting', 'manager_approval', 'ceo_approval'] for move in self):
            raise UserError(_("Only draft journal entries can be cancelled."))
        self.write({'auto_post': 'no', 'state': 'cancel'})

    def accounting_approval_email_notify(self, move, user, approval_level=1):
        # Build the URL as a clickable link
        doc_type_mapping = {
            'entry': 'Journal Entry',
            'out_invoice': 'Customer Invoice',
            'out_refund': 'Customer Credit Note',
            'in_invoice': 'Vendor Bill',
            'in_refund': 'Vendor Credit Note',
            'out_receipt': 'Sales Receipt',
            'in_receipt': 'Purchase Receipt',
        }
        doc_label = doc_type_mapping.get(move.move_type, move.name)
        str_url = f'<a href="/odoo/action-{self.env.ref('account.action_move_journal_line').id}/{move.id}">{move.name}</a>'

        # Build the email body using the user's name and the link
        body = (
            "Dear {},"
            "<br><br>"
            "Hope this mail finds you well. Please review and approve the {}: {}"
            "<br><br>"
            "Kind Regards"
            "<br>"
            "{}"
        ).format(user.name, doc_label, str_url, move.create_uid.name)

        # Get the sender email from the order creator's partner
        sender = move.create_uid.partner_id.email

        # Set the subject based on the approval level
        subject = f'Level-{approval_level} Approval Needed for {doc_label}: {move.name}'

        mail_values = {
            'model': 'account.move',
            'res_id': move.id,
            'subject': subject,
            'body_html': body,
            'email_from': sender,
            'email_to': user.email,  # assuming user.email is a string
            'reply_to': sender,
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()




# payment stay in drft
# Forces the payment to stay in draft if created from bill or invoices.
class AccountMOveLines(models.Model):
    _inherit = 'account.move.line'
    has_abnormal_deferred_dates = fields.Date()


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        # Force draft state after creation
        if res.state != 'draft':
            res.write({'state': 'draft'})
        return res

    @api.model
    def _prepare_payment_vals(self, invoices):
        # Inherit the preparation of payment values
        vals = super(AccountPayment, self)._prepare_payment_vals(invoices)
        # Force draft state in preparation
        vals['state'] = 'draft'
        return vals

    def action_post(self):
        return super(AccountPayment, self).action_post()


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        # Ensure payments are created in draft state
        payments = super(AccountPaymentRegister, self)._create_payments()
        for payment in payments:
            payment.write({'state': 'draft'})
        return payments
