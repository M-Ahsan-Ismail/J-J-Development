{
    'name': 'Assets 2-Level Approvals',  # Module name
    'author': 'Ahsan',  # author name
    'maintainer': 'M.Rizwan',
    'description': "Two Level Approvals",  # desc about app
    'version': '18.0.1.0',  # specify version of app after odoo
    'summary': 'Assets 2-Level Approvals WorkFlow',  # give little info about app
    'sequence': 1,  # set the position in all apps
    'category': 'Customizations/Studio',  # will displayed in info
    'website': 'https://www.bssuniversal.com',  # will displayed in info
    'depends': ['base', 'account','account_accountant','account_asset'],
    'installable': True,
    'application': True,
    'data': [
        'security/groups.xml',
        'views/asset_custom_approval_view.xml',
    ]
}
