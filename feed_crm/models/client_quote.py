from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ClientQuote(models.Model):
    _name = "feed.client.quote"

    _rec_name = 'module'

    item = fields.Char(string='Items')
    module = fields.Many2one('field.module', string='Module')

    detail = fields.Char(string='Details')
    type = fields.Selection(
        [('quantitative', 'Quantitative'), ('qualitative', 'Qualitative'), ('other', 'Other')], string='Type')
    cost = fields.Float(string='Cost')
    currency = fields.Many2one("res.currency", string='Currency')
    margin = fields.Float(string='Margin%')
    client_quote = fields.Float(string='Total Cost', compute='_compute_client_quote', store=True)
    crm_id = fields.Many2one('crm.lead', string='Crm')
    project_id = fields.Many2one('project.project', string='Project')
    field_line_id = fields.Many2one("feed.crm.field", string='Field Line')

    @api.depends('cost', 'margin')
    def _compute_client_quote(self):
        for rec in self:
            rec.client_quote = rec.cost + (rec.cost * (rec.margin / 100))
