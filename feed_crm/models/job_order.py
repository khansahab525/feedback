
from odoo import api, fields, models, _


class JobOrder(models.Model):
    _name = "feed.job.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Project Name',readonly=True)
    p_number = fields.Char(string='Project Number', readonly=True)
    job_leader = fields.Many2one('res.users', string='Send By', readonly=True)
    assign_to = fields.Many2one('res.users', string='Assign To', readonly=False)

    project_id = fields.Many2one('project.project', string='Project', readonly=1)
    type = fields.Selection([('quantitative','Quantitative'),('qualitative','Qualitative')])
    project_brief = fields.Text(string='Project Brief')
    date_submitted_to_field = fields.Date(string='Date Submitted To Field',default=fields.Date.context_today)
    methodology = fields.Many2many('field.methodology', string='Methodology')
    sample_size = fields.Char(string='Sample Size')
    quota = fields.Char(string='Quota')
    location = fields.Char(string='Location')
    survey_link = fields.Char(string='Survey Link')

    field_team_req = fields.Text(string='Field Team Requirement')
    data_processing_req = fields.Text(string='Data Processing Requirement')
    quality_control = fields.Text(string='Quality Control Requiremen')




    field_team_requirement = fields.One2many('field.team.requirement', 'job_order')
    data_processing_requirement = fields.One2many('data.processing.requirement', 'job_order')
    quality_control_requirement = fields.One2many('quality.control.requirement', 'job_order')
    fieldwork_schedule = fields.One2many('fieldwork.schedule', 'job_order')

    def btn_create_job_order(self):
        pass



class FieldTeamRequirement(models.Model):
    _name = "field.team.requirement"

    job_order = fields.Many2one('feed.job.order')
    name = fields.Text(string='Requirements')
    key_notes = fields.Text(string='Keynotes')

class DataProcessingRequirement(models.Model):
    _name = "data.processing.requirement"

    job_order = fields.Many2one('feed.job.order')
    name = fields.Text(string='Requirements')
    key_notes = fields.Text(string='Keynotes')

class QualityControlRequirement(models.Model):
    _name = "quality.control.requirement"

    job_order = fields.Many2one('feed.job.order')
    name = fields.Text(string='Requirements')
    key_notes = fields.Text(string='Keynotes')

class FieldworkSchedule(models.Model):
    _name = "fieldwork.schedule"

    job_order = fields.Many2one('feed.job.order')
    name = fields.Text(string='Fieldwork Schedule')
    date = fields.Date(string='Date',default=fields.Date.context_today)






