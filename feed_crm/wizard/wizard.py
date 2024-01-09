# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectWizard(models.TransientModel):
    _name = 'project.wizard'

    name = fields.Char(string='Name')