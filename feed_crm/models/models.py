# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FeedCrm(models.Model):
    _inherit = 'crm.lead'

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




    employee_id = fields.Many2one('hr.employee', string='Project Leader', tracking=True)
    proposal_writer = fields.Many2one('hr.employee', string='Proposal Writer', tracking=True)
    attachment_id = fields.Many2many('ir.attachment', string="Attachment", required=True)
    # documents_require = fields.Many2many('ir.attachment', string="Documents Require")
    # performance_bond = fields.Selection([('no','No'),('yes','Yes')],string='Performance Bond')


    scope_of_work = fields.Text(string='Scope of Work', tracking=True)

    # crm_compute_state = fields.Char(string='State',compute='_compute_crm_state', store=True)
    crm_state = fields.Char(string='State', default='expression_of_interest', store=True)

    lead_no = fields.Char(string='Lead Number', required=True,
                          readonly=True, default=lambda self: _('Lead no'))
    lead_date = fields.Datetime(string='Lead Generated Date',default=lambda self: fields.Datetime.now())


    industry = fields.Selection(
        [('financial_services', 'Financial Services'), ('gp_and_ss', 'Government, Public  and Social Services'),
         ('consumer', 'Consumer'), ('er_and industrials', 'Energy Resources and Industrials'),
         ('ls_and_healthcare', 'Life Sciences and Healthcare'), ('tm_and_telecom', 'Technology, Media and Telecom'),
         ('business_data_services', 'Business/Data Services')])

    industry_type = fields.Many2one('feed.industry', string='Industry Type',domain="[('industry_type', '=', industry)]")
    field_line = fields.One2many('feed.crm.field', 'lead_id')
    client_quote = fields.One2many('feed.client.quote', 'crm_id')
    total_cost = fields.One2many('feed.total.cost', 'crm_id')
    feed_invoice_line = fields.One2many('feed.schedule.invoices', 'crm_line', readonly=False)
    is_invoice_schedule = fields.Selection([('no', 'No'), ('yes', 'Yes')], string='Schedule Invoice', tracking=True,
                                         default="no",
                                         widget='radio')

    is_field_required = fields.Selection([('no', 'No'),('yes', 'Yes')], string='Field Required', tracking=True, default="no",
                              widget='radio')


    project_id = fields.Many2one('project.project', string='Project Id')

    field_count = fields.Integer(string='Project Modules',compute='_compute_field_count', store=True)
    client_quote_count = fields.Integer(string='Client Quote',compute='_compute_client_quote_count', store=True)
    proposal_count = fields.Integer(string='Proposal',compute='_compute_proposal_count', store=True)
    proposal_line_ids = fields.One2many('feed.proposal', 'crm_id', string='Proposals Line')
    total_cost_margin = fields.Float(string='Total Cost Margin', compute='_compute_total_cost_margin', store=True)
    total_cost_margin_per = fields.Char(string='Total Cost Margin %', store=True, readonly=True)
    @api.depends('client_quote','client_quote.cost','client_quote.client_quote')
    def _compute_total_cost_margin(self):
        for rec in self:
            if rec.client_quote and sum(rec.client_quote.mapped('cost')) > 0:

                res = (sum(rec.client_quote.mapped('client_quote'))  - sum(rec.client_quote.mapped('cost'))) / sum(rec.client_quote.mapped('cost'))
                rec.total_cost_margin = res*100
                rec.total_cost_margin_per = str(int(res*100))



    partner_id = fields.Many2one(
        'res.partner', string='Client', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    @api.depends('field_line')
    def _compute_field_count(self):
        for rec in self:
            line = [rec.id for rec in rec.field_line if rec.field_required == 'yes']
            rec.field_count = len(line)

    @api.depends('client_quote')
    def _compute_client_quote_count(self):
        for rec in self:
            # line = [rec.id for rec in rec.client_quote]
            rec.client_quote_count = len(rec.client_quote.ids)

            # rec.update({'total_cost': [(5, 0, 0)]})  # Remove all existing lines in client_quote

    @api.depends('proposal_line_ids')
    def _compute_proposal_count(self):
        for record in self:
            record.proposal_count = len(record.proposal_line_ids)


    @api.model
    def create(self, vals):

        vals['lead_no'] = self.env['ir.sequence'].next_by_code('feed.lead.seq')

        record = super(FeedCrm, self).create(vals)

        total_cost_vals = []
        for field in record.field_line:
            new_line_vals = {
                'module': field.module.id,
                'type': field.type,
                'cost': field.amount_total,
                'field_line_id': field.id,
                'currency': field.currency.id
            }
            total_cost_vals.append((0, 0, new_line_vals))
        record.write({'total_cost': total_cost_vals})
        # record.write({'client_quote': total_cost_vals})

        return record

    def write(self, vals):
        result = super(FeedCrm, self).write(vals)

        # if any(field in vals for field in ['module', 'type', 'cost']):
        if 'field_line' in vals:
            # Handle updates to 'module', 'type', or 'cost'
            total_cost_vals = []

            for field_line in self.field_line:
                existing_line = self.total_cost.filtered(lambda x: x.field_line_id.id == field_line.id)
                if existing_line:
                    # Update existing line
                    existing_line.write({
                        'module': field_line.module.id,
                        'type': field_line.type,
                        'cost': field_line.amount_total,
                        'currency': field_line.currency.id
                    })
                else:
                    # Create new line
                    new_line_vals = {
                        'module': field_line.module.id,
                        'type': field_line.type,
                        'cost': field_line.amount_total,
                        'field_line_id': field_line.id,
                        'currency': field_line.currency.id
                    }
                    total_cost_vals.append((0, 0, new_line_vals))

            if total_cost_vals:
                self.write({'total_cost': total_cost_vals})

        client_quote_vals = []
        for cost_rec in self.total_cost:
            existing_line = self.client_quote.filtered(lambda x: x.field_line_id.id == cost_rec.field_line_id.id)
            if existing_line:
                # Update existing line
                existing_line.write({
                    'module': cost_rec.module.id,
                    'type': cost_rec.type,
                    'cost': cost_rec.total_cost,
                    'currency': cost_rec.currency.id
                })

            else:
                # Create new line
                new_line_vals = {
                    'module': cost_rec.module.id,
                    'type': cost_rec.type,
                    'cost': cost_rec.cost,
                    'field_line_id': cost_rec.field_line_id.id,
                    'currency': cost_rec.currency.id
                }
                client_quote_vals.append((0, 0, new_line_vals))

        if client_quote_vals:
            self.write({'client_quote': client_quote_vals})


        return result

    def action_create_new_project(self):
        if self._name == 'crm.lead':
            ctx = {'default_crm_id': self.id,
                   'default_partner_id': self.partner_id.id,

                   }

        action = self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all")
        action['view_mode'] = 'form'
        action['views'] = [(False, 'form')]
        action['target'] = 'new'
        action['context'] = ctx

        return action

    def action_view_project_quotation(self):
        list = []
        context = dict(self._context or {})
        project_ids = self.env['project.project'].search([('crm_id', '=', self.id)])
        for project in project_ids:
            list.append(project.id)
        return {
            'name': _('Project'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', list)],
            'context': context,
        }
    def action_view_field_requirement(self):
        return {
            'name': _('Project Module'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'feed.crm.field',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.field_line.ids),('field_required','=','yes')],
            # 'context': context,
        }
    def action_view_client_quote(self):
        return {
            'name': _('Client Quote'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'feed.client.quote',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.client_quote.ids)],
            # 'context': context,
        }

    def action_view_proposal(self):
        return {
            'name': _('Review Proposal'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'feed.proposal',
            'view_id': False,
            'type': 'ir.actions.act_window',
            # 'domain': [('id', 'in', self.field_line.ids), ('field_required', '=', 'yes')],
            'context': {'default_crm_id': self.id},
        }



        #
        # self.ensure_one()
        # action = self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all")
        # action['views'] = [(self.env.ref('project.edit_project').id, 'form')]
        # action['domain'] = [('crm_id', '=', self.id)]
        # # action['res_id'] = self.project_id.id
        # return action

    # @api.model
    # def create(self, vals):
    #     vals['job_number'] = self.env['ir.sequence'].next_by_code(
    #         'crm.lead.seq') or _('New')
    #     res = super(FeedCrm, self).create(vals)
    #
    #     return res


class FeedCrmStage(models.Model):
    _inherit = 'crm.stage'

    code = fields.Char(string='Code', tracking=True)

class FeedIndustry(models.Model):
    _name = 'feed.industry'

    name = fields.Char(string='Name')
    industry_type = fields.Selection(
        [('financial_services', 'Financial Services'), ('gp_and_ss', 'Government, Public  and Social Services'),
         ('consumer', 'Consumer'), ('er_and_industrials', 'Energy Resources and Industrials'),
         ('ls_and_healthcare', 'Life Sciences and Healthcare'), ('tm_and_telecom', 'Technology, Media and Telecom'),
         ('business_data_services', 'Business/Data Services')])

class FeedScheduleInvoies(models.Model):
    _name = 'feed.schedule.invoices'

    name = fields.Char()
    crm_line = fields.Many2one('crm.lead')
    project_id = fields.Many2one('project.project', string='Project')
    project_name = fields.Char(string='Project Name')
    milestone = fields.Char(string='Milestone')
    percentage = fields.Char(string='Percentage %')
    invoice_amount = fields.Float('Invoice Amount')

