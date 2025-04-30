from odoo import api, fields, models, _
from odoo.exceptions import UserError


class rejection_wizard(models.TransientModel):
    _name = 'cost.sheet.reject'

    name = fields.Text('Reason', required=True)

    def reject_po(self):
        self.ensure_one()  # Ensure single record
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise models.UserError("No active record found.")
        obj = self.env['cost.sheet.builder'].browse(active_id)
        if not obj:
            raise models.UserError("Cost Sheet not found.")
        obj.reject_reason = self.name
        obj.action_reject()
