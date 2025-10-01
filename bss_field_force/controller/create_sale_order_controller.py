import re
import odoo
from odoo import http, fields
from odoo.http import request


class CreateSaleOrderController(http.Controller):

    @http.route('/create/sale/order', type='http', auth="user", website=True, methods=['GET', 'POST'], csrf=True)
    def create_sale_order(self, **post):
        so_id = None
        product_list, customer_list = [], []

        # Get products
        for product in request.env['product.template'].sudo().search([]):
            product_list.append({'product_id': product.id, 'product_name': product.name})

        # Get customers
        for customer in request.env['res.partner'].sudo().search([]):
            customer_list.append({'customer_id': customer.id, 'customer_name': customer.name})

        error_message = False

        if request.httprequest.method == 'POST':
            print(f'Post: {post}')
            try:
                customer_id = int(post.get('customer_id') or 0)
                date_order_str = post.get('date_order') or ''
                date_order_str = date_order_str.replace('T', ' ')  # Convert '2025-09-30T15:40' -> '2025-09-30 15:40'

                date_order = fields.Datetime.from_string(date_order_str)

                if not customer_id:
                    raise odoo.exceptions.ValidationError('Customer is required')

                # Parse dynamic product lines
                indices = set()
                for key in post.keys():
                    m = re.match(r'product_id_(\d+)', key)
                    if m:
                        indices.add(int(m.group(1)))

                order_lines = []
                for i in sorted(indices):
                    product_template_id = int(post.get(f'product_id_{i}') or 0)
                    quantity = float(post.get(f'quantity_{i}') or 0)
                    price = float(post.get(f'price_{i}') or 0)

                    if not product_template_id or quantity <= 0 or price <= 0:
                        continue

                    # Get the first variant of the product template
                    product_template_id = int(post.get(f'product_id_{i}'))
                    product_template = request.env['product.template'].sudo().browse(product_template_id)

                    # Pick a variant (first one) or a specific variant you want
                    product_variant = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', product_template.id)], limit=1
                    )
                    print(f'Name: {product_template.name}   {product_variant.name}')
                    print(f'Product ID: {product_template.id}   {product_variant.id}')
                    if not product_variant:
                        continue

                    order_lines.append((0, 0, {
                        'product_template_id': product_template.id,
                        'product_id': product_variant.id,  # <-- explicitly set product
                        'product_uom_qty': quantity,
                        'price_unit': price,
                        'name': product_template.name,  # force correct display
                    }))

                if not order_lines:
                    raise odoo.exceptions.ValidationError('At least one valid product line is required')

                # Create Sale Order
                sale_order_id = request.env['sale.order'].sudo().create({
                    'partner_id': customer_id,
                    'date_order': date_order,
                    'order_line': order_lines,
                })
                print(f'Sale Order ID: {sale_order_id}')
                so_id = sale_order_id.name


            except Exception as e:
                request.env.cr.rollback()
                error_message = str(e)

        return request.render('bss_field_force.create_sale_order_controller_id', {
            'product_list': product_list,
            'customer_list': customer_list,
            'error_message': error_message,
            'so_id': so_id,
        })
