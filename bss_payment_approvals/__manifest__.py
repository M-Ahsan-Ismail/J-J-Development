# -*- coding: utf-8 -*-
{
    'name': "Payments 2-Level Approvals",

    'summary': "Payments Two Level Approvals Workflow",

    'description': """
Long description of module's purpose
    """,

    'author': "M.Rizwan",
    'website': "https://www.bssuniversal.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Customizations/Studio',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'payment', 'account_payment', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_payment_inherited_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}
