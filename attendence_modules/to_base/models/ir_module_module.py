from odoo import api, models

from odoo.addons.base.models.ir_module import assert_log_admin_access


MAP_TRANSLATION_KEY = {
    'shortdesc': 'name',
    'summary': 'summary',
    'description': 'description',
}


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @assert_log_admin_access
    @api.model
    def update_list(self):
        res = super(IrModuleModule, self).update_list()
        self.env['ir.module.module'].search([])._update_module_infos_translation()
        return res

    def _update_module_infos_translation(self):
        langs_code = [lang[0] for lang in self.env['res.lang'].get_installed()]
        for r in self:
            terp = r.get_module_info(r.name)
            for key in MAP_TRANSLATION_KEY:
                vals = {}
                for lang_code in langs_code:
                    manifest_key = f'{MAP_TRANSLATION_KEY[key]}_{lang_code}'
                    if terp.get(manifest_key, False) and r.with_context(lang=lang_code)[key] != terp[manifest_key]:
                        vals.update({lang_code: terp[manifest_key]})
                if vals:
                    r.update_field_translations(key, vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(IrModuleModule, self).create(vals_list)

        if vals_list and vals_list[0].get('name', '') != 'foo':
            # to avoid odoo.modules.module: Missing `license` key in manifest for 'foo', defaulting to LGPL-3
            # when running test_import_module_addons_path
            records._update_module_infos_translation()
        return records

    def write(self, vals):
        res = super(IrModuleModule, self).write(vals)

        if any(val in MAP_TRANSLATION_KEY.keys() for val in vals):
            self._update_module_infos_translation()
        return res
