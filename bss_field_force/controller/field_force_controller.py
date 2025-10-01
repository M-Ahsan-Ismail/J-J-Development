# -*- coding: utf-8 -*-
from _datetime import datetime
import json
import requests
from odoo import http, fields
from odoo.http import request, Response
import base64


class PortalAttendanceController(http.Controller):

    @http.route('/field/routes/', type='http', auth='user', website=True)
    def portal_attendance_page(self, **kwargs):
        user = request.env.user
        customers_list = []
        # fetch confirmed route.planing records for this salesperson (employee)
        customer_recs = request.env['route.planing'].sudo().search([
            ('state', '=', 'confirm'),
            ('salesperson_id', '=', request.env.user.employee_id.id),
        ])
        for rec in customer_recs:
            # iterate lines (line_ids) and add one row per line
            for line in rec.line_ids:
                customers_list.append({
                    'id': rec.id,
                    'customer_id': line.partner_id.id,
                    'customer_name': line.partner_id.name,
                    'location': line.partner_location or '',
                    'notes': line.note_desc,
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

        rec = Model.sudo().create(vals)

        if route_plan_id:
            try:
                route_rec = request.env['route.planing'].sudo().browse(route_plan_id)
                if route_rec and route_rec.exists():
                    # only write the field_force_id (and optionally change state if desired)
                    route_rec.sudo().write({'field_force_id': rec.id})
                    # optional: set state to in_process or whatever business logic requires:
                    # route_rec.sudo().write({'field_force_id': rec.id, 'state': 'in_process'})
            except Exception:
                # don't let linking failure crash the whole request; you may want to log this
                pass

        total_hours = None
        if rec.check_in_time and rec.check_out_time:
            try:
                delta = rec.check_out_time - rec.check_in_time
                total_hours = round(delta.total_seconds() / 3600.0, 3)
            except Exception:
                total_hours = None

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
            'total_hours': total_hours,
        }
        return Response(json.dumps(response), content_type='application/json')

    @http.route('/portal/attendance/checkin_state', type='http', auth='user', methods=['POST'], csrf=False)
    def portal_attendance_checkin_state(self, **post):
        """
        Accepts JSON or form POST with { "record_id": <id> } and sets route.planing.state = 'in_process'
        """
        print(f'Hited Me , Called Me... {post}')
        try:
            raw = request.httprequest.get_data(as_text=True) or None
            payload = json.loads(raw) if raw and raw.strip() else dict(post)
        except Exception:
            payload = dict(post)

        rec_id = payload.get('record_id') or payload.get('rec_id') or payload.get('id')
        if not rec_id:
            return Response(json.dumps({'success': False, 'error': 'missing_record_id'}),
                            content_type='application/json')

        try:
            rec_id = int(rec_id)
        except Exception:
            return Response(json.dumps({'success': False, 'error': 'invalid_record_id'}),
                            content_type='application/json')

        rec = request.env['route.planing'].sudo().browse(rec_id)
        if not rec or not rec.exists():
            return Response(json.dumps({'success': False, 'error': 'record_not_found'}),
                            content_type='application/json')

        try:
            rec.sudo().write({'state': 'in_process'})
        except Exception as e:
            return Response(json.dumps({'success': False, 'error': 'write_failed', 'message': str(e)}),
                            content_type='application/json')

        return Response(json.dumps({'success': True, 'new_state': rec.state, 'id': rec.id}),
                        content_type='application/json')

    @http.route('/portal/attendance/checkout_state', type='http', auth='user', methods=['POST'], csrf=False)
    def portal_attendance_checkout_state(self, **post):
        """
        Accepts JSON or form POST with { "record_id": <id> } and sets route.planing.state = 'complete'
        """
        try:
            raw = request.httprequest.get_data(as_text=True) or None
            payload = json.loads(raw) if raw and raw.strip() else dict(post)
        except Exception:
            payload = dict(post)

        rec_id = payload.get('record_id') or payload.get('rec_id') or payload.get('id')
        if not rec_id:
            return Response(json.dumps({'success': False, 'error': 'missing_record_id'}),
                            content_type='application/json')

        try:
            rec_id = int(rec_id)
        except Exception:
            return Response(json.dumps({'success': False, 'error': 'invalid_record_id'}),
                            content_type='application/json')

        rec = request.env['route.planing'].sudo().browse(rec_id)
        if not rec or not rec.exists():
            return Response(json.dumps({'success': False, 'error': 'record_not_found'}),
                            content_type='application/json')

        try:
            rec.sudo().write({'state': 'complete'})
        except Exception as e:
            return Response(json.dumps({'success': False, 'error': 'write_failed', 'message': str(e)}),
                            content_type='application/json')

        return Response(json.dumps({'success': True, 'new_state': rec.state, 'id': rec.id}),
                        content_type='application/json')


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
