{
    'name': 'Backdate Entries',
    'version': '18.0',
    'category': 'Extra Tools',
    'author': "Ahsan",
    'website': "ahsan-developer.netlify.app",
    'summary': 'The Backdate Entries module allows users to enter transactions on a date prior to the current date.',
    'depends': [
        'stock','account','sale','purchase', 'mrp','stock', 'stock_account','account_accountant'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/backdate_wiz_view.xml',
        'views/backdate_action.xml'
    ],
    "license": "AGPL-3",
    'images': ['static/description/banner.gif'],
    "auto_install": False,
    "installable": True,
    "application": True,
}
