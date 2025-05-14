{
    'name': 'procurement',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Rizwan',
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'web', 'crm', 'stock', 'sale', 'hr', 'purchase', 'mrp', 'approvals'],  # Dependencies
    'installable': True,
    'application': True,
    "license": "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'wizard/rejection_wizard.xml',
        # 'report/delivery_report.xml',
        'report/po_request_report_temp.xml',
        'views/po_request.xml',
        'views/purchase_order_inherit.xml',
        'views/inherit_approval_request_view.xml',

    ],
    'images': ['static/description/icon.png'],

}
