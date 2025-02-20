from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    @api.constrains('name', 'currency_id', 'company_id')
    def _constraint_currency_rate_unique_name_per_day(self):
        if not self:
            return

        names = self.mapped('name')
        constrains = self.env['res.currency.rate'].search([
            ('name', '>=', min(names)),
            ('name', '<=', max(names)),
            ('currency_id', 'in', self.mapped('currency_id').ids),
            ('company_id', 'in', self.mapped('company_id').ids),
            ('id', 'not in', self.ids)
            ])
        for r in self:
            cons = constrains.filtered(
                lambda line:
                line.name == r.name
                and line.currency_id == r.currency_id
                and line.company_id == r.company_id
                )
            if cons:
                raise ValidationError(_('Only one currency rate per day allowed!'))
            else:
                constrains |= r
