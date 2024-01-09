from odoo import api, fields, models, _


class InheritAccountInvoice(models.Model):
    _inherit = "account.move"

    crm_line = fields.Many2one('crm.lead')
    project_name = fields.Char(string='Project Name')
    milestone = fields.Char(string='Milestone')
    percentage = fields.Char(string='Percentage %')