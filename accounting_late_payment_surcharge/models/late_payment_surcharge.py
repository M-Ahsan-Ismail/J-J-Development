from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
from odoo.exceptions import UserError


class LatePaymentSurcharge(models.Model):
    _inherit = 'account.payment.term'

    late_payment_surcharge = fields.Boolean(string="Late Payment Surcharge")
    Daily_Surcharge_percentage = fields.Float(string="Daily Surcharge Percentage",
                                              help="Percentage charged daily for late payments (e.g., 0.066 for 0.066%).")


class AccountingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    late_payment_surcharge_account = fields.Many2one(
        'account.account',
        string="Default Late Payment Surcharge Account",
        config_parameter='tt_accounting_surcharge.late_payment_surcharge_account',
        help="This account will be used as default for late payments."
    )


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    late_payment_surcharge = fields.Monetary(
        string="Late Payment Surcharge",
        readonly=True,
        help="Surcharge amount for late payment."
    )


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    late_payment_surcharge = fields.Monetary(
        string="Late Payment Surcharge",
        compute='_compute_late_payment_surcharge',
        store=False,
        help="Surcharge amount for late payment."
    )

    @api.depends('can_edit_wizard', 'source_amount', 'source_amount_currency', 'source_currency_id', 'company_id',
                 'currency_id', 'payment_date', 'installments_mode')
    def _compute_amount(self):
        for wizard in self:
            if not wizard.journal_id or not wizard.currency_id or not wizard.payment_date or wizard.custom_user_amount:
                wizard.amount = wizard.amount
            else:
                total_amount_values = wizard._get_total_amounts_to_pay(wizard.batches)
                wizard.amount = total_amount_values['amount_by_default'] + wizard.late_payment_surcharge

    @api.depends('early_payment_discount_mode')
    def _compute_payment_difference_handling(self):
        for wizard in self:
            if wizard.can_edit_wizard:
                wizard.payment_difference_handling = 'reconcile' if wizard.early_payment_discount_mode or wizard.late_payment_surcharge else 'open'
            else:
                wizard.payment_difference_handling = False

    @api.depends('early_payment_discount_mode', 'can_edit_wizard', 'can_group_payments', 'group_payment',
                 'payment_method_line_id')
    def _compute_show_payment_difference(self):
        for wizard in self:
            wizard.show_payment_difference = (
                    wizard.payment_difference != 0.0
                    and not wizard.early_payment_discount_mode
                    and wizard.can_edit_wizard
                    and (not wizard.can_group_payments or wizard.group_payment)
                    and wizard.payment_method_line_id.payment_account_id
                    and not wizard.late_payment_surcharge != 0.0
            )

    @api.depends('payment_date', 'line_ids')
    def _compute_late_payment_surcharge(self):
        """Compute the late payment surcharge based on due date and payment date."""
        for wizard in self:
            surcharge = 0.0
            if wizard.line_ids and wizard.payment_date:
                for line in wizard.line_ids:
                    invoice = line.move_id
                    if invoice.move_type == 'out_invoice':  # Ensure it’s a customer invoice
                        payment_term = invoice.invoice_payment_term_id
                        if payment_term.late_payment_surcharge and payment_term.Daily_Surcharge_percentage:
                            due_date = invoice.invoice_date_due
                            if due_date and wizard.payment_date > due_date:
                                # Calculate days late
                                days_late = (wizard.payment_date - due_date).days
                                # Calculate surcharge: (Installment Amount * Daily Surcharge % * Days Late)
                                installment_amount = invoice.amount_residual
                                daily_surcharge_rate = payment_term.Daily_Surcharge_percentage / 100  # Convert to decimal
                                surcharge += installment_amount * daily_surcharge_rate * days_late
            wizard.late_payment_surcharge = surcharge
            if wizard.late_payment_surcharge:
                # Get the default late payment surcharge account from settings
                config_params = self.env['ir.config_parameter'].sudo()
                surcharge_account_id = int(
                    config_params.get_param('tt_accounting_surcharge.late_payment_surcharge_account'))
                wizard.writeoff_account_id = surcharge_account_id
                wizard.writeoff_label = 'Late Payment Surcharge'

#     def _create_payment_vals_from_wizard(self, batch_result=None):
#         """Override to include surcharge in the payment amount and create surcharge journal entry."""
#         payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
#
#         for wizard in self:
#             if wizard.late_payment_surcharge > 0:
#                 # Adjust the payment amount to include the surcharge
#                 payment_vals['amount'] = payment_vals.get('amount', 0.0) + wizard.late_payment_surcharge
#                 wizard.amount = payment_vals['amount']  # Sync with the wizard field
#
#                 # Get the default late payment surcharge account from settings
#                 config_params = self.env['ir.config_parameter'].sudo()
#                 surcharge_account_id = config_params.get_param('tt_accounting_surcharge.late_payment_surcharge_account')
#                 surcharge_account = self.env['account.account'].browse(
#                     int(surcharge_account_id)) if surcharge_account_id else False
#
#                 if not surcharge_account:
#                     raise ValidationError(
#                         "Please configure the Default Late Payment Surcharge Account in Accounting Settings.")
#
#                 # Get the receivable account (default from the journal or invoice)
#                 journal = self.env['account.journal'].browse(payment_vals['journal_id'])
#                 receivable_account = journal.default_account_id or wizard.line_ids[0].move_id.account_id
#
#                 # Create journal entry for the surcharge
#                 move = self.env['account.move'].create({
#                     'journal_id': payment_vals['journal_id'],
#                     'date': wizard.payment_date,
#                     'ref': f"Late Payment Surcharge for {wizard.line_ids[0].move_id.name}",
#                     'line_ids': [
#                         (0, 0, {
#                             'account_id': surcharge_account.id,
#                             'debit': wizard.late_payment_surcharge,
#                             'credit': 0.0,
#                             'name': 'Late Payment Surcharge',
#                         }),
#                         (0, 0, {
#                             'account_id': receivable_account.id,
#                             'debit': 0.0,
#                             'credit': wizard.late_payment_surcharge,
#                             'name': 'Late Payment Surcharge',
#                         }),
#                     ],
#                 })
#                 move.action_post()
#                 wizard._invalidate_cache()  # Ensure UI refreshes
#         return payment_vals
#
#     def action_create_payments(self):
#         """Override to ensure the payment reflects the surcharge."""
#         payments = super(AccountPaymentRegister, self).action_create_payments()
#
#         if not payments:
#             return payments  # No payments were created, exit early
#
#         if isinstance(payments, bool):  # Avoid processing if payments is False
#             return payments
#
#             # Ensure payments is a recordset
#         payment = payments if isinstance(payments, models.Model) else self.env['account.payment'].browse(payments)
#
#         if payment:
#             payment.write({'late_payment_surcharge': self.late_payment_surcharge})
#
#         return payments
#
# # ----------------------------> BackUp Current Spot:   :-----------------------------------------------------------------
#
#
# # class AccountPaymentRegister(models.TransientModel):
# #     _inherit = 'account.payment.register'
# #
# #     late_payment_surcharge = fields.Monetary(
# #         string="Late Payment Surcharge",
# #         compute='_compute_late_payment_surcharge',
# #         store=False,
# #         help="Surcharge amount for late payment."
# #     )
# #
# #     @api.depends('payment_date', 'line_ids')
# #     def _compute_late_payment_surcharge(self):
# #         """Compute the late payment surcharge based on due date and payment date."""
# #         for wizard in self:
# #             surcharge = 0.0
# #             if wizard.line_ids and wizard.payment_date:
# #                 for line in wizard.line_ids:
# #                     invoice = line.move_id
# #                     if invoice.move_type == 'out_invoice':  # Ensure it’s a customer invoice
# #                         payment_term = invoice.invoice_payment_term_id
# #                         if payment_term.late_payment_surcharge and payment_term.Daily_Surcharge_percentage:
# #                             due_date = invoice.invoice_date_due
# #                             if due_date and wizard.payment_date > due_date:
# #                                 # Calculate days late
# #                                 days_late = (wizard.payment_date - due_date).days
# #                                 # Calculate surcharge: (Installment Amount * Daily Surcharge % * Days Late)
# #                                 installment_amount = invoice.amount_residual
# #                                 daily_surcharge_rate = payment_term.Daily_Surcharge_percentage / 100  # Convert to decimal
# #                                 surcharge += installment_amount * daily_surcharge_rate * days_late
# #             wizard.late_payment_surcharge = surcharge
# #
# #
# #     # Helooo Mr.Rizwan  -----> Issue here: here we r creating an separate jv .....
# #
# #     def _create_payment_vals_from_wizard(self, batch_result=None):
# #         """Override to include surcharge in the payment amount and create surcharge journal entry."""
# #         payment_vals = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
# #
# #         for wizard in self:
# #             if wizard.late_payment_surcharge > 0:
# #                 # Adjust the payment amount to include the surcharge
# #                 payment_vals['amount'] = payment_vals.get('amount', 0.0) + wizard.late_payment_surcharge
# #                 wizard.amount = payment_vals['amount']  # Sync with the wizard field
# #
# #                 # Get the default late payment surcharge account from settings
# #                 config_params = self.env['ir.config_parameter'].sudo()
# #                 surcharge_account_id = config_params.get_param('tt_accounting_surcharge.late_payment_surcharge_account')
# #                 surcharge_account = self.env['account.account'].browse(
# #                     int(surcharge_account_id)) if surcharge_account_id else False
# #
# #                 if not surcharge_account:
# #                     raise ValidationError(
# #                         "Please configure the Default Late Payment Surcharge Account in Accounting Settings.")
# #
# #                 # Get the receivable account (default from the journal or invoice)
# #                 journal = self.env['account.journal'].browse(payment_vals['journal_id'])
# #                 receivable_account = journal.default_account_id or wizard.line_ids[0].move_id.account_id
# #
# #                 # Create journal entry for the surcharge
# #                 move = self.env['account.move'].create({
# #                     'journal_id': payment_vals['journal_id'],
# #                     'date': wizard.payment_date,
# #                     'ref': f"Late Payment Surcharge for {wizard.line_ids[0].move_id.name}",
# #                     'line_ids': [
# #                         (0, 0, {
# #                             'account_id': surcharge_account.id,
# #                             'debit': wizard.late_payment_surcharge,
# #                             'credit': 0.0,
# #                             'name': 'Late Payment Surcharge',
# #                         }),
# #                         (0, 0, {
# #                             'account_id': receivable_account.id,
# #                             'debit': 0.0,
# #                             'credit': wizard.late_payment_surcharge,
# #                             'name': 'Late Payment Surcharge',
# #                         }),
# #                     ],
# #                 })
# #                 move.action_post()
# #                 wizard._invalidate_cache()  # Ensure UI refreshes
# #
# #         return payment_vals
# #
# #     def action_create_payments(self):
# #         """Override to ensure the payment reflects the surcharge."""
# #         payments = super(AccountPaymentRegister, self).action_create_payments()
# #
# #         if not payments:
# #             return payments  # No payments were created, exit early
# #
# #         if isinstance(payments, bool):  # Avoid processing if payments is False
# #             return payments
# #
# #             # Ensure payments is a recordset
# #         payment = payments if isinstance(payments, models.Model) else self.env['account.payment'].browse(payments)
# #
# #         if payment:
# #             payment.write({'late_payment_surcharge': self.late_payment_surcharge})
# #
# #         return payments
