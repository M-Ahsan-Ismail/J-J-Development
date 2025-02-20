# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bss_mrp_access(models.Model):
#     _name = 'bss_mrp_access.bss_mrp_access'
#     _description = 'bss_mrp_access.bss_mrp_access'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

