from odoo import models, fields, api


class ClassicalInheritanceParent(models.Model):
    _name = 'classic.parent'
    _inherits = {'stock.picking': 'stock_id'}

    stock_id = fields.Many2one('stock.picking', 'Stock ID')
    parent_age = fields.Integer('Parent Age', compute='_compute_parent_age')

    @api.depends('stock_id')
    def _compute_parent_age(self):
        for rec in self:
            # Searching for stock pickings with a specific product
            pickings = self.env['stock.picking'].search_read(
                [('move_ids_without_package.product_id.name', '=', 'Cabinet Doors ')],
                ['id', 'name']
            )
            partners = self.env['res.partner'].search([]).read(['name', 'email'])
            print(partners)

            rec.parent_age = pickings[1]['id']

# -------------------------------> Info About: Search_Read(domain,fields)  <---------------------------------------------
#
# - it is just like search(), but instead of returning recordsets (which contain only IDs unless accessed), it returns a list of dictionaries with the fields you specify.
#
# ----> When to Use search_read()?
# When you need specific fields but don’t want to iterate over search() results.
# pickings = self.env['stock.picking'].search_read(
#                 [('move_ids_without_package.product_id.name', '=', 'Cabinet Doors ')],
#                 ['id','name']
#             )
# print(pickings[1]['name']) # directly printed  an value instead of looping
# OR ---> rec.parent_age = pickings[1]['name']  # directly assigned value instead of browsing record then finding specific field value
#
#
#
#
#
# -----------------------------------> Read(fields)  <---------------------------------------------
#
# used to retrive the values from sepcific records , returns a list of dicts.first search the read.
# partners = self.env['res.partner'].search([], limit=2).read(['name', 'email'])
# print(partners)
# [
# {'id': 47, 'name': 'Abigail Peterson', 'email': 'abigail.peterson39@example.com'},
# {'id': 55, 'name': 'Anita Oliver', 'email': 'anita.oliver32@example.com'}
# ]
#
#
#
# -----------------------------------> with_context(**kwargs)  <---------------------------------------------
#Some built-in context keys (active_test, lang, tz, etc.) affect queries automatically.
# with_context() is NOT a search domain but a way to modify how Odoo processes data.
# models in Odoo have an active field.
# If active_test=True, the record is visible and usable.
# If active_test=False, the record is  archived (inactive) and is hidden from normal searches.
#
# Example:--->
# partners = self.env['res.partner'].with_context(active_test=False).search([])
# print(partners)
#
#
#
#
# -----------------------------------> with_user(user_id)  <---------------------------------------------
#
# it is used to execute an operation as a different user.
# This is useful when you need to temporarily override the current user’s permissions while executing a specific action.
# Used to execute actions as a specific user instead of the logged-in user (self.env.user).
#
# Example:--->
#
# admin_user = self.env.ref('base.user_admin')
# partners = self.env['res.partner'].with_user(admin_user).search([]) #  Search all partners as Admin
# print(f"Executed as: {admin_user.name}")
# print(f"Total partners found: {len(partners)}")
#
#
# -----------------------------------> sudo() --->	Bypasses access rights restrictions  <---------------------------------------------

