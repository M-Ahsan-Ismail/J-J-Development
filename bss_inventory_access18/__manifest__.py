{
    'name': 'Inventory Access Rights',
    'author': 'Ahsan',
    'description': """
        This module manages access rights for Inventory Valuation.
        - Restricts access to `unit_cost` and `value` fields in Stock Valuation Layer.
        - Introduces a new security group for controlling inventory valuation access.
    """,
    'version': '18.0.1.1',
    'summary': 'Access Rights for Stock Valuation Layer Fields',
    'sequence': 1,
    'category': 'Inventory',
    'website': 'https://www.google.com',
    'license': 'LGPL-3',
    'depends': ['base', 'stock', 'mrp', 'stock_account'],
    'installable': True,
    'application': False,  # Changed to False since it's an access control module
    'auto_install': False,  # Ensures it doesn't install automatically
    'data': [
        'security/groups.xml',
        'views/inventory_access_view.xml',
    ],
}

