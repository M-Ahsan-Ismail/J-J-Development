from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ApprovalModel(models.Model):
    _name = "approval.model"
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string='Model Name', required=True, ondelete='set default')
    group_id = fields.Many2one('res.groups', string='Approval Group', required=True)
    state = fields.Char(string='Status', readonly=True)
    active = fields.Boolean('Active', default=True)

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.state = False
            self.group_id = []

    def action_open(self):
        model_name = self.model_id.model
        model_objs = self.env[model_name]
        selection_list = []
        if 'state' in model_objs._fields:
            selection_list = model_objs._fields['state'].selection
        else:
            raise UserError(_("This model have no state. Please select another model."))

        return {
            'name': 'State',
            'view_mode': 'form',
            'res_model': 'approval.model.state.wizard',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'selection_list': selection_list,
            }
        }

    def cron_approval_mail(self):
        active_recs = self.search([('active', '=', True)])
        for rec in active_recs:
            receivers = self.env['res.groups'].search([('id', '=', rec.group_id.id)])
            mail_user_list = []
            if receivers:
                mail_user_list = [user.partner_id.email for user in receivers.users]
            else:
                _logger.error("No receiving user found.")
            if rec.model_id.name:
                subject = "Reminder for {}'s approval.".format(rec.model_id.name)
            else:
                subject = "Reminder for approval."
            str_url = ''
            model_objs = self.env[rec.model_id.model].search([('state', '=', rec.state)])
            for model_obj in model_objs:
                title = model_obj.name
                link = "web#id={}&model={}&view_type=form".format(model_obj.id, rec.model_id.model)
                str_url = str_url + '<li><a href={}>Click here to approve {} </a></li>'.format(link, title)
            body = "Dear user," \
                   "Hope this mail finds you well. " \
                   "This is gentle remainder that, some record(s) waiting for your approval in ERP." \
                   "<br>"\
                   "<ol> {} </ol>"\
                   "Kind Regards".format(str_url)
            sender = rec.create_uid.partner_id.email
            if sender and mail_user_list:
                mail_values = {
                    'model': 'approval.model',
                    'res_id': rec.id,
                    'subject': subject,
                    'body_html': body,
                    'email_from': sender,
                    'email_to': ", ".join(mail_user_list),
                    'reply_to': sender,
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()
        _logger.info("Cron job run!!!")
