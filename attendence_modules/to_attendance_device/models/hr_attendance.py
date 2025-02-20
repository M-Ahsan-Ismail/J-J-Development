from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    checkin_device_id = fields.Many2one('attendance.device', string='Checkin Device', readonly=True, index=True,
                                        help="The device with which user took check in action")
    checkout_device_id = fields.Many2one('attendance.device', string='Checkout Device', readonly=True, index=True,
                                         help="The device with which user took check out action")
    activity_id = fields.Many2one('attendance.activity', string='Attendance Activity',
                                  help="This field is to group attendance into multiple Activity (e.g. Overtime, Normal Working, etc)")

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ If sync from device, skip
        """
        sync_from_device = self.env.context.get('sync_from_device', False)
        if not sync_from_device:
            super(HrAttendance, self)._check_validity()
