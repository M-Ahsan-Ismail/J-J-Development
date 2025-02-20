# -*- coding: utf-8 -*-
{
    'name': " Hide BOM cost & product cost in BoM Overview",

    'summary': "If user access rights is not given then will not show bom and product cost. Hide BOM cost & product cost in BOM structure cost. Hide BOM cost and product cost in printed PDF report.",

    'description': """
If user access rights is not given then will not show bom and product cost.
     Hide BOM cost & product cost in BOM structure cost.
     Hide BOM cost and product cost in printed PDF report.
     """,

    'author': "M.Rizwan",
    'website': "https://www.bssuniversal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations/Studio',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'bss_mrp_access/static/src/components/inherited_bom_overview_component.js',
        ]
    },
}
