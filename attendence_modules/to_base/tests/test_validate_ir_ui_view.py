from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestValidateIrUiView(TransactionCase):

    def test_01_validate_ir_ui_view(self):
        """Validate all views after installation to avoid errors
        Case:
            module A xpath from module B's view
            module C xpath and replace view of module B

        If module A is installed before module C => no error
        If module C is installed before module A => error, because the view has been replaced
        """
        views = self.env['ir.ui.view'].search([])
        views._check_xml()
