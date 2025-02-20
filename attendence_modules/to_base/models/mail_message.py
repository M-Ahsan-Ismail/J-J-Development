from odoo import models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _invalidate_documents(self, model=None, res_id=None):
        """Override to allow delete orphan messages of non-existing models if the context
        `ignore_non_exist_model_error` is passed as True.
        """
        if not self._context.get('ignore_non_exist_model_error'):
            super()._invalidate_documents(model=model, res_id=res_id)
        else:
            try:
                with self.env.cr.savepoint():
                    super()._invalidate_documents(model=model, res_id=res_id)
            except KeyError:
                pass
