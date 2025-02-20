from odoo import api, SUPERUSER_ID


def _apply_xml_id_for_attendance_activity_and_state(env):
    """
    This is to make sure that we not raise any error because when add new record to data file although noupdate is true
    The system will always try to create that record, many case some below records are already created
    """
    env.cr.execute("""
        SELECT t1.id
        FROM attendance_activity t1 INNER JOIN attendance_state t2
        on t1.id = t2.activity_id
        WHERE t2.code = 2 or t2.code = 3
    """)
    attendance_activity_break = env.cr.dictfetchone()
    if attendance_activity_break and attendance_activity_break.get('id', False):
        env['ir.model.data'].create({
            'noupdate': True,
            'name': 'attendance_activity_break',
            'module': 'to_attendance_device',
            'model': 'attendance.activity',
            'res_id': attendance_activity_break.get('id')
            })
        env.cr.execute("""
            UPDATE attendance_activity
            set name = 'Break'
            WHERE id = %s
        """, (attendance_activity_break.get('id'),))

    env.cr.execute("""
        SELECT t1.id
        FROM attendance_activity t1 INNER JOIN attendance_state t2
        on t1.id = t2.activity_id
        WHERE t2.code = 255
    """)
    attendance_activity_unknown_punch_state = env.cr.dictfetchone()
    if attendance_activity_unknown_punch_state and attendance_activity_unknown_punch_state.get('id', False):
        env['ir.model.data'].create({
            'noupdate': True,
            'name': 'attendance_activity_unknown_punch_state',
            'module': 'to_attendance_device',
            'model': 'attendance.activity',
            'res_id': attendance_activity_unknown_punch_state.get('id')
            })
        env.cr.execute("""
            UPDATE attendance_activity
            set name = 'Unknown Punch State'
            WHERE id = %s
        """, (attendance_activity_unknown_punch_state.get('id'),))

    env.cr.execute("""
        SELECT id
        FROM attendance_state
        WHERE code = 2
    """)
    attendance_device_state_code_2 = env.cr.dictfetchone()
    if attendance_device_state_code_2 and attendance_device_state_code_2.get('id', False):
        env['ir.model.data'].create({
            'noupdate': True,
            'name': 'attendance_device_state_code_2',
            'module': 'to_attendance_device',
            'model': 'attendance.state',
            'res_id': attendance_device_state_code_2.get('id')
            })

    env.cr.execute("""
        SELECT id
        FROM attendance_state
        WHERE code = 3
    """)
    attendance_device_state_code_3 = env.cr.dictfetchone()
    if attendance_device_state_code_3 and attendance_device_state_code_3.get('id', False):
        env['ir.model.data'].create({
            'noupdate': True,
            'name': 'attendance_device_state_code_3',
            'module': 'to_attendance_device',
            'model': 'attendance.state',
            'res_id': attendance_device_state_code_3.get('id')
            })

    env.cr.execute("""
        SELECT id
        FROM attendance_state
        WHERE code = 255
    """)
    attendance_device_state_code_255 = env.cr.dictfetchone()
    if attendance_device_state_code_255 and attendance_device_state_code_255.get('id', False):
        env['ir.model.data'].create({
            'noupdate': True,
            'name': 'attendance_device_state_code_255',
            'module': 'to_attendance_device',
            'model': 'attendance.state',
            'res_id': attendance_device_state_code_255.get('id')
            })
        env.cr.execute("""
            UPDATE attendance_state
            SET name = 'Unknown Punch State (this usually happen when you check-in or out with no punch state specified)'
            WHERE code = 255
        """)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _apply_xml_id_for_attendance_activity_and_state(env)
