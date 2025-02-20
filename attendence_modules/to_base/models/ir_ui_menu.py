import os
from odoo import models, api


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def _build_viin_web_icon_path_from_image(self, img_path):
        """
        This method will turn `/module_name/path/to/image` and `module_name/path/to/image`
        into 'module_name,path/to/image' which is for web_icon

        @param img_path: path to the image that will be used for web_icon.
            The path must in the format of either `/module_name/path/to/image` or `module_name/path/to/image`

        @return: web_icon string (e.g. 'module_name,path/to/image')
        """
        path = []
        while img_path:
            img_path, basename = os.path.split(img_path)
            if img_path == os.path.sep:
                img_path = ''
            if img_path:
                path.insert(0, basename)
        return '%s,%s' % (basename, os.path.join(*path))

    def _compute_web_icon_data(self, web_icon):
        """
        Override to take web_icon for menus from
            either '/viin_brand_originmodulename'/static/description/icon.png'
            or '/viin_brand/static/img/apps/originmodulename.png'
        """
        paths = web_icon.split(',') if web_icon and isinstance(web_icon, str) else []
        if len(paths) == 2:
            # we cannot import outside the class due to the import order in the module's __init__.py
            # i.e. models are imported prior to assigning the `get_viin_brand_module_icon()` to the `get_module_icon()`
            from odoo.modules.module import get_module_icon
            img_path = get_module_icon(paths[0])
            web_icon = self._build_viin_web_icon_path_from_image(img_path)
        return super(IrUiMenu, self)._compute_web_icon_data(web_icon)
