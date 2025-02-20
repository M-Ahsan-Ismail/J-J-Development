{
    'name': "Purchase 2-Level Approvals",  # Module name
    'author': 'Ahsan',  # author name
    'maintainer': 'M.Rizwan',
    'description': "Purchase Two Level Approvals Workflow",  # desc about app
    'version': '18.0.1.0',  # specify version of app after odoo
    'summary': '',  # give little info about app
    'category': 'Customizations/Studio',  # will display in info
    'website': 'https://www.bssuniversal.com',  # will display in info
    'depends': ['base', 'purchase'],  # those modules , on which our app depends , inherit them here
    # always loaded
    'data': [
        'security/groups.xml',
        'views/purchase_custom_approval_view.xml'
    ],
'installable': True,
    'application': True,
    'sequence': 1,
}
