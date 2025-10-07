from _datetime import datetime
import json
import requests
from odoo import http, fields
from odoo.exceptions import ValidationError
from odoo.http import request, Response
import base64
from datetime import timedelta

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PortalAttendanceController(http.Controller):

    @http.route('/field/routes/', type='http', auth='user', website=True, methods=['GET', 'POST'], csrf=False)
    def portal_attendance_page(self, **kwargs):
        user = request.env.user
        today_date = datetime.today().date()
        print(f'User: {user}')
        customers_list = []
        # fetch confirmed route.planing records for this salesperson (employee)
        route_recs = request.env['route.planing'].sudo().search([
            ('state', 'in', ['confirm', 'in_process', 'complete']),
            ('salesperson_id', '=', request.env.user.employee_id.id),
            ('date_from', '<=', today_date),
            ('date_to', '>=', today_date),
        ])

        for rec in route_recs:
            for line in rec.line_ids:
                # find if there is already a field.force record for this line+customer
                ff_rec = request.env['field.force'].sudo().search([
                    ('route_plan_id', '=', rec.id),
                    ('partner_id', '=', line.partner_id.id),
                ], limit=1)

                customers_list.append({
                    'route_id': rec.id,
                    'customer_id': line.partner_id.id,
                    'customer_name': line.partner_id.name,
                    'location': line.partner_location or '',
                    'notes': line.note_desc,
                    'field_force_id': ff_rec.id if ff_rec else False,
                    'check_in_time': ff_rec.check_in_time.strftime(
                        "%Y-%m-%d %H:%M:%S") if ff_rec and ff_rec.check_in_time else '',
                    'check_out_time': ff_rec.check_out_time.strftime(
                        "%Y-%m-%d %H:%M:%S") if ff_rec and ff_rec.check_out_time else '',
                    'total_time_spent': ff_rec.total_time_spent if ff_rec else '',
                    'check_in_address': ff_rec.check_in_address if ff_rec else '',
                    'check_out_address': ff_rec.check_out_address if ff_rec else '',
                    'is_check_in': line.is_check_in,
                    'is_check_out': line.is_check_out,
                })

        partner_list_json = json.dumps(customers_list)

        return request.render('bss_field_force.portal_attendance_page', {
            'customers_list': customers_list,
            'partner_list_json': partner_list_json,
            'user': user,
        })

    @http.route('/create/field/force/rec', type='http', auth='user', methods=['POST'], csrf=False)
    def create_field_force_record(self, **post):
        # Accept JSON body or form data
        try:
            raw = request.httprequest.get_data(as_text=True)
            payload = json.loads(raw) if raw else dict(post)
        except Exception:
            payload = dict(post)

        # normalize names
        lat_in = payload.get('lat_in') or payload.get('latitude_in') or payload.get('latitudeIn') or None
        lon_in = payload.get('lon_in') or payload.get('longitude_in') or payload.get('longitudeIn') or None
        lat_out = payload.get('lat_out') or payload.get('latitude_out') or payload.get('latitudeOut') or None
        lon_out = payload.get('lon_out') or payload.get('longitude_out') or payload.get('longitudeOut') or None

        check_in_loc = payload.get('check_in_loc') or payload.get('check_in_address') or ''
        check_out_loc = payload.get('check_out_loc') or payload.get('check_out_address') or ''

        check_in_time_str = payload.get('check_in_time') or payload.get('checkInTime') or ''
        check_out_time_str = payload.get('check_out_time') or payload.get('checkOutTime') or ''

        partner_id = payload.get('partner_id') or False
        partner_address = payload.get('partner_address') or ''

        # require explicit post
        is_post = payload.get('post') in (True, '1', 'true', 'True') or bool(partner_id)
        if not is_post:
            return Response(json.dumps({'success': True, 'message': 'ignored, not a post'}),
                            content_type='application/json')

        try:
            partner_id = int(partner_id) if partner_id else False
        except Exception:
            partner_id = False

        def parse_client_datetime(s):
            if not s:
                return None
            s = str(s).strip()
            try:
                if s.endswith('Z'):
                    s2 = s[:-1]
                    dt = datetime.fromisoformat(s2)
                else:
                    dt = datetime.fromisoformat(s)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                pass
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y, %I:%M:%S %p'):
                try:
                    dt = datetime.strptime(s, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    continue
            return s

        def reverse_geocode(lat, lon):
            try:
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={'lat': float(lat), 'lon': float(lon), 'format': 'jsonv2'},
                    headers={'User-Agent': 'odoo-portal-checkin/1.0'},
                    timeout=5
                )
                if resp.ok:
                    return resp.json().get('display_name')
            except Exception:
                pass
            return None

        if not check_in_loc and lat_in and lon_in:
            check_in_loc = reverse_geocode(lat_in, lon_in) or ''
        if not check_out_loc and lat_out and lon_out:
            check_out_loc = reverse_geocode(lat_out, lon_out) or ''

        # Build vals
        vals = {
            'user_id': request.env.user.id,
            'partner_id': partner_id or False,
            'partner_address': partner_address or False,
        }

        if lat_in and lon_in:
            try:
                vals['latitude_in'] = float(lat_in)
            except Exception:
                vals['latitude_in'] = 0.0
            try:
                vals['longitude_in'] = float(lon_in)
            except Exception:
                vals['longitude_in'] = 0.0
            vals['check_in_address'] = check_in_loc or partner_address or 'Unknown'
            parsed_in = parse_client_datetime(check_in_time_str)
            if parsed_in:
                vals['check_in_time'] = parsed_in
            else:
                vals['check_in_time'] = fields.Datetime.now()
            vals['action_check_in'] = 'checkin'

        if lat_out and lon_out:
            try:
                vals['latitude_out'] = float(lat_out)
            except Exception:
                vals['latitude_out'] = 0.0
            try:
                vals['longitude_out'] = float(lon_out)
            except Exception:
                vals['longitude_out'] = 0.0
            vals['check_out_address'] = check_out_loc or partner_address or 'Unknown'
            parsed_out = parse_client_datetime(check_out_time_str)
            if parsed_out:
                vals['check_out_time'] = parsed_out
            else:
                vals['check_out_time'] = fields.Datetime.now()
            vals['action_check_out'] = 'checkout'

        # Create record: try field.force else portal.attendance
        Model = None
        if 'field.force' in request.env:
            Model = request.env['field.force']
        else:
            # fallback - create in ir.model.data? raise
            return Response(json.dumps({'success': False, 'error': 'no_model'}), content_type='application/json')

        route_plan_id = payload.get('route_plan_id') or payload.get('rec_id') or None
        try:
            route_plan_id = int(route_plan_id) if route_plan_id else False
        except Exception:
            route_plan_id = False

        if route_plan_id:
            vals['route_plan_id'] = route_plan_id

        # --- validation before creating record ---
        try:
            self._check_already_checked_in(route_plan_id, partner_id)
        except ValidationError as e:
            return Response(
                json.dumps({'success': False, 'error': str(e)}),
                content_type='application/json'
            )

        rec = Model.sudo().create(vals)

        # --- update planing.lines booleans for this route+partner ---
        try:
            if route_plan_id and partner_id:
                lines_id = request.env['planing.lines'].sudo().search(domain=[
                    ('route_planing_id', '=', route_plan_id),
                    ('partner_id', '=', partner_id),
                ], limit=1)
                if lines_id:
                    # If the request contained check-in info, set is_check_in
                    if (lat_in is not None and lon_in is not None) or vals.get('check_in_time'):
                        lines_id.sudo().write({'is_check_in': True})
        except Exception as e:
            print(f'Unable To Update Route Plan: {e}')

        response = {
            'success': True,
            'id': rec.id,
            'partner_id': rec.partner_id.id if rec.partner_id else False,
            'partner_address': rec.partner_address or '',
            'check_in': {
                'latitude_in': rec.latitude_in or 0.0,
                'longitude_in': rec.longitude_in or 0.0,
                'address': rec.check_in_address or '',
                'time': rec.check_in_time.strftime("%Y-%m-%d %H:%M:%S") if rec.check_in_time else '',
            },
            'check_out': {
                'latitude_out': rec.latitude_out or 0.0,
                'longitude_out': rec.longitude_out or 0.0,
                'address': rec.check_out_address or '',
                'time': rec.check_out_time.strftime("%Y-%m-%d %H:%M:%S") if rec.check_out_time else '',
            },
            'total_hours': None,
        }
        return Response(json.dumps(response), content_type='application/json')

    def _check_already_checked_in(self, route_id, partner_id):
        """Helper: Check if user already checked in for this route & partner."""
        if not route_id or not partner_id:
            return False  # no check needed

        lines = request.env['planing.lines'].sudo().search([
            ('route_planing_id', '=', route_id),
            ('partner_id', '=', partner_id),
            ('is_check_in', '=', True),
            ('is_check_out', '=', False)
        ], limit=1)

        if lines:
            raise ValidationError(
                "You have already checked in for this customer on this route. Please check out first."
            )

    @http.route('/update/field/force/rec', type='http', auth='user', methods=['POST'], csrf=False)
    def portal_attendance_checkout_state(self, **post):
        """
        POST payload:
            { "record_id": <route.planing id>,
              "field_force_id": <optional field.force id>,
              "partner_id": <optional partner id>,
              "latitude_out": <float>,
              "longitude_out": <float>,
              "check_out_time": <ISO string or server will set now>,
              "check_out_loc": <address string>
            }

        Sets route.state = 'complete' and updates the specified field.force record.
        """
        try:
            raw = request.httprequest.get_data(as_text=True)
            payload = json.loads(raw) if raw else dict(post)
        except Exception:
            payload = dict(post)

        rec_id = payload.get('record_id') or payload.get('rec_id') or payload.get('id')
        if not rec_id:
            return Response(json.dumps({'success': False, 'error': 'missing_record_id'}),
                            content_type='application/json')

        try:
            route = request.env['route.planing'].sudo().browse(int(rec_id))
        except Exception:
            return Response(json.dumps({'success': False, 'error': 'invalid_record_id'}),
                            content_type='application/json')

        if not route or not route.exists():
            return Response(json.dumps({'success': False, 'error': 'record_not_found'}),
                            content_type='application/json')

        # locate the field.force record to update:
        ff = None
        ff_id = payload.get('field_force_id')
        if ff_id:
            try:
                ff = request.env['field.force'].sudo().browse(int(ff_id))
                if not ff.exists():
                    ff = None
            except Exception:
                ff = None

        # fallback: try to find latest field.force for this route + partner (if partner_id provided)
        if not ff:
            partner_id = payload.get('partner_id')
            domain = [('route_plan_id', '=', route.id)]
            if partner_id:
                try:
                    partner_id_int = int(partner_id)
                    domain.append(('partner_id', '=', partner_id_int))
                except Exception:
                    pass
            ff = request.env['field.force'].sudo().search(domain, order='id desc', limit=1)

        check_out_time_str = payload.get('check_out_time') or ''

        # helper to parse ISO or common formats (simple)
        def _parse_client_datetime(s):
            if not s:
                return None
            s = str(s).strip()
            try:
                if s.endswith('Z'):
                    s2 = s[:-1]
                    dt = datetime.fromisoformat(s2)
                else:
                    dt = datetime.fromisoformat(s)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                # try common fallback
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M:%S', '%m/%d/%Y, %I:%M:%S %p'):
                    try:
                        dt = datetime.strptime(s, fmt)
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
            return None

        result = {'success': True, 'route_id': route.id, 'field_force_id': False, 'state': route.state}

        if ff and ff.exists():
            vals = {}
            if payload.get('latitude_out') is not None:
                try:
                    vals['latitude_out'] = float(payload['latitude_out'])
                except Exception:
                    vals['latitude_out'] = 0.0
            if payload.get('longitude_out') is not None:
                try:
                    vals['longitude_out'] = float(payload['longitude_out'])
                except Exception:
                    vals['longitude_out'] = 0.0
            if payload.get('check_out_loc'):
                vals['check_out_address'] = payload.get('check_out_loc')
            parsed = _parse_client_datetime(check_out_time_str)
            if parsed:
                vals['check_out_time'] = parsed
            else:
                vals['check_out_time'] = fields.Datetime.now()
            vals['action_check_out'] = 'checkout'
            try:
                ff.sudo().write(vals)
                result['field_force_id'] = ff.id

                # --- update planing.lines is_check_out flag ---
                try:
                    if route.id and ff.partner_id:
                        line = request.env['planing.lines'].sudo().search([
                            ('route_planing_id', '=', route.id),
                            ('partner_id', '=', ff.partner_id.id),
                        ], limit=1)
                        if line:
                            line.sudo().write({'is_check_out': True})
                except Exception as e:
                    # optional: log or print
                    print(f"Unable to update planing.lines checkout flag: {e}")
                # --- end update ---

                # also return latest values for UI convenience
                result['check_out'] = {
                    'time': ff.check_out_time.strftime("%Y-%m-%d %H:%M:%S") if ff.check_out_time else '',
                    'address': ff.check_out_address or '',
                }
                # compute hours if both present
                try:
                    if ff.check_in_time and ff.check_out_time:
                        delta = ff.check_out_time - ff.check_in_time
                        result['total_hours'] = round(delta.total_seconds() / 3600.0, 3)
                    else:
                        result['total_hours'] = None
                except Exception:
                    result['total_hours'] = None
            except Exception as e:
                return Response(json.dumps({'success': False, 'error': 'write_failed', 'message': str(e)}),
                                content_type='application/json')

        return Response(json.dumps(result), content_type='application/json')


class PortalRoutePlanPDF(http.Controller):
    @http.route('/route_plan/pdf/all', type='http', auth='user', website=True)
    def download_all_route_plan_pdf(self, **kw):
        try:
            # Fetch confirmed route.planing records for the current salesperson
            route_recs = request.env['route.planing'].sudo().search([
                ('state', '=', 'confirm'),
                ('salesperson_id', '=', request.env.user.employee_id.id),
            ])
            if not route_recs:
                return request.not_found("No confirmed routes found.")

            # Find the report
            report = request.env['ir.actions.report'].sudo().search([
                ('report_name', '=', 'bss_field_force.report_route_planing_minimal')
            ], limit=1)
            if not report:
                return request.not_found("Report template not found.")

            # Render PDF
            pdf_content = report._render_qweb_pdf(report.report_name, res_ids=route_recs.ids)[0]
            if not pdf_content:
                return request.not_found("PDF generation failed.")

            # Return PDF as download
            return request.make_response(pdf_content, headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf_content)),
                ('Content-Disposition', 'attachment; filename=Route_Planning_Report.pdf')
            ])
        except Exception as e:
            _logger = request.env['ir.logging'].sudo()
            _logger.create({
                'name': 'Portal Route PDF Error',
                'type': 'server',
                'dbname': request.env.cr.dbname,
                'level': 'ERROR',
                'message': str(e),
                'path': '/route_plan/pdf/all',
                'func': 'download_all_route_plan_pdf',
                'line': '1',
            })
            return request.not_found("An error occurred while generating PDF.")
