from odoo import fields, models, api, _
from odoo.cli.scaffold import template
from odoo.exceptions import ValidationError
from datetime import timedelta, time
from odoo.exceptions import UserError
from datetime import datetime
import time

class SetExpenseManager(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_manager = fields.Many2one(
        'res.users',
        string="Set Expense Manager",
        help="User responsible for approving expenses",
        config_parameter='expense_employee.expense_manager',
        store=True,  # Add this
        readonly=False  # Ensure it's editable
    )


class EmployeeExpense(models.Model):
    _name = 'expense.request'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Add mail.thread inheritance

    name = fields.Char(string="Expense Name", required=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    amount = fields.Float(string="Expense Amount")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    expense_date = fields.Date(string="Expense Date", default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'),
                              ('paid', 'Paid'), ('rejected', 'Rejected')], default='draft', string="Status")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'expense_attachment_rel', 'res_id', 'attachment_id',
        string="Receipts & Documents", help="Attach expense receipts or related documents.")
    approved_by = fields.Many2one('res.users', string="Approved by")
    approved_date = fields.Date(string="Approved Date")

    expense_manager_id = fields.Many2one(
        'res.users',
        string="Expense Manager",
        help="User responsible for approving expenses",readonly=True,
    )
    payment_id = fields.Many2one('account.payment', string="Payment ID")
    rejection_reason = fields.Text(string="Rejection Reason", tracking=True)

    def default_get(self, fields_list):
        defaults = super(EmployeeExpense, self).default_get(fields_list)

        get_default_manager = self.env['ir.config_parameter'].sudo().get_param('expense_employee.expense_manager')
        print('get_default_manager Id:', get_default_manager)
        if get_default_manager:
            defaults['expense_manager_id'] = int(get_default_manager)

        return defaults

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('expense.request.sequence') or _('New')
            print(f'Generated Reference: {vals['name']}')
        return super(EmployeeExpense, self).create(vals)

    def action_submit(self):
        template_id = self.env.ref('expense_employee.expense_request_email_to_manager_id')
        if template_id:
            self.update({'state': 'submitted'})
            template_id.send_mail(self.id, force_send=True)





        # template_id = self.env.ref('expense_employee.expense_request_email_to_manager_id').id
        #
        # ctx = {
        #     'default_model': 'expense.request',
        #     'default_res_ids': self.ids,  # Use self.ids for multiple records
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        #     'custom_action': 'bss_employee_expense.update_expense_state_and_track_email',  # New custom action
        # }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'target': 'new',
        #     'context': ctx,
        # }



    def action_reset_to_draft(self):
        self.update({'state': 'draft'})

    def button_approve(self):
        self.write({'state': 'approved', 'approved_by': self.env.user.id, 'approved_date': datetime.now()})

        template_id = self.env.ref('expense_employee.expense_request_email_to_finance_group_users_id')
        if template_id:
            template_id.send_mail(self.id, force_send=True)  # Sends email immediately

    def get_finance_group_emails(self):
        """Returns a comma-separated string of emails for users in the finance group."""
        finance_group = self.env.ref('expense_employee.finance_approval_verify')
        finance_users = finance_group.users
        finance_emails = finance_users.mapped('email')  # Get email addresses
        return finance_emails

    def create_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'Register Payment {self.id}',
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': False,  # Can specify a specific form view ID if needed
            'target': 'new',  # 'new' if you want a popup
            'context': {
                'default_expense_id': self.id,
                'default_partner_id': self.employee_id.id,  # Assigning employee as partner
                'default_amount': self.amount,  # Prefilling amount
                'default_payment_date': datetime.now().strftime('%Y-%m-%d'),  # Prefilling today's date
                'default_journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
                # Getting bank journal
            },
        }

    def action_reject(self):
        """ Manager rejects the expense and sends an email to the employee """
        self.ensure_one()

        # Get the employee email
        email_to = self.employee_id.email
        if not email_to:
            raise UserError("Employee does not have a private email set.")

        self.write({'state': 'rejected'})

        # Find the email template
        template = self.env.ref('expense_employee.expense_request_email_to_employee_id')

        # Send email
        template.send_mail(self.id, force_send=True)

        # Log message in Chatter
        self.message_post(body="Expense Rejected. Notification sent to Employee.")


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    expense_id = fields.Many2one('expense.request', string="Expense ID")

    def create(self, vals_list):
        # Ensure vals_list is treated as a list, even for single records
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        # Create the payment record(s)
        payments = super(AccountPaymentInherit, self).create(vals_list)

        # Iterate over payments and their corresponding vals
        for i, payment in enumerate(payments):
            # Check if expense_id is provided in the corresponding vals
            if i < len(vals_list) and 'expense_id' in vals_list[i] and vals_list[i]['expense_id']:
                expense = self.env['expense.request'].browse(vals_list[i]['expense_id'])
                if expense:
                    expense.write({'payment_id': payment.id, 'state': 'paid'})
            # Check if expense_id is set on the payment after creation
            elif payment.expense_id:
                expense = payment.expense_id
                if expense:
                    expense.write({'payment_id': payment.id, 'state': 'paid'})

        return payments
