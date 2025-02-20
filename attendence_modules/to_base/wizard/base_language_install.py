from odoo import models


class BaseLanguageInstall(models.TransientModel):
    _inherit = 'base.language.install'

    def lang_install(self):
        res = super(BaseLanguageInstall, self).lang_install()
        modules = self.env['ir.module.module'].search([])
        modules._update_module_infos_translation()
        return res
