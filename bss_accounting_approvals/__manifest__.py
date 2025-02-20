# -*- coding: utf-8 -*-
{
    'name': "Accounting 2-Level Approvals",

    'summary': "Bill, Invoice & Journal Entry two Approvals workflow",

    'description': """
    Bill, Invoice & Journal Entry two Approvals workflow
    """,

    'author': "M.Rizwan",
    'website': "https://www.bssuniversal.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Customizations/Studio',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant', 'accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_move_inherited_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}
