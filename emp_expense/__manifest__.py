{
    'name': 'expense_employee',
    'author': 'Ahsan',
    'description': """bss_employee_expense""",
    'version': '18.0.1.2',
    'summary': 'bss_employee_expense',
    'sequence': 1,
    'category': 'Services/expenses',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',  # Core Odoo module (always required)
        'hr', 'hr_expense',  # Employee management (for linking expenses to employees)
        'account', 'account_accountant',  # Accounting module (for journal entries & financial integration)
        'mail',  # Email notifications (for approvals & status updates)
        'portal',  # Portal access (employees can submit & track expenses)
        'web',  # UI & views (for form, tree, kanban, reports)
    ]
    ,
    'installable': True,
    'application': True,  # Set to True for easy access in the Apps menu
    'auto_install': False,

    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'data/email_view.xml',
        'controller/employee_expenses_controller_views.xml',
        'wizard/rejection_wizard_view.xml',
        'views/menu_ids_view.xml',
        'views/expense.request_views.xml',

    ],
}
