# -*- coding: utf-8 -*-


from odoo import models, fields, api
from datetime import datetime, timedelta


class PublisherWarrantyContract(models.AbstractModel):
    _inherit = "publisher_warranty.contract"

    def update_notification(self, cron_mode=True):
        # Update expiration date
        expiration_date = (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d %H:%M:%S')
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('database.expiration_date', expiration_date)
        set_param('database.expiration_reason', 'renewal')
        return True
