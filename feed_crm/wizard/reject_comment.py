# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import format_date


class RejectCommentWizard(models.TransientModel):
    _name = 'reject.comment.wizard'

    name = fields.Char(string='Comment')

    def btn_reject_comment(self):
        self.ensure_one()
        current_opn_record = self.env['feed.crm.field'].browse(self.env.context.get('active_ids'))
        current_opn_record.write({'state': 'cancel'})
        msg = _(self.name)
        current_opn_record.message_post(body=msg)