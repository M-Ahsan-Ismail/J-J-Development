from odoo import models, fields, api

class AgingReportWizard(models.TransientModel):
    _name = 'aging.report.wizard'
    _description = 'Aging Report Wizard'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        required=True,
        help="Select the partners for the aging report."
    )
    date = fields.Date(
        string='As of Date',
        required=True,
        default=fields.Date.context_today,
        help="Date to calculate the aging as of."
    )
    report_type = fields.Selection(
        [('payable', 'Payable'),
         ('receivable', 'Receivable'),
         ('both', 'Both')],
        string='Report Type',
        required=True,
        default='both',
        help="Select the type of report to generate."
    )

    def action_print_report(self):
        """Generate the aging report based on wizard inputs."""
        data = {
            'partner_ids': self.partner_ids.ids,
            'date': self.date,
            'report_type': self.report_type,
        }
        return self.env.ref('jnj_aging_reports.action_aging_report').report_action(self, data=data)