from odoo import api, fields, models


class RejectionWizard(models.TransientModel):
    _name = 'rejection.wizard'
    _description = 'Rejection Wizard'

    name = fields.Text('Reason', required=True)

    def reject_po(self):
        self.ensure_one()  # Ensure single record
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise models.UserError("No active record found.")
        obj = self.env['po.request'].browse(active_id)
        if not obj:
            raise models.UserError("Purchase Order Request not found.")
        obj.reject_reason = self.name
        obj.action_reject()
