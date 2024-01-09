# -*- coding: utf-8 -*-


from odoo import models, fields, _


class FeedHrEmployee(models.Model):
    _inherit = "hr.employee"

    age = fields.Integer()
    have_children = fields.Boolean('Do you have any children?')
    emergency_person_relation = fields.Char('Relationship to you')
    health_condition = fields.Char('Health Conditions or Allergies')
    passport_expiry_date = fields.Date('Passport Expiry Date')
    visa_status_uae = fields.Char('Visa Status (For UAE)')
    visa_status_ksa = fields.Char('Visa Status (for KSA)')
    work_visa = fields.Char('Work Visa')
    id_expiry_date = fields.Date('ID expiry date')
    market_research_experience = fields.Integer('Market Research Experience', help='How many years of experience do you have in a market research related field?')
    research_experience_since = fields.Date('Research Experience Since')

    whn_feedback_join_date = fields.Date('When did you join feedback?')

    employee_licence = fields.Char('Employee Licence')
    dietary_restrictions = fields.Char('Dietary Restrictions')
    education = fields.Char('Education')
    cv = fields.Binary('CV')
    visa = fields.Binary('Visa')
    id_doc = fields.Binary('ID Doc')
    passport_doc = fields.Binary('Passport Doc')
