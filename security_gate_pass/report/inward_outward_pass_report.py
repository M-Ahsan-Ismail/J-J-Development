from odoo import _, api, fields, models ,_
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError



class StockPickingInherit(models.Model):
    _inherit = 'visitor.info'

