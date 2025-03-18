{
    'name': 'auto_invoice_on_payment_terms',
    'version': '18.0.1.0',  # Incremented for version tracking
    'author': 'M.Ahsan',
    'website': 'https://www.tech-toch.com',
    'summary': '',
    'description': """""",
    'category': 'Accounting',
    'license': 'LGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'account','accountant',
        'account_accountant','sale','sale_account_accountant'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/auto_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
