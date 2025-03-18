{
    'name': 'Invoice Surcharge',
    'version': '18.0.1.0',  # Incremented for version tracking
    'author': 'M.Rizwan',
    'website': 'https://www.tech-toch.com',
    'summary': 'Manage late payment surcharges in accounting.',
    'description': """This module adds functionality to apply late payment surcharges 
    based on overdue invoices. It integrates with Odoo Accounting to ensure accurate 
    financial tracking.""",
    'category': 'Accounting',
    'license': 'LGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'sale',
        'account',
        'account_accountant',
    ],
    'data': [
        'views/late_payment_surcharge_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
