from odoo import models


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ This overrides to replace mail template by branding when preview email template,
        that using wizard to send email.
        """
        res = super(MailComposer, self)._onchange_template_id(template_id, composition_mode, model, res_id)
        if template_id:
            template = self.env['mail.template'].browse(template_id)
            res['value'] = template._replace_mail_template_by_brand(res['value'])
        return res
