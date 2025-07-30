from odoo import models, fields, api


class AgingReport(models.AbstractModel):
    _name = 'report.jnj_aging_reports.aging_report_doc'
    _description = 'Aging Report'

    def _get_report_data(self, data):
        domain = [
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
        ]
        if data.get('partner_ids'):
            domain.append(('partner_id', 'in', data['partner_ids']))
        if data.get('date'):
            domain.append(('invoice_date', '<=', data['date']))
        if data.get('report_type') == 'payable':
            domain.append(('move_type', '=', 'in_invoice'))
        if data.get('report_type') == 'receivable':
            domain.append(('move_type', '=', 'out_invoice'))
        if data.get('report_type') == 'both':  # both
            domain.append(('move_type', 'in', ['in_invoice', 'out_invoice']))

        invoices = self.env['account.move'].search(domain)
        report_data = []
        as_of_date = fields.Date.from_string(data.get('date', fields.Date.today()))

        for invoice in invoices:
            aging_days = (as_of_date - invoice.invoice_date).days if invoice.invoice_date else 0
            report_data.append({
                'type': 'Bill' if invoice.move_type == 'in_invoice' else 'Invoice',
                'date': invoice.invoice_date,
                'num': invoice.name,
                'memo': invoice.narration,
                'aging': aging_days,
                'open_balance': invoice.amount_residual,
                'partner': invoice.partner_id.name,
            })

        # Group by partner
        grouped_data = {}
        for record in report_data:
            if record['partner'] not in grouped_data:
                grouped_data[record['partner']] = []
            grouped_data[record['partner']].append(record)

        return grouped_data

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'data': self._get_report_data(data or {}),
            'date_as_of': fields.Date.from_string(data.get('date', fields.Date.today())),
            'report_type': data.get('report_type'),
        }