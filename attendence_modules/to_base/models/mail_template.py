import importlib

import odoo
from odoo import api, models

# from ..__init__ import _get_branding_module, viin_brand_manifest


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    @api.model
    def _replace_mail_template_by_brand(self, values):
        """
        This overrides to replace mail template by brand with '/branding_module/apriori.py'
        where apriori contains dict:
        mail_template_terms = [
            ('<a target="_blank" href="https://www.odoo.com?utm_source=db&amp;utm_medium=portalinvite" style="color: #875A7B;">Odoo</a>', '<a target="_blank" href="https://viindoo.com?utm_source=db&amp;utm_medium=portalinvite" style="color: #875A7B;">Viindoo</a>'),
            ('Odoo', 'Viindoo'),
        ]
        :return: list with a tuple with the name and base64 content of the attachment by brand
        """
        branding_module = _get_branding_module()
        for adp in odoo.addons.__path__:
            if viin_brand_manifest.get('installable', False):
                try:
                    mail_template_terms = importlib.import_module('odoo.addons.%s.apriori' % branding_module).mail_template_terms or []
                    fields_to_replace = ['subject', 'body', 'body_html']
                    for term in mail_template_terms:
                        for field in fields_to_replace:
                            if field in values:
                                values[field] = values[field].replace(term[0], term[1])
                except Exception:
                    pass
        return values

    def generate_email(self, res_ids, fields):
        res = super(MailTemplate, self).generate_email(res_ids, fields)
        res = self._replace_mail_template_by_brand(res)
        return res
