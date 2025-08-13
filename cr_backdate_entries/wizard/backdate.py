# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from datetime import date, datetime
import logging
import re

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def _set_scheduled_date(self):
        for picking in self:
            picking.move_line_ids.write({'date': picking.scheduled_date})


class BackDateWiz(models.TransientModel):
    _name = 'backdate.entries.wiz'
    _description = "Backdate Wizard"

    date = fields.Datetime('Date', default=fields.Datetime.now)
    picking_ids = fields.Many2many('stock.picking')

    def change_to_backdate(self):
        active_model = self._context.get('active_model')
        picking_ids = invoice_ids = False

        if active_model == 'sale.order':
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids'))
            picking_ids = sale_orders.mapped('picking_ids')
            invoice_ids = sale_orders.mapped('invoice_ids')
            # Update Sale Order Date
            for order in sale_orders:
                order.date_order = self.date
            # Update Picking Dates
            for picking in picking_ids:
                move_ids = picking.move_ids_without_package
                accmove_ids = self.env['account.move'].search([('stock_move_id', 'in', move_ids.ids)])
                # Update account.move (Invoices/Journal Entries)
                for acc_move in accmove_ids:
                    acc_move.button_draft()
                    acc_move.name = False
                    acc_move.date = self.date
                    acc_move.invoice_date = self.date
                    acc_move.action_post()
                # Update Stock Moves
                move_ids.write({'date': self.date})
                # Update Stock Valuation Layer
                self.env.cr.execute("""
                                    UPDATE stock_valuation_layer
                                    SET create_date = %s
                                    WHERE stock_move_id IN %s
                                    """, (self.date, tuple(move_ids.ids)))
                # Update Stock Move Lines
                move_line_ids = self.env['stock.move.line'].search([('move_id', 'in', move_ids.ids)])
                move_line_ids.write({'date': self.date})
                # Update Picking Record
                picking.write({
                    'scheduled_date': self.date,
                    'date_deadline': self.date,
                    'date_done': self.date,
                })
            # Update Invoice Dates
            for invoice in invoice_ids:
                invoice.button_draft()
                invoice.name = False
                invoice.invoice_date = self.date
                invoice.date = self.date
                invoice.action_post()

        elif active_model == 'purchase.order':
            purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids'))
            picking_ids = purchase_orders.mapped('picking_ids')
            invoice_ids = purchase_orders.mapped('invoice_ids')
            # Update Purchase Order Dates
            for order in purchase_orders:
                order.date_approve = self.date
                order.date_order = self.date

            # Update Picking Records
            for picking in picking_ids:
                move_ids = picking.move_ids_without_package
                accmove_ids = self.env['account.move'].search([('stock_move_id', 'in', move_ids.ids)])

                # Update Accounting Moves (Journal Entries from Stock Moves
                for acc_move in accmove_ids:
                    acc_move.button_draft()
                    acc_move.name = False
                    acc_move.invoice_date = self.date
                    acc_move.date = self.date
                    acc_move.action_post()

                # Update Stock Moves
                move_ids.write({'date': self.date})

                # Update Stock Valuation Layer
                self.env.cr.execute("""

                                    UPDATE stock_valuation_layer

                                    SET create_date = %s

                                    WHERE stock_move_id IN %s

                                    """, (self.date, tuple(move_ids.ids)))

                # Update Stock Move Lines
                move_line_ids = self.env['stock.move.line'].search([('move_id', 'in', move_ids.ids)])
                move_line_ids.write({'date': self.date})

                # Update Picking Record
                picking.write({
                    'scheduled_date': self.date,
                    'date_deadline': self.date,
                    'date_done': self.date,

                })

            # Update Invoices Related to Purchase Orders
            for invoice in invoice_ids:
                invoice.button_draft()
                invoice.name = False
                invoice.invoice_date = self.date
                invoice.date = self.date
                invoice.action_post()


        elif active_model == 'stock.picking':
            picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))
            for picking in picking_ids:
                move_ids = picking.move_ids_without_package
                accmove_ids = self.env['account.move'].search([('stock_move_id', 'in', move_ids.ids)])
                # Updating related invoices/journal entries
                for acc_move in accmove_ids:
                    # acc_move.button_draft()
                    # acc_move.name = False
                    acc_move.invoice_date = self.date
                    acc_move.date = self.date
                    # acc_move.action_post()

                # Update stock move dates
                move_ids.write({'date': self.date})

                # Update stock valuation layers
                self.env.cr.execute("""
                                    UPDATE stock_valuation_layer
                                    SET create_date = %s
                                    WHERE stock_move_id IN %s
                                    """, (self.date, tuple(move_ids.ids)))

                # Update stock move line dates
                move_line_ids = self.env['stock.move.line'].search([('move_id', 'in', move_ids.ids)])
                move_line_ids.write({'date': self.date})

                # Update picking dates
                picking.write({
                    'scheduled_date': self.date,
                    'date_deadline': self.date,
                    'date_done': self.date,
                })

        elif active_model == 'account.move':
            moves = self.env['account.move'].browse(self._context.get('active_ids'))
            for move in moves:
                move.sudo().write({
                    'invoice_date': self.date,
                    'date': self.date,
                    'invoice_date_due': self.date,
                })


        elif active_model == 'mrp.production':
            mrp_prods = self.env['mrp.production'].browse(self._context.get('active_ids'))

            for mrp in mrp_prods:
                # Get all relevant stock moves (raw and finished) for the MO
                move_ids = mrp.move_raw_ids | mrp.move_finished_ids

                # Update stock move dates
                move_ids.sudo().write({'date': self.date})

                # Update stock move line dates
                move_line_ids = self.env['stock.move.line'].search(
                    ['|', ('move_id', 'in', move_ids.ids), ('reference', '=', mrp.name)]
                )
                move_line_ids.sudo().write({'date': self.date})

                # Search and update stock valuation layers
                valuation_layers = self.env['stock.valuation.layer'].search([('stock_move_id', 'in', move_ids.ids)])
                if valuation_layers:
                    self._cr.execute("""
                                     UPDATE stock_valuation_layer
                                     SET create_date = %s
                                     WHERE stock_move_id IN %s
                                     """, (self.date, tuple(move_ids.ids)))
                    valuation_layers._invalidate_cache(['create_date'])

                else:
                    pass  # No action if no valuation layers found, but you can add custom logic if needed

                # Update picking dates in MRP
                self._cr.execute("""
                                 UPDATE mrp_production
                                 SET date_start    = %s,
                                     date_finished = %s,
                                     create_date   = %s
                                 WHERE id = %s
                                 """, (self.date, self.date, self.date, mrp.id))

            self._cr.commit()  # Commit changes

    def change_to_backdate_wizard(self):
        active_ids = self.env.context.get('active_ids')
        print('active_ids', active_ids)
        active_record = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
        return {
            'name': 'Backdate Transfer',
            'res_model': 'backdate.entries.wiz',
            'view_mode': 'form',
            'view_id': self.env.ref('cr_backdate_entries.backdate_wizard_view_form').id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }
    #
    # def change_to_backdate(self):
    #     active_model = self._context.get('active_model')
    #     picking_ids = False
    #     invoice_ids = False
    #     if active_model == 'sale.order':
    #         sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
    #         picking_list = [sale_id.picking_ids for sale_id in sale_order_ids]
    #         picking_ids = self.env['stock.picking'].browse(picking_list)
    #         invoice_list = [sale_id.invoice_ids for sale_id in sale_order_ids]
    #         invoice_ids = self.env['account.move'].browse(invoice_list)
    #         for rec in sale_order_ids:
    #             rec.date_order = self.date
    #
    #     elif active_model == 'purchase.order':
    #         purchase_order_ids = self.env['purchase.order'].browse(self._context.get('active_ids'))
    #         picking_list = [purchase_id.picking_ids for purchase_id in purchase_order_ids]
    #         picking_ids = self.env['stock.picking'].browse(picking_list)
    #         invoice_list = [purchase_id.invoice_ids for purchase_id in purchase_order_ids]
    #         invoice_ids = self.env['account.move'].browse(invoice_list)
    #         for rec in purchase_order_ids:
    #             rec.date_approve = self.date
    #             rec.date_order = self.date
    #
    #     elif active_model == 'stock.picking':
    #         picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids'))
    #         for picking in picking_ids:
    #             moveObj = self.env['stock.move'].search([('picking_id', '=', picking.id)])
    #             accmoveObj = self.env['account.move'].search([('stock_move_id', 'in', moveObj.ids)])
    #             for acc_mv in accmoveObj if not invoice_ids else invoice_ids.ids:
    #                 acc_mv.button_draft()
    #                 acc_mv.name = False
    #                 acc_mv.date = self.date
    #                 acc_mv.invoice_date = self.date
    #                 acc_mv.action_post()
    #
    #             for move in moveObj:
    #                 move.update({
    #                     'date': self.date,
    #                 })
    #                 valuationObj = self.env['stock.valuation.layer'].search([('stock_move_id', '=', move.id)])
    #                 for val in valuationObj:
    #                     self.env.cr.execute('update stock_valuation_layer set create_date=%s where id=%s',
    #                                         (self.date, val.id))
    #                 movelineObj = self.env['stock.move.line'].search([('move_id', '=', move.id)])
    #                 for move_line in movelineObj:
    #                     move_line.update({
    #                         'date': self.date,
    #                     })
    #             picking.update({
    #                 'scheduled_date': self.date,
    #                 'date_deadline': self.date,
    #             })
    #             picking.write({
    #                 'date_done': self.date,
    #             })


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def write(self, vals):
        # Remove the restriction on moving a manufacturing order in 'done' or 'cancel' state
        if 'date_start' in vals and not self.env.context.get('force_date', False):
            if self.is_planned:
                self.button_unplan()

        res = super(MrpProduction, self).write(vals)

        for production in self:
            if vals.get('date_start'):
                production.move_raw_ids.write({'date': production.date_start, 'date_deadline': production.date_start})
            if vals.get('date_finished'):
                production.move_finished_ids.write({'date': production.date_finished})
            if any(field in ['move_raw_ids', 'move_finished_ids', 'workorder_ids'] for field in
                   vals) and production.state != 'draft':
                production.with_context(no_procurement=True)._autoconfirm_production()
                if production.is_planned:
                    production._plan_workorders()
            if production.state == 'done' and ('lot_producing_id' in vals or 'qty_producing' in vals):
                finished_move = production.move_finished_ids.filtered(
                    lambda move: move.product_id == production.product_id and move.state == 'done')
                finished_move_lines = finished_move.move_line_ids
                if 'lot_producing_id' in vals:
                    finished_move_lines.write({'lot_id': vals.get('lot_producing_id')})
                if 'qty_producing' in vals:
                    finished_move.quantity = vals.get('qty_producing')
                    if production.product_tracking == 'lot':
                        finished_move.move_line_ids.lot_id = production.lot_producing_id
            if self._has_workorders() and not production.workorder_ids.operation_id and vals.get(
                    'date_start') and not vals.get('date_finished'):
                new_date_start = fields.Datetime.to_datetime(vals.get('date_start'))
                if not production.date_finished or new_date_start >= production.date_finished:
                    production.date_finished = new_date_start + datetime.timedelta(hours=1)

        return res



class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        # Set context to skip readonly check for date and invoice_date
        context = dict(self._context, skip_readonly_check=True)

        # Handle fiscal lock date check for posted moves
        if 'date' in vals and any(move.state == 'posted' for move in self):
            # Skip fiscal lock date check for date changes
            context = dict(context, skip_fiscal_lock_check=True)

        # Filter out date and invoice_date from name/date validation
        for move in self:
            if move.state == 'posted' and (
                    ('name' in vals and move.name != vals['name'])
                    # Exclude date from this validation
            ):
                move._check_fiscal_lock_dates()
                move.line_ids._check_tax_lock_date()

        # Define unmodifiable fields, excluding date and invoice_date
        unmodifiable_fields = (
            'invoice_line_ids', 'line_ids', 'partner_id',
            'invoice_payment_term_id', 'currency_id', 'fiscal_position_id',
            'invoice_cash_rounding_id'
        )
        for move in self:
            move_state = vals.get('state', move.state)
            readonly_fields = [val for val in vals if val in unmodifiable_fields]
            if move_state == "posted" and readonly_fields:
                raise UserError(_("You cannot modify the following readonly fields on a posted move: %s",
                                  ', '.join(readonly_fields)))

        # Call super with modified context
        return super(AccountMove, self.with_context(context)).write(vals)

    @api.constrains(lambda self: (self._sequence_field, self._sequence_date_field))
    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            if not record._must_check_constrains_date_sequence():
                continue
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if (
                    sequence
                    and date
                    and date > constraint_date
                    and not record._sequence_matches_date()
            ):
                pass