{
    'name': 'cost_sheet_builder',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'crm', 'stock', 'sale'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'wizard/rejection_wizard.xml',
        'report/cost_sheet_report_template.xml',
        'views/cost_sheet_builder_view.xml',
        'views/sale_order_inherit.xml',

    ], 'images': ['static/description/icon.png'],

}
