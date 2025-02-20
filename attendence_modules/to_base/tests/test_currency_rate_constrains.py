from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestCurrencyRates(TransactionCase):

    def setUp(self):
        super(TestCurrencyRates, self).setUp()
        self.company11 = self.env['res.company'].create({'name': 'XXX'})
        self.company12 = self.env['res.company'].create({'name': 'YYY'})
        self.currency11 = self.env['res.currency'].create({'name': 'XYX', 'symbol': 'XYX', 'rounding': 1.0})
        self.currency12 = self.env['res.currency'].create({'name': 'XYY', 'symbol': 'XYY', 'rounding': 1.0})

    def test_01_currency_rate_constrains(self):
        self.env['res.currency.rate'].create({
            'name': '2010-01-01',
            'currency_id': self.currency11.id,
            'rate': 1.0,
            'company_id': self.company11.id
            })
        self.env['res.currency.rate'].create({
            'name': '2010-01-01',
            'currency_id': self.currency11.id,
            'rate': 1.0,
            'company_id': self.company12.id
            })
        self.env['res.currency.rate'].create({
            'name': '2010-01-01',
            'currency_id': self.currency12.id,
            'rate': 2.0,
            'company_id': self.company11.id
            })
        with self.assertRaises(ValidationError):
            self.env['res.currency.rate'].create({
                'name': '2010-01-01',
                'currency_id': self.currency11.id,
                'rate': 2.0,
                'company_id': self.company11.id
                })
