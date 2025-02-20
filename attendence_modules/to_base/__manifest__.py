{
    'name': "TVTMA Base",
    'name_vi_VN': "Mô-đun Cơ Sở",

    'summary': """
Additional tools and utilities for other modules""",
    'summary_vi_VN': """
Bổ sung các công cụ và tiện ích cho các mô-đun khác""",

    'description': """
Base module that provides additional tools and utilities for developers

* Check if barcode exist by passing model and barcode field name
* Generate barcode from any number
* Find the IP of the host where Odoo is running.
* Date & Time Utilities

  * Convert time to UTC
  * UTC to local time
  * Get weekdays for a given period
  * Same Weekday next week
  * Split date

* Zip a directory and return bytes object which is ready for storing in Binary fields. No on-disk temporary file is needed.

  * usage: zip_archive_bytes = self.env['to.base'].zip_dir(path_to_directory_to_zip)

* Sum all digits of a number (int|float)
* Finding the lucky number (digit sum = 9) which is nearest the given number
* Return remote host IP by sending http request to http(s)://base_url/my/ip/
* Replace the SQL constraint `unique_name_per_day` in res.currency.rate model with Python constraint

* Replace Odoo's module icons with your own icons by

  * How to do

    * creating a new module named 'viin_brand' and place your icons in side `viin_brand/static/imp/apps/`
    * the icon name convention is `module_name.png`. For example, `mrp.png` to replace the module MRP's icon
    * upgrade all the modules (start Odoo server with option `-u all`)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô-đun cơ sở cung cấp các công cụ và tiện ích bổ sung cho các nhà phát triển

* Kiểm tra xem mã vạch có tồn tại hay không bằng cách đi qua mô hình và tên trường mã vạch
* Tạo mã vạch từ bất kỳ số nào
* Tìm IP của máy chủ lưu trữ Odoo đang chạy.
* Tiện ích Ngày & Giờ

  * Chuyển đổi thời gian sang UTC
  * UTC sang giờ địa phương
  * Lấy các ngày trong tuần trong một khoảng thời gian nhất định
  * Cùng ngày trong tuần vào tuần tới
  * Tách ngày

* Zip một thư mục và trả về đối tượng byte đã sẵn sàng để lưu trữ trong các trường Nhị phân. Không cần tệp tạm thời trên đĩa.

  * sử dụng: zip_archive_bytes = self.env['to.base'].zip_dir(path_to_directory_to_zip)

* Tính tổng tất cả các chữ số của một số (int | float)
* Tìm số may mắn (tổng = 9) gần nhất với số đã cho
* Trả lại IP máy chủ từ xa bằng cách gửi yêu cầu http đến http (s): // base_url / my / ip /
* Thay thế ràng buộc SQL `unique_name_per_day` trong mô hình res.currency.rate bằng ràng buộc Python

* Thay thế các biểu tượng mô-đun của Odoo bằng các biểu tượng của riêng bạn bằng cách

  * Làm thế nào để làm

    * tạo một mô-đun mới có tên 'viin_brand' và đặt các biểu tượng của bạn vào bên cạnh `viin_brand / static / imp / apps /`
    * quy ước tên biểu tượng là `module_name.png`. Ví dụ: `mrp.png` để thay thế biểu tượng MRP của mô-đun
    * nâng cấp tất cả các mô-đun (khởi động máy chủ Odoo với tùy chọn `-u all`)

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com/apps/app/16.0/to_base',
    'live_test_url': "https://v16demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v16demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '18.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'web',
        'base_setup',
        'mail'
        ],

    # always loaded
    'data': [
        # 'data/base_data.xml',
        # 'data/cron_data.xml',
        'views/res_country_views.xml',
        ],
    'images': ['static/description/main_screenshot.png'],
    # 'assets': {
    #     'web.assets_backend': [
    #         'to_base/static/src/js/settings_page.js',
    #         'to_base/static/src/xml/settings_page.xml'
    #         ],
    #     'web.tests_assets': [
    #         'to_base/static/tests/to_base_mock_server.js',
    #         ],
    #     },
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    # 'post_load': 'post_load',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
