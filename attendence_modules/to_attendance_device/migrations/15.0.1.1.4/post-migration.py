from odoo import SUPERUSER_ID, api


def _delete_hr_attendance_records(env):
    user_attendances = env['user.attendance'].search([('hr_attendance_id', '=', False)])
    to_unlink_hr_attendances = env['hr.attendance']
    for uatt in user_attendances:
        hr_attendance = env['hr.attendance'].search(
            [('employee_id', '=', uatt.employee_id.id),
            ('check_in', '=', uatt.timestamp),
            ('checkin_device_id', '=', uatt.device_id.id)], limit=1
        )
        to_unlink_hr_attendances += hr_attendance
    if len(to_unlink_hr_attendances) != 0:
        to_unlink_hr_attendances.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _delete_hr_attendance_records(env)
