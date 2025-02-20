{
    'name': "Safe Confirm Button",
    'name_vi_VN': "Nút Xác Nhận An Toàn",
    'summary': """
Draw more attention on dangerous confirmation action
        """,
    'summary_vi_VN': """
Thu hút sự chú ý nhiều hơn vào hành động xác nhận nguy hiểm
        """,
    'description': """

Key Features
============
* This application adds safe_confirm attribute to button tag to draw more attention from users. It is useful for action that could harm something
* Example

.. code-block:: xml

  <button name="action_clear_data" type="object" string="Clear Data"
      safe_confirm="Odoo will connect and clear all device data (include: user, attendance report, finger database). Do you want to proceed?"
      help="Clear all data from the device" groups="hr_attendance.group_hr_attendance_manager" />

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

     'description_vi_VN': """

Tính năng nổi bật
=================
* Ứng dụng này thêm thuộc tính safe_confirm (xác nhận an toàn) vào thẻ nút để thu hút sự chú ý của người dùng, đặc biệt hữu ích khi thực hiện hành động có thể gây hại tới đối tượng khác.
* Ví dụ

.. code-block:: xml

  <button name="action_clear_data" type="object" string="Clear Data"
      safe_confirm="Odoo will connect and clear all device data (include: user, attendance report, finger database). Do you want to proceed?"
      help="Clear all data from the device" groups="hr_attendance.group_hr_attendance_manager" />

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com/apps/app/16.0/to_safe_confirm_button',
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    # always loaded
    'data': [
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'to_safe_confirm_button/static/src/js/safe_confirm.js',
    #         'to_safe_confirm_button/static/src/xml/safe_confirm.xml',
    #         ],
    #     },
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
