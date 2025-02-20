Cài đặt
=======

1. Truy cập **Ứng dụng**;
2. Tìm từ khóa *to_attendance_device*;
3. Bấm chọn **Cài đặt**. 

Hướng dẫn sử dụng
=================

**Video hướng dẫn:** `Tích hợp Máy chấm công Sinh trắc học <https://youtu.be/wfnJ_5d8_L8>`_

Khái niệm
---------

#. **Vị trí máy chấm công**: là một model để lưu trữ vị trí nơi mà bạn lắp đặt máy chấm công bao gồm thông tin Tên vị trí và Múi giờ tại vị trí đặt máy chấm công (hỗ trợ việc ghi nhận dữ liệu vào/ra tại nhiều vị trí với múi giờ khác nhau).

#. **Trạng thái Vào/Ra**: nơi để lưu trữ các trạng thái của hoạt động chấm công và có thể được định nghĩa bởi người dùng. Trạng thái có thể là Đăng nhập, Đăng xuất, Đăng nhập tăng ca, Đăng xuất tăng ca,... Truy cập **Quản lý Vào/Ra ‣ Máy Chấm Công ‣ Trạng thái Vào/Ra** để xem danh sách các trạng thái.

#. **Hoạt động Vào/Ra**: nơi để phân loại các hoạt động chấm công vào/ra. Ví dụ:  Làm việc bình thường, Tăng ca,... Truy cập **Quản lý Vào/Ra ‣ Máy Chấm Công ‣ Hoạt động Vào/Ra** để xem danh sách hoặc tạo mới các hoạt động.

#. **Người dùng thiết bị**: nơi để lưu trữ thông tin về người dùng máy chấm công trên hệ thống và có liên kết những người dùng này với danh sách nhân viên trên phần mềm. 

#. **Dữ liệu Vào/Ra**: nơi để lưu trữ tất cả dữ liệu vào/ra được tải về từ máy chấm công. Nói cách khác, đây là cơ sở dữ liệu trung tâm của dữ liệu vào/ra của tất cả các máy chấm công. Các bản ghi này là cơ sở để tạo ra dữ liệu vào/ra của nhân viên. Trong quá trình tạo dữ liệu này, phần mềm sẽ kiểm tra tính hợp lệ của dữ liệu và đảm bảo dữ liệu vào/ra của nhân viên là đúng và hợp lệ.

#. **Quản lý Vào/Ra**: dữ liệu Quản lý Vào/Ra được tạo tự động và định kỳ bằng hoạt động định kỳ **Đồng bộ dữ liệu quản lý vào/ra**, bao gồm các trường thông tin sau:

   * Đăng nhập: thời gian đăng nhập;
   * Đăng xuất: thời gian đăng xuất;
   * Nhân viên: nhân viên liên quan;
   * Thiết bị đăng nhập: máy chấm công ghi nhận dữ liệu đăng nhập;
   * Thiết bị đăng xuất: máy chấm công ghi nhận dữ liệu đăng xuất.

#. **Máy chấm công**: là menu lưu trữ thông tin của máy chấm công. Tại đây cung cấp khá nhiều tính năng hữu ích (xem thêm tại bài hướng dẫn sử dụng `các tính năng trên giao diện Máy chấm công <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/biometric-attendance-device-intergration.html#use-active-buttons-on-the-devices-information-view>`_).

Tích hợp máy chấm công
----------------------

Truy cập **Máy chấm công > Quản lý Máy chấm công**, ấn Tạo để khai báo thông tin máy chấm công.

Xem thêm bài viết về `Tích hợp máy chấm công sinh trắc học vân tay <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/biometric-attendance-device-intergration.html#set-up-biometric-attendance-devices>`_ của chúng tôi.

.. image:: 6-thong-tin-chung.vi.jpg
   :align: center
   :height: 500
   :width: 1100
   :alt: Thông tin tích hợp máy chấm công

Liên kết người dùng máy chấm công với dữ liệu nhân viên trên phần mềm
---------------------------------------------------------------------

- `Tải danh sách nhân viên từ Viindoo lên máy chấm công <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/link_attendance_device_users_with_employees_in_viindoo_system.html#upload-the-employee-list-to-the-attendance-device>`_
- `Đăng ký nhận diện cho nhân viên <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/link_attendance_device_users_with_employees_in_viindoo_system.html#register-recognition-for-employees>`_
- `Liên kết người dùng chấm công với danh sách nhân viên <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/link_attendance_device_users_with_employees_in_viindoo_system.html#link-the-attendance-device-users-with-the-employee-in-the-viindoo-system>`_

Quản lý dữ liệu chấm công/điểm danh của nhân viên
-------------------------------------------------

Xem thêm tại bài viết về `Theo dõi và quản lý dữ liệu vào/ra <https://viindoo.com/documentation/15.0/vi/applications/human-resources/attendances/operations/manage-attendance-data.html#manage-attendance-data>`_

Hệ thống có hành động tự động để:

* Tải Dữ liệu vào/ra từ máy chấm công về hệ thống Viindoo 30 phút 1 lần.
   
  * Tải Dữ liệu vào/ra khi cho các Máy chấm công ở trạng thái Xác nhận.
  * Tạo bản ghi về Dữ liệu vào/ra trong hệ thống Viindoo (Truy cập **Quản lý Vào/Ra ‣ Máy Chấm Công ‣ Dữ liệu Vào/Ra**).
  * Tùy thuộc vào cài đặt tại máy chấm công, nó cũng có thể thực hiện các hoạt động sau:
   
    * Tạo mới Nhân viên và liên kết với người dùng trong máy chấm công nếu người dùng này khai báo trên máy chấm công.
    * Xóa dữ liệu vào/ra trên máy chấm công khi đến thời gian thiết lập.
   
* Đồng bộ dữ liệu quản lý vào/ra mỗi 30 phút 1 lần.

  * Tìm các dữ liệu vào/ra hợp lệ từ dữ liệu tải về của máy chấm công.
  * Tạo bản ghi chấm công hợp lệ cho nhân viên (Truy cập **Quản lý Vào/Ra ‣ Quản lý Vào/Ra**).
