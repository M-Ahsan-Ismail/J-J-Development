import threading

from odoo import api, models


class ImBus(models.Model):
    _inherit = 'bus.bus'

    @api.model
    def _sendone(self, channel, notification_type, message):
        """
        Skip this method in some cases.
        Why ? Because we have module viin_brand_hr attempt to write 'description' from hr.job record
        which will trigger this method and eventually trigger 'AccessShareLock' on table res.users
        see PR https://github.com/Viindoo/tvtmaaddons/pull/9966 for more details
        """
        if notification_type == 'editor_collaboration' and getattr(threading.current_thread(), 'testing', False):
            return
        super(ImBus, self)._sendone(channel, notification_type, message)
