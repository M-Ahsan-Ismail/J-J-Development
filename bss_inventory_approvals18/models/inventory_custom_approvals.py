from odoo import fields, models, _
from odoo.exceptions import ValidationError,UserError


class StockPicking_TransferReceipts_Approvals(models.Model):
    _inherit = 'stock.picking'
    _description = 'Custom Approvals'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('submit_for_approval', 'Submit For Approval'),
        ('manager_approved', 'Verified'),
        ('ceo_approved', 'Approved'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")


    def submit_for_approval(self):
        for rec in self:
            rec.update({'state': 'submit_for_approval'})

            # Find users with the 'purchase_approval_level1' access right
            group_level1 = self.env.ref(
                'bss_inventory_approvals18.inventory_approval_level1')  # Replace 'your_module' with the correct module name
            level1_users = group_level1.users

            if not level1_users:
                raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

            # Create an activity for all users in the group
            for user in level1_users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,  # ID of the current record
                    'res_model_id': self.env['ir.model']._get_id('stock.picking'),
                    # Replace with your model's technical name
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    # Default 'To Do' activity type
                    'summary': _('1st-Approval Needed'),
                    'note': _('Please verify the Receipt: %s') % rec.name,
                    'user_id': user.id,  # Assign to the user
                    'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                })


    def button_manager_approval(self):
        for rec in self:
            rec.write({'state': 'manager_approved'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'stock.picking'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Receipt has been verified by the {self.env.user.name}."))

                # Find users with the 'purchase_approval_level1' access right
                group_level1 = self.env.ref(
                    'bss_inventory_approvals18.inventory_approval_level2')  # Replace 'your_module' with the correct module name
                level1_users = group_level1.users

                if not level1_users:
                    raise UserError(_("No users are assigned to the 'First-Level Approval' group."))

                # Create an activity for all users in the group
                for user in level1_users:
                    self.env['mail.activity'].create({
                        'res_id': rec.id,  # ID of the current record
                        'res_model_id': self.env['ir.model']._get_id('stock.picking'),
                        # Replace with your model's technical name
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        # Default 'To Do' activity type
                        'summary': _('1st-Approval Needed'),
                        'note': _('Please review and approve the Budget: %s') % rec.name,
                        'user_id': user.id,  # Assign to the user
                        'date_deadline': fields.Date.context_today(self),  # Optional: Add a deadline
                    })

    def button_ceo_approval(self):
        for rec in self:
            rec.write({'state': 'ceo_approved'})

            # Create an activity and mark it as done
            activity = self.env['mail.activity'].search([
                ('res_id', '=', rec.id),  # Link the activity to this order
                ('res_model', '=', 'stock.picking'),  # Replace with your model's technical name
                ('user_id', '=', self.env.uid),  # The current user
                ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id)  # 'To Do' activity type
            ], limit=1)

            if activity:
                activity.action_feedback(feedback=_(f"The Receipt has been Approved by the {self.env.user.name}."))


    def action_confirm(self):
        res = super(StockPicking_TransferReceipts_Approvals,self).action_confirm()
        for rec in self:
            rec.state = 'assigned'
        return res



