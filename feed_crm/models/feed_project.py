# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError


class Feedproject(models.Model):
    _inherit = 'project.project'

    project_number = fields.Char(string='Project Number', required=True,
                                 readonly=True, default=lambda self: _('New'))

    crm_id = fields.Many2one('crm.lead', string='Crm')
    project_code = fields.Char(string='Project Code', required=False)
    team_ids = fields.Many2many('res.users', string='Team')

    timeline = fields.Datetime(string='Time Line')
    project_type = fields.Selection([('research', 'Research'), ('internal', 'Internal'), ('other', 'Other')])
    stage_timeline = fields.One2many('stage.timeline.line', 'project_id')

    # RFP
    rfp_number = fields.Char(string='RFP Number (Client)', tracking=True)
    prop_submission_dline = fields.Datetime(string='Proposal Submission Deadline', tracking=True)
    inquiry_deadline = fields.Datetime(string='Inquiry Deadline', tracking=True)
    inquiry_email = fields.Char(string='Inquiry Email', tracking=True)
    company_id = fields.Many2one('res.company', string='Which Company', tracking=True)
    # email = fields.Char(string='Inquiry Email', tracking=True)
    job_number = fields.Char(string='Job Number Internal', tracking=True, readonly=True)
    submission_mode = fields.Selection(
        [('email', 'Email'), ('portal', 'Portal'), ('in_person', 'In-Person'), ('mail', 'Mail')],
        string='Submission Mode', tracking=True, default="email")
    finance_email = fields.Char(string='Associated Finance Email', tracking=True)
    submission_format = fields.Selection([('pdf', 'PDF'), ('print', 'Print'), ('usb', 'USB')],
                                         string='Submission Format', tracking=True, default="pdf")
    tender = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Tender Bond', tracking=True, default="yes",
                              widget='radio')
    method = fields.Char(string='Method', tracking=True)
    release_date = fields.Date(string='Release Date', tracking=True)
    deadline = fields.Datetime(string='Deadline', tracking=True)
    amount = fields.Float(string='Amount', tracking=True)
    rfp_currency = fields.Many2one("res.currency", string='Currency')
    tender_desc = fields.Text(string='Details')

    performance_bond = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Performance Bond', default='no')
    performance_method = fields.Char(string='Method', tracking=True)
    performance_release_date = fields.Date(string='Release Date', tracking=True)
    performance_amount = fields.Float(string='Amount', tracking=True)
    performance_rfp_currency = fields.Many2one("res.currency", string='Currency')
    performance_bond_desc = fields.Text(string="Performance Bond Details")
    scope_of_work = fields.Text(string='Scope of Work', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Project Leader', tracking=True)
    proposal_writer = fields.Many2one('hr.employee', string='Proposal Writer', tracking=True)
    attachment_id = fields.Many2many('ir.attachment', string="Attachment", required=True)

    field_line = fields.One2many('feed.crm.field', 'project_id')
    total_cost = fields.One2many('feed.total.cost', 'project_id')
    client_quote = fields.One2many('feed.client.quote', 'project_id')
    feed_invoice_line = fields.One2many('feed.schedule.invoices', 'project_id', readonly=False)

    total_cost_margin = fields.Float(string='Total Cost Margin', store=True)
    total_cost_margin_per = fields.Char(string='Total Cost Margin %', store=True, readonly=True)

    def btn_create_job_order(self):
        vals = context = {
            'project_id': self.id,
            'name': self.name,
            'p_number': self.project_code,
            'job_leader': self.user_id.id,
            'project_id': self.id,
            'type': [],

        }
        create_jo = self.env['feed.job.order'].create(vals)
        return True


        # job_order = self.env['feed.job.order'].search([('project_id', '=', self.id)])
        # context = {
        #     'default_project_id': self.id,
        #     'default_name': self.name,
        #     'default_p_number': self.project_code,
        #     'default_job_leader': self.user_id.id,
        #
        # }
        # return {
        #     'name': _('Job Order'),
        #     'view_type': 'tree',
        #     'view_mode': 'tree,form',
        #     'res_model': 'feed.job.order',
        #     'view_id': False,
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        #     'domain': [('id', 'in', job_order.ids)],
        #     'context': context,
        # }

    def action_view_project_job_order(self):
        job_order = self.env['feed.job.order'].search([('project_id', '=', self.id)])
        return {
            'name': _('Job Order'),
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'feed.job.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', job_order.ids)],
            'context': {'create': False},
            # 'flags': {'initial_mode': 'view'}
        }

    def send_email_to_team(self):
        for record in self:
            # Get the email addresses of the recipients from the record fields
            recipients = record.team_ids
            if recipients:
                recipients_list = [usr for usr in recipients]
                # recipients_list.append(self.env.user)
                # recipients.append(self.env.user.email)
                for recipient in recipients_list:
                    name = recipient.name
                    project_name = record.name
                    email_body = """<html>
                            <div style='margin: 0px; padding: 0px;'>
                                <p>Hello <b>{}</b></p>
                                <p>Project <b>{}</b> is assigned to you. Thank you</p>
                                <p>Best regards,</p>
                                <p>Odoo S.A.</p>
                            </div>
                        </html>""".format(name, project_name)

                    mail = self.env['mail.mail'].create({
                        'subject': 'Crm Project',
                        'body_html': email_body,
                        'email_from': 'zubairali12292@gmail.com',
                        'email_to': recipient.email,
                        # 'attachment_ids': [(6, 0, template.attachment_ids.ids)],
                    })
                    # Send the email immediately
                    mail.send()
                if self.env.user.email:
                    recipients_name_li = [user.name for user in recipients_list]
                    recipients_name = ', '.join(recipients_name_li)
                    name = self.env.user.name
                    project_name = record.name
                    email_body = """<html>
                            <div style='margin: 0px; padding: 0px;'>
                                <p>Hello <b>{}</b></p>
                                <p>You have assign project <b>{}</b> to <b>{}</b>. Thank you</p>
                                <p>Best regards,</p>
                                <p>Odoo S.A.</p>
                            </div>
                        </html>""".format(name, project_name, recipients_name)

                    mail = self.env['mail.mail'].create({
                        'subject': 'Crm Project',
                        'body_html': email_body,
                        'email_from': 'zubairali12292@gmail.com',
                        'email_to': self.env.user.email,
                        # 'attachment_ids': [(6, 0, template.attachment_ids.ids)],
                    })
                    # Send the email immediately
                    mail.send()

    @api.model
    def create(self, vals):

        # Perform operations before creating the record
        if vals.get('project_type') in ('research','other'):
            if vals.get('crm_id') and vals.get('partner_id'):
                vals['project_code'] = self.env['ir.sequence'].next_by_code('project.code.seq')
                partner_code = self.env['res.partner'].browse(vals.get('partner_id')).partner_code
                if partner_code:
                    current_year = datetime.datetime.now().year
                    year_str = str(current_year)
                else:
                    raise UserError(_("You have not set a code for the customer"))
            else:
                raise UserError(_("You have not selected a customer OR CRM"))

        res = super(Feedproject, self).create(vals)
        if res.project_code:
            res.crm_id.job_number = self.env.company.name + '/' + year_str + '/' + vals['project_code'] + '/' + partner_code


        res.send_email_to_team()
        crm_id = res.crm_id
        if res.crm_id:
            res.update({
                'field_line': [(6, 0, crm_id.field_line.ids)],
                'client_quote': [(6, 0, crm_id.client_quote.ids)],
                'total_cost': [(6, 0, crm_id.total_cost.ids)],
                'feed_invoice_line': [(6, 0, crm_id.feed_invoice_line.ids)],
                'rfp_number': crm_id.rfp_number,
                'company_id': crm_id.company_id.id,
                'job_number': crm_id.job_number,
                'attachment_id': crm_id.attachment_id.ids,
                'prop_submission_dline': crm_id.prop_submission_dline,
                'scope_of_work': crm_id.scope_of_work,
                'submission_mode': crm_id.submission_mode,
                'submission_format': crm_id.submission_format,
                'finance_email': crm_id.finance_email,
                'employee_id': crm_id.employee_id.id,
                'proposal_writer': crm_id.proposal_writer,
                'inquiry_deadline': crm_id.inquiry_deadline,
                'inquiry_email': crm_id.inquiry_email,
                'tender': crm_id.tender,
                'performance_bond': crm_id.performance_bond,
                'method': crm_id.method,
                'release_date': crm_id.release_date,
                'amount': crm_id.amount,
                'rfp_currency': crm_id.rfp_currency,
                'tender_desc': crm_id.tender_desc,
                'performance_method': crm_id.performance_method,
                'performance_release_date': crm_id.performance_release_date,
                'performance_amount': crm_id.performance_amount,
                'performance_rfp_currency': crm_id.performance_rfp_currency,
                'performance_bond_desc': crm_id.performance_bond_desc,

            })

        return res


class StageTimeline(models.Model):
    _name = "stage.timeline.line"

    name = fields.Many2one('project.project.stage', string='Stage')
    timeline = fields.Datetime(string='Time Line')
    project_id = fields.Many2one('project.project')
