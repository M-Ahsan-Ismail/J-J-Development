from odoo import fields, models, api
import datetime


class RejectionWizard(models.TransientModel):
    _name = 'rejection.wizard'

    rejection_reason = fields.Text(string="Rejection Reason")

    def reject(self):
        active_obj = self.env['expense.request'].browse(self._context.get('active_id'))
        action = active_obj.action_reject()
        active_obj.write({'rejection_reason': self.rejection_reason})
        return action

