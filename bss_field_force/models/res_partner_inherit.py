from odoo import models, fields


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean('Is Customer', default=False)



class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_sales_man = fields.Boolean('Is Sales Man', default=False)