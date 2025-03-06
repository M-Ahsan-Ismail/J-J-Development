# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
import logging

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

        active_ids = self._context.get('active_ids', [])

        if not active_ids or not active_model:
            return

        if active_model == 'stock.valuation.layer':
            print('Called-----------')

            # Get the stock valuation layers' IDs
            valuation_layer_ids = active_ids

            # Use SQL to update create_date for stock.valuation.layer
            if valuation_layer_ids:
                self._cr.execute("""
                                   UPDATE stock_valuation_layer
                                   SET create_date = %s
                                   WHERE id IN %s
                               """, (self.date, tuple(valuation_layer_ids)))
                self._cr.commit()  # Commit the changes immediately

                # Invalidate cache to reflect changes in Odoo UI
                self.env['stock.valuation.layer'].browse(valuation_layer_ids)._invalidate_cache(['create_date'])

            # Get and update account.move IDs from stock.valuation.layer.account_move_id using SQL
            self._cr.execute("""
                               SELECT account_move_id 
                               FROM stock_valuation_layer 
                               WHERE id IN %s AND account_move_id IS NOT NULL
                           """, (tuple(valuation_layer_ids),))

            account_move_ids = [row[0] for row in self._cr.fetchall() if row[0]]

            # Use SQL to update date for related account.move (journal entries)
            if account_move_ids:
                self._cr.execute("""
                                   UPDATE account_move 
                                   SET date = %s, name = NULL 
                                   WHERE id IN %s
                               """, (self.date, tuple(account_move_ids)))
                self._cr.commit()  # Commit the changes

                # Update the state and repost the journal entries using ORM (required for state changes)
                account_moves = self.env['account.move'].browse(account_move_ids)
                for account_move in account_moves:
                    if account_move.state != 'draft':
                        account_move.button_draft()
                    account_move.action_post()

                # Invalidate cache for account.move to reflect changes
                account_moves._invalidate_cache(['date', 'name'])





        elif active_model == 'sale.order':
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
                    acc_move.button_draft()
                    acc_move.name = False
                    acc_move.invoice_date = self.date
                    acc_move.date = self.date
                    acc_move.action_post()

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
                    SET date_start = %s, date_finished = %s, create_date = %s
                    WHERE id = %s
                """, (self.date, self.date, self.date, mrp.id))

            self._cr.commit()  # Commit changes

        # - Old Code

        # elif active_model == 'mrp.production':
        #     mrp_prod = self.env['mrp.production'].browse(self._context.get('active_ids'))
        #     for mrp in mrp_prod:
        #         move_ids = mrp.move_raw_ids
        #         # Update stock move dates
        #         move_ids.sudo().write({'date': self.date})
        #         # # Update stock valuation layers
        #         # self.env.cr.execute("""
        #         #                     UPDATE stock_valuation_layer
        #         #                     SET create_date = %s
        #         #                     WHERE stock_move_id IN %s
        #         #                 """, (self.date, tuple(move_ids.ids)))
        #         # Update stock move line dates
        #         move_line_ids = self.env['stock.move.line'].search(
        #             ['|', ('move_id', 'in', move_ids.ids), ('reference', '=', mrp.name)])
        #         move_line_ids.sudo().write({'date': self.date})
        #         # Update picking dates
        #         mrp.sudo().write({
        #             'date_start': self.date,
        #             'date_finished': self.date,
        #             'create_date': self.date,
        #         })

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
