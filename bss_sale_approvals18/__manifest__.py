# -*- coding: utf-8 -*-
{
    'name': "Sales 2-Level Approvals",

    'summary': "Sale 2-Level Approvals Work flow",

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
    'depends': ['base', 'sale', 'sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/sale_order_inherited_view.xml',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
}
