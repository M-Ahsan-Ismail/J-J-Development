{
    'name': 'Receipt 2-Level Approvals',
    'author': 'Ahsan',
    'maintainer': 'M.Rizwan',
    'summary': "Inventory->Receipt 2-Level Approvals Work flow",
    'version': '18.0.1.0',
    'sequence': 1,
    'category': 'Customizations/Studio',
    'website': 'https://www.bssuniversal.com.com',
    'depends': ['base', 'stock', 'mail'],  # if you need mail for other purposes
    'installable': True,
    'application': True,
    #
    'data': [
        'security/groups.xml',
        'views/inventory_transfer_receipt_custom_approval_view.xml',
    ]
}
