from odoo import models, _
from odoo.exceptions import AccessError


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        try:
            return super().message_subscribe(partner_ids=partner_ids, subtype_ids=subtype_ids)
        except AccessError as e:
            if self._context.get('mail_post_autofollow'):
                raise AccessError(
                    _("You are only allowed to send messages or log notes if you don't mention anyone "
                      "since you don't have access right to add followers to this document."))
            raise AccessError(_('You may not be able to add followers. Here is the reason:\n%s') % str(e))
