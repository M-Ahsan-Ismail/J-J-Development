from odoo import models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_viin_brand_modules_icon(self, modules):
        # we cannot import outside the class due to the import order in the module's __init__.py
        # i.e. models are imported prior to assigning the `get_viin_brand_module_icon()` to the `get_module_icon()`
        from odoo.modules.module import get_module_icon
        result = []
        for module in modules:
            result.append(get_module_icon(module))
        return result
