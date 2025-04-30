{
    'name': 'procurement',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base','web', 'crm', 'stock', 'sale', 'hr', 'purchase', 'mrp'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'wizard/rejection_wizard.xml',
        # 'report/delivery_report.xml',
        'report/po_request_report_temp.xml',
        'views/po_request.xml',
        'views/purchase_order_inherit.xml',

    ],
    'images': ['static/description/icon.png'],

}
