# -*- coding: utf-8 -*-
{
    'name': 'Approval Notifier',
    'summary': "Send mail to the group of people for approve.",
    'category': 'Tools',
    'author': 'Shah Alam Sumon',
    'version': '18.0.0.1',
    'website': 'https://github.com/ShahAlamSumon',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'images': ["static/description/banner.gif"],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'wizards/model_state_wizard.xml',
        'views/approval_model_views.xml',
    ],
}
