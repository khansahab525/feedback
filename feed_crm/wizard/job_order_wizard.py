# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobOrderWizard(models.TransientModel):
    _name = 'job.order.wizard'

    name = fields.Char(string='Project Name')
    p_number = fields.Char(string='Project Number')
    job_leader = fields.Many2one('hr.employee', string='Send By')
    assign_to = fields.Many2one('res.users', string='Assign To', readonly=True)
    type = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    date_submitted_to_field = fields.Date(string='Date Submitted To Field')
    methodology = fields.Many2many('field.methodology', string='Methodology')
    sample_size = fields.Char(string='Sample Size')
    quota = fields.Char(string='Quota')
    location = fields.Char(string='Location')

    def create_job_order(self):
        pass