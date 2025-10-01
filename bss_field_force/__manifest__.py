{
    'name': 'bss_field_force',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Portal check-in / check-out with live location',
    'author': 'Your Name',
    'depends': ['portal', 'website', 'web', 'sale', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'reports/route_plan_report_temp.xml',
        'views/menu_items.xml',
        'views/route_planing.xml',
        'views/res_partner_inherit.xml',
        'views/portal_templates.xml',
        'views/portal_menu.xml',
        'views/field_force_views.xml',
        'views/create_sale_order_controller_view.xml',
    ], 'images': ['static/description/icon.png'],

    # 'assets': {
    #     'web.assets_frontend': [
    #         'bss_field_force/static/src/js/portal_checkin.js',
    #     ],
    # },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
