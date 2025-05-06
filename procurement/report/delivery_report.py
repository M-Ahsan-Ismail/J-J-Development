# # QR Code:-
#
# # from odoo import models
# # import base64
# # import qrcode
# # from io import BytesIO
# #
# #
# # class StockPicking(models.Model):
# #     _inherit = 'stock.picking'
# #
# #     def get_qr_code(self):
# #         # Hardcoded value for testing; replace with self.name for dynamic use
# #         qr_value = "WH/OUT/00001"  # Hardcoding the value from your image
# #         qr = qrcode.QRCode(version=1, box_size=10, border=4)
# #         qr.add_data(qr_value)
# #         qr.make(fit=True)
# #         img = qr.make_image(fill='black', back_color='white')
# #         buffer = BytesIO()
# #         img.save(buffer, format="PNG")
# #         qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
# #         return qr_base64
#
# # Bar Code:-
#
# from odoo import models
# import base64
# from io import BytesIO
# from barcode.codex import Code128  # Import from the correct submodule
# from barcode.writer import ImageWriter
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     def get_barcode(self):
#         # Hardcoded value for testing; replace with self.name for dynamic use
#         barcode_value = "2405223"
#         # Generate Code128 barcode
#         code128 = Code128(barcode_value, writer=ImageWriter())
#         # Save barcode to a BytesIO buffer
#         buffer = BytesIO()
#         code128.write(buffer)
#         # Encode the image as base64
#         barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
#         buffer.close()
#         return barcode_base64