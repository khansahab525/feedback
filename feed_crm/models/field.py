from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class FeedCrmField(models.Model):
    _name = "feed.crm.field"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _rec_name = 'module'

    module = fields.Many2one('field.module', string='Module',required=True)
    field_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='yes', string='Field Requirement',required=True)
    type = fields.Selection(
        [('quantitative', 'Quantitative'), ('qualitative', 'Qualitative'), ('other', 'Other')], string='Type')
    details = fields.Text(string='Details')
    currency = fields.Many2one("res.currency", string='Currency')
    sample = fields.Char(string='Sample')
    country = fields.Many2many('res.country', string='Country')
    methodology = fields.Many2one('field.methodology', string='Methodology')
    lead_id = fields.Many2one('crm.lead')
    project_id = fields.Many2one('project.project')
    field_line_ids = fields.One2many('feed.crm.field.line', 'field_id')
    member = fields.Many2one('hr.employee', string='Field Supervisor', tracking=True)
    recruitment = fields.Text(string='Recruitment Timeline')
    recruitment_selection = fields.Selection(
        [('daily', 'Day'), ('week', 'Week')], default="daily")
    field = fields.Text(string='Field Timeline')
    field_selection = fields.Selection(
        [('daily', 'Day'), ('week', 'Week')], default="daily")
    dp_timeline = fields.Text(string='DP Timeline ')
    dp_selection = fields.Selection(
        [('daily', 'Day'), ('week', 'Week')], default="daily")
    research_timeline = fields.Text(string='Research Timeline')
    research_selection = fields.Selection(
        [('daily', 'Day'), ('week', 'Week')], default="daily")
    cost = fields.Float(string='Cost')
    multiplier = fields.Float(string='Multiplier')

    project_revenue = fields.Float(compute='_compute_project_revenue', store=True, string='Project Revenue')
    # For Total Cost Tab
    # multiplier = fields.Float(string='Multiplier')
    module_total_cost = fields.Float(string='Total Cost')


    @api.depends('amount_total', 'multiplier')
    def _compute_project_revenue(self):
        for record in self:
            record.project_revenue = record.amount_total * record.multiplier

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('research_approval', 'Research Approval'),
            ('finance_approval', 'CD Approvel'),
            ('done', 'Done'),
            ('cancel', 'cancel')

        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft', )

    amount_total = fields.Float(compute='_compute_amount_total', store=True, string='Total',readonly=True)
    currency_id = fields.Many2one("res.currency", string='Currency')


    @api.depends('field_line_ids')
    def _compute_amount_total(self):
        for line in self:
            if line.field_line_ids.ids:
                line.amount_total = sum(line.field_line_ids.mapped('total_cost'))

                crm_id = self.env['crm.lead'].search([('id', '=', line.lead_id.id)])

                total_cost_existing_line = crm_id.total_cost.filtered(lambda x: x.field_line_id.id == line.id)
                total_cost_existing_line.cost = line.amount_total
                total_cost_existing_line.currency = line.currency.id

                client_quote_existing_line = crm_id.client_quote.filtered(lambda x: x.field_line_id.id == line.id)
                client_quote_existing_line.currency = total_cost_existing_line.currency.id





    margin = fields.Integer(compute='_compute_field_margin', store=True)

    @api.depends('amount_total', 'project_revenue')
    def _compute_field_margin(self):
        for rec in self:
            if rec.project_revenue and rec.amount_total:
                rec.margin = (rec.amount_total / rec.project_revenue) * 100

    def send_to_finance_approval(self):
        if self.field_line_ids:
            self.write({'state': 'finance_approval'})
        else:
            raise UserError("Please add lines before submit to approve")


    def send_to_research_approval(self):
        self.write({'state': 'research_approval'})

    def research_approved(self):
        self.write({'state': 'finance_approval'})

    def research_reject(self):
        # self.write({'state': 'cancel'})
        return {
            'name': _('Comment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reject.comment.wizard',
            # 'res_id': self.lead_id.id,
            'view_id': False,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def cd_approved(self):
        self.write({'state': 'done'})

    def cd_reject(self):
        self.write({'state': 'cancel'})

    def reset_to_draft(self):
        self.write({'state': 'draft'})


    def unlink(self):
        for record in self:
            # Check if the record is in the "approve" state (adjust field and state as needed)
            if record.state != 'draft':
                raise ValidationError("You can delete records only in 'Draft' state.")

        return super(FeedCrmField, self).unlink()

    def action_view_crm_record(self):
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    @api.onchange('field_line_ids','field_line_ids.product_id')
    def onchange_field_line_ids(self):
        for line in self.field_line_ids:
            line.currency = self.currency.id

class FeedCrmFieldLine(models.Model):
    _name = "feed.crm.field.line"

    field_id = fields.Many2one('feed.crm.field')
    product_id = fields.Many2one('product.product')
    product_desc = fields.Text(string='Details')
    cost_for_unit = fields.Float(compute='_compute_price_unit', readonly=False, store=True, string='Cost for Unit')
    quantity = fields.Float(string='Sample/Frequency')
    total_cost = fields.Float(string='Total Cost', compute='_total_cost')
    currency = fields.Many2one("res.currency", string='Currency')

    @api.depends('product_id')
    def _compute_price_unit(self):
        for line in self:
            line.cost_for_unit = line.product_id.list_price



    @api.depends('cost_for_unit', 'quantity')
    def _total_cost(self):
        for record in self:
            record.total_cost = record.cost_for_unit * record.quantity

class FieldModule(models.Model):
    _name = "field.module"

    name = fields.Char(string='Name')


class FieldMethodology(models.Model):
    _name = "field.methodology"

    name = fields.Char(string='Name')
