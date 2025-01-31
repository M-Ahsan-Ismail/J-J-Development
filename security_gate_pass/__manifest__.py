{
    'name': 'Security Gate Pass',  # Module name
    'author': 'M.Ahsan',  # Author name
    'maintainer': 'M.Ahsan',  # Author name
    'description': "This is Gate Pass",  # Description about the app
    'version': '18.0.1.0',  # Correct version format for Odoo 17
    'summary': 'Gate Pass',  # Brief info about the app
    'sequence': 2,  # Position in the apps menu
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'hr','stock'],  # Dependencies
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'wizard/gate_pass_wizard_view.xml',
        'report/report.xml',
        'report/gate_pass_outward_report_temp.xml',
        'report/gate_pass_inward_report_temp.xml',
        'views/stock_picking_form_inherit.xml',
        'views/gate_pass_view.xml'
    ],

}
