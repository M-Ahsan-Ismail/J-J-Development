from odoo import api, fields, models
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)

class AutoInvoiceGenerator(models.Model):
    _name = 'auto.invoice.generator'
    _description = 'Automatic Invoice Generator'

    @api.model
    def _generate_invoices(self):
        """
        Cron job method to automatically generate invoices based on sale orders and payment terms.
        Invoices are created on or after the due dates, handling installments, and linked to sale orders.
        """
        # Get all confirmed sale orders with payment terms
        sale_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale']),  # Only process confirmed orders
        ])
        _logger.info('Called---1: Found %d sale orders', len(sale_orders))

        current_date = fields.Date.context_today(self)

        for order in sale_orders:
            if not order.payment_term_id:
                continue  # Skip if no payment term is defined

            # Get payment term lines sorted by days
            payment_terms = order.payment_term_id.line_ids.sorted(key=lambda r: r.nb_days)
            if not payment_terms:
                continue  # Skip if payment term has no lines
            _logger.info('Called---2: Processing order %s with payment term %s', order.name, order.payment_term_id.name)

            # Get existing invoices for the sale order
            existing_invoices = order.invoice_ids.filtered(lambda inv: inv.state in ['posted', 'draft',])
            invoiced_amount = sum(inv.amount_total for inv in existing_invoices if inv.state == 'posted')
            total_amount = order.amount_total
            remaining_amount = total_amount - invoiced_amount
            _logger.info('Order %s: Invoiced Amount=%s, Total Amount=%s, Remaining Amount=%s', order.name,
                         invoiced_amount, total_amount, remaining_amount)

            # Iterate through payment term lines
            for term in payment_terms:
                days_due = term.nb_days
                percentage = term.value_amount / 100.0  # Convert percentage to decimal
                amount = total_amount * percentage

                # Calculate the due date based on order_date
                due_date = order.date_order + timedelta(days=days_due) if order.date_order else current_date + timedelta(days=days_due)
                due_date_date = due_date.date()
                _logger.info('Term: Days=%s, Percentage=%s, Amount=%s, Due Date=%s', days_due, percentage, amount,
                             due_date_date)

                # Check for existing invoices matching this term by amount, due date, and payment term
                already_invoiced = any(
                    inv.amount_total == amount and
                    inv.invoice_date_due == due_date_date and
                    inv.invoice_payment_term_id == order.payment_term_id and
                    inv.state in ['posted', 'draft']
                    for inv in existing_invoices
                )
                _logger.info('Already Invoiced for term: %s', already_invoiced)

                # Create invoice if conditions are met (on or after due date)
                if current_date >= due_date_date and not already_invoiced and remaining_amount >= amount:
                    try:
                        # Prepare base invoice values
                        invoice_vals = order._prepare_invoice()
                        invoice_vals.update({
                            'invoice_date': current_date,
                            'invoice_date_due': due_date,
                            'invoice_origin': order.name,  # Set the origin to the sale order name
                            'invoice_line_ids': [],
                        })

                        # Create a single invoice line for the installment amount
                        account_id = (order.order_line[0].product_id.property_account_income_id.id or
                                      order.order_line[0].product_id.categ_id.property_account_income_categ_id.id)
                        invoice_line_vals = {
                            'name': f'Installment for {percentage * 100:.2f}%',
                            'quantity': 1,
                            'price_unit': amount,
                            'account_id': account_id,
                            'sale_line_ids': [(4, line.id) for line in order.order_line],  # Link to sale order lines
                        }
                        invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

                        # Create and post the invoice
                        invoice = self.env['account.move'].create(invoice_vals)
                        invoice.action_post()
                        _logger.info('Invoice created: %s for Sale Order %s', invoice.name, order.name)

                        # Update remaining amount
                        remaining_amount -= amount

                        # Update the sale order’s invoice_ids
                        order.write({'invoice_ids': [(4, invoice.id)]})

                    except Exception as e:
                        _logger.error('Failed to create invoice for order %s: %s', order.name, str(e))
                        continue

        return True


















#
# # ---Simply Creates The Invoice ----> duplicates if not payed
# class AutoInvoiceGenerator(models.Model):
#     _name = 'auto.invoice.generator'
#     _description = 'Automatic Invoice Generator'
#
#     @api.model
#     def _generate_invoices(self):
#         """
#         Cron job method to automatically generate invoices based on sale orders and payment terms.
#         Invoices are created on or after the due dates, handling installments, and linked to sale orders.
#         """
#         # Get all confirmed sale orders with payment terms
#         sale_orders = self.env['sale.order'].search([
#             ('state', 'in', ['sale']),  # Only process confirmed orders
#         ])
#         _logger.info('Called---1: Found %d sale orders', len(sale_orders))
#
#         current_date = fields.Date.context_today(self)
#
#         for order in sale_orders:
#             if not order.payment_term_id:
#                 continue  # Skip if no payment term is defined
#
#             # Get payment term lines sorted by days
#             payment_terms = order.payment_term_id.line_ids.sorted(key=lambda r: r.nb_days)
#             if not payment_terms:
#                 continue  # Skip if payment term has no lines
#             _logger.info('Called---2: Processing order %s with payment term %s', order.name, order.payment_term_id.name)
#
#             # Get existing invoices for the sale order
#             existing_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
#             invoiced_amount = sum(inv.amount_total for inv in existing_invoices)
#             total_amount = order.amount_total
#             remaining_amount = total_amount - invoiced_amount
#             _logger.info('Order %s: Invoiced Amount=%s, Total Amount=%s, Remaining Amount=%s', order.name,
#                          invoiced_amount, total_amount, remaining_amount)
#
#             # Iterate through payment term lines
#             for term in payment_terms:
#                 days_due = term.nb_days
#                 percentage = term.value_amount / 100.0  # Convert percentage to decimal
#                 amount = total_amount * percentage
#
#                 # Calculate the due date based on order_date
#                 due_date = order.date_order + timedelta(
#                     days=days_due) if order.date_order else current_date + timedelta(days=days_due)
#                 due_date_date = due_date.date()
#                 _logger.info('Term: Days=%s, Percentage=%s, Amount=%s, Due Date=%s', days_due, percentage, amount,
#                              due_date_date)
#
#                 # Check for existing invoices matching this term by amount and due date
#                 already_invoiced = any(
#                     inv.amount_total == amount and
#                     inv.invoice_date_due == due_date_date and
#                     inv.invoice_payment_term_id == order.payment_term_id
#                     for inv in existing_invoices
#                 )
#                 _logger.info('Already Invoiced for term: %s', already_invoiced)
#
#                 # Create invoice if conditions are met (on or after due date)
#                 if current_date >= due_date_date and not already_invoiced and remaining_amount >= amount:
#                     try:
#                         # Prepare base invoice values
#                         invoice_vals = order._prepare_invoice()
#                         invoice_vals.update({
#                             'invoice_date': current_date,
#                             'invoice_date_due': due_date,
#                             'invoice_origin': order.name,  # Set the origin to the sale order name
#                             'invoice_line_ids': [],
#                         })
#
#                         # Create a single invoice line for the installment amount
#                         account_id = (order.order_line[0].product_id.property_account_income_id.id or
#                                       order.order_line[0].product_id.categ_id.property_account_income_categ_id.id)
#                         invoice_line_vals = {
#                             'name': f'Installment for {percentage * 100:.2f}%',
#                             'quantity': 1,
#                             'price_unit': amount,
#                             'account_id': account_id,
#                             'sale_line_ids': [(4, line.id) for line in order.order_line],  # Link to sale order lines
#                         }
#                         invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
#
#                         # Create and post the invoice
#                         invoice = self.env['account.move'].create(invoice_vals)
#                         invoice.action_post()
#                         _logger.info('Invoice created: %s for Sale Order %s', invoice.name, order.name)
#
#                         # Update remaining amount
#                         remaining_amount -= amount
#
#                         # Update the sale order’s invoice_ids
#                         order.write({'invoice_ids': [(4, invoice.id)]})
#
#                     except Exception as e:
#                         _logger.error('Failed to create invoice for order %s: %s', order.name, str(e))
#                         continue
#
#         return True







