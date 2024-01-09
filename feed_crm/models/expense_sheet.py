from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context
from odoo.tools import float_is_zero


class FeedInheritExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('qc_manager', 'QC Manager'),
        ('commercial_director', 'Commercial Director'),
        ('finance_manager', 'Finance Manager'),
        ('approve', 'Manager'),
        ('post', 'Posted'),
        ('done', 'Done'),
        ('cancel', 'Refused')], string='Status', index=True, readonly=True, tracking=True, copy=False, default='draft',
        required=True)

    freelancer_visible_state = fields.Selection(
        [('draft', 'To Submit'), ('submit', 'Manager Approval'),
         ('qc_manager', 'QC Manager'),
         ('commercial_director', 'Commercial Director'),
         ('finance_manager', 'Finance Manager'),
         ('approve', 'Approved'),
         ('post', 'Posted'),
         ('done', 'Done'),
         ('cancel', 'Refused')], default='draft')

    other_visible_state = fields.Selection([('draft', 'To Submit'), ('submit', 'Direct Manger'),
                                            ('finance_manager', 'Finance Manager'),
                                            ('approve', 'Approved'),
                                            ('post', 'Posted'),
                                            ('done', 'Done'),
                                            ('cancel', 'Refused')], default='draft')

    def field_manager_approve_expense_sheets(self):
        if self.payment_mode == 'freelancer':
            self.write({'state': 'qc_manager'})
            self.write({'freelancer_visible_state': 'qc_manager'})
        else:
            self.write({'state': 'finance_manager'})
            self.write({'other_visible_state': 'finance_manager'})

    def field_manager_reject_expense_sheets(self):
        if self.payment_mode == 'freelancer':
            self.write({'state': 'cancel'})
            self.write({'freelancer_visible_state': 'cancel'})
        else:
            self.write({'state': 'cancel'})
            self.write({'other_visible_state': 'cancel'})

    def qc_manager_approve_expense_sheets(self):
        self.write({'state': 'commercial_director'})
        if self.payment_mode == 'freelancer':
            self.write({'freelancer_visible_state': 'commercial_director'})
        else:
            self.write({'other_visible_state': 'commercial_director'})

    def qc_manager_reject_expense_sheets(self):
        if self.payment_mode == 'freelancer':
            self.write({'state': 'cancel'})
            self.write({'freelancer_visible_state': 'cancel'})
        else:
            self.write({'state': 'cancel'})
            self.write({'other_visible_state': 'cancel'})

    def commercial_director_approve_expense_sheets(self):
        self.write({'state': 'finance_manager'})
        if self.payment_mode == 'freelancer':
            self.write({'freelancer_visible_state': 'finance_manager'})
        else:
            self.write({'other_visible_state': 'finance_manager'})

    def commercial_director_reject_expense_sheets(self):
        if self.payment_mode == 'freelancer':
            self.write({'state': 'cancel'})
            self.write({'freelancer_visible_state': 'cancel'})
        else:
            self.write({'state': 'cancel'})
            self.write({'other_visible_state': 'cancel'})

    def reset_expense_sheets(self):
        res = super(FeedInheritExpenseSheet, self).reset_expense_sheets()
        if self.payment_mode == 'freelancer':
            self.write({'freelancer_visible_state': 'draft'})
        else:
            self.write({'other_visible_state': 'draft'})
        return res

    # def approve_expense_sheets(self):
    #     res = super(FeedInheritExpenseSheet, self).approve_expense_sheets()
    #
    #     return res

    def _do_create_moves(self):
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        skip_context = {
            'skip_invoice_synce': True,
            'skip_invoice_line_sync': True,
            'skip_account_move_synchronization': True,
            'check_move_validity': False,
        }
        # MY CUSTOM ADDED CODE
        freelancer_sheets = self.filtered(lambda sheet: sheet.payment_mode == 'freelancer')
        if freelancer_sheets:
            moves = self.env['account.move'].create([sheet._prepare_bill_vals() for sheet in freelancer_sheets])

            moves.action_post()
            self.activity_update()
        else:
            moves = super(FeedInheritExpenseSheet, self)._do_create_moves()

        return moves

    def action_sheet_move_create(self):
        if self.payment_mode == 'freelancer':
            samples = self.mapped('expense_line_ids.sample')
            if samples.count(True):
                if samples.count(False):
                    raise UserError(_("You can't mix sample expenses and regular ones"))
                self.write({'state': 'post'})
                return

            if any(sheet.state != 'approve' for sheet in self):
                raise UserError(_("You can only generate accounting entry for approved expense(s)."))

            if any(not sheet.journal_id for sheet in self):
                raise UserError(_("Specify expense journal to generate accounting entries."))

            if not self.employee_id.address_home_id:
                raise UserError(
                    _("The private address of the employee is required to post the expense report. Please add it on the employee form."))

            expense_line_ids = self.mapped('expense_line_ids') \
                .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(
                    r.currency_id or self.env.company.currency_id).rounding))
            res = expense_line_ids.with_context(clean_context(self.env.context)).action_move_create()
            paid_expenses_freelancer = self
            paid_expenses_freelancer.write({'state': 'post'})
            self.activity_update()
        else:
            res = super(FeedInheritExpenseSheet, self).action_sheet_move_create()

        return res

    def action_open_account_move(self):
        if self.payment_mode == 'freelancer':
            self.ensure_one()
            return {
                'name': self.account_move_id.name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [[False, "form"]],
                'res_model': 'account.move',
                'res_id': self.account_move_id.id,
            }
        else:
            return super(FeedInheritExpenseSheet, self).action_open_account_move()

    def _set_visible_state(self, state):
        field_name = 'freelancer_visible_state' if self.payment_mode == 'freelancer' else 'other_visible_state'
        self.write({field_name: state})

    def action_submit_sheet(self):
        res = super(FeedInheritExpenseSheet, self).action_submit_sheet()
        self._set_visible_state('submit')
        return res

    def _do_approve(self):
        self._check_can_approve()

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no expense reports to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        filtered_sheet = self.filtered(lambda s: s.state in ['finance_manager', 'draft'])
        if not filtered_sheet:
            return notification
        for sheet in filtered_sheet:
            sheet.write({
                'state': 'approve',
                'user_id': sheet.user_id.id or self.env.user.id,
                'approval_date': fields.Date.context_today(sheet),
            })
            sheet._set_visible_state('approve')

        notification['params'].update({
            'title': _('The expense reports were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        self.activity_update()
        return notification

    def refuse_sheet(self, reason):
        res = super(FeedInheritExpenseSheet, self).refuse_sheet(reason)
        self._set_visible_state('cancel')
        return res
