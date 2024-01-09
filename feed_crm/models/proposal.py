from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Proposal(models.Model):
    _name = "feed.proposal"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    attachment_id = fields.Many2many('ir.attachment', string="Attachment", required=True)
    feedback = fields.Text(string='Manager Feedback')
    finance_feedback = fields.Text(string='Research Feedback')
    crm_id = fields.Many2one('crm.lead', string='Opportunity')
    follow_up_date = fields.Date(string='Follow Up Date', required=True, index=True,
                                 default=fields.Date.context_today)
    client_decision_date = fields.Date(string='Client Decision Date', required=True, index=True,
                                       default=fields.Date.context_today)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('manager_approval', 'Manager Approval'),
            ('research_approval', 'Research Approval'),
            ('approved', 'Approved'),
            ('for_review', 'For Review'),
            ('sent_to_client', 'Sent to Client')

        ],
        string='Status',
        required=True,
        readonly=False,
        copy=False,
        tracking=True,
        default='draft', )

    def unlink(self):
        for record in self:
            # Check if the record is in the "approve" state (adjust field and state as needed)
            if record.state != 'draft':
                raise ValidationError("You can delete records only in 'Draft' state.")

        return super(Proposal, self).unlink()

    def btn_change_to_manager_approval(self):
        self.write({'state': 'manager_approval'})

    def btn_manager_approved(self):
        self.write({'state': 'research_approval'})

    def btn_research_return_back(self):
        self.write({'state': 'for_review'})

    def btn_research_approved(self):
        self.write({'state': 'approved'})

    def btn_manager_return_back(self):
        self.write({'state': 'for_review'})

    def btn_change_from_review(self):
        self.write({'state': 'manager_approval'})

    def btn_sent_to_client(self):
        self.write({'state': 'sent_to_client'})

    def btn_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_view_crm_record(self):
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'res_id': self.crm_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
