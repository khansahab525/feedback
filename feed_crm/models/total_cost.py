from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class TotalCost(models.Model):
    _name = "feed.total.cost"

    _rec_name = 'module'

    module = fields.Many2one('field.module', string='Module')

    cost = fields.Float(string='Cost')
    currency = fields.Many2one("res.currency", string='Currency')
    multiplier = fields.Float(string='Multiplier', default=1.00)
    cost = fields.Float()
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    crm_id = fields.Many2one('crm.lead', string='Crm')
    project_id = fields.Many2one('project.project', string='Project')
    field_line_id = fields.Many2one("feed.crm.field", string='Field Line')
    type = fields.Selection(
        [('quantitative', 'Quantitative'), ('qualitative', 'Qualitative'), ('other', 'Other')], string='Type')

    @api.depends('cost', 'multiplier')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.cost * rec.multiplier
