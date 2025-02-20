from odoo import fields
from odoo.tools import relativedelta
from odoo.addons.to_attendance_device.tests.common import Common
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestHrAttendance(Common):

    # Case 11: test method get last_hr_attedance
    def test_01_get_last_hr_attendance_record(self):
        checkin_with_device = self.env['hr.attendance'].create({
            'employee_id': self.hr_employee.id,
            'check_in': fields.datetime.now() - relativedelta(days=4),
            'check_out': fields.datetime.now() - relativedelta(days=3),
            'checkin_device_id': self.attendance_device.id,
            'checkout_device_id': self.attendance_device.id,
        })
        checkin_am = self.env['hr.attendance'].create({
            'employee_id': self.hr_employee.id,
            'check_in': fields.datetime.now() - relativedelta(days=2),
            'check_out': fields.datetime.now() - relativedelta(days=1),
        })
        last_hr_attendance = self.user_attendance._get_last_hr_attendance(self.user_attendance, checkin_with_device + checkin_am)
        # we skip the hr.attendance that do not have checkin device id
        self.assertEqual(last_hr_attendance, checkin_with_device)
