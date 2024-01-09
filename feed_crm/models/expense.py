# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context, format_date
from odoo.tools import float_compare


class FeedInheritExpense(models.Model):
    _inherit = 'hr.expense'

    expense_type = fields.Selection(
        [('employee', 'Employee'), ('project_expense', 'Project Expense'), ('freelancer', 'Freelancer'),
         ('other', 'Other')],
        string='Expense Type', tracking=True, default="project_expense")

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'QC Manager'),
        ('commercial_director', 'Commercial Director'),
        ('finance_manager', 'Finance Manager'),
        ('approved', 'Manager'),
        ('done', 'Done'),
        ('refused', 'Refused')
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True, default='draft')
    freelancer_visible_state = fields.Selection(
        [('draft', 'To Submit'), ('reported', 'QC Manager'),
         ('commercial_director', 'Commercial Director'),
         ('finance_manager', 'Finance Manager'),
         ('approved', 'Approved'),
         ('done', 'Done'),
         ('refused', 'Refused')], default='draft')
    other_visible_state = fields.Selection([('draft', 'To Submit'), ('reported', 'Finance Manager'),
                                            ('approved', 'Approved'),
                                            ('done', 'Done'),
                                            ('refused', 'Refused')], default='draft')
    project_no = fields.Many2one('project.project')
    internal = fields.Boolean(default=True)
    payment_method = fields.Many2one('payment.method', string='Payment Method')
    payment_mode = fields.Selection(
        [("own_account", "Employee (to reimburse)"), ("company_account", "Company"), ("freelancer", "Freelancer")
         ], default='own_account', tracking=True,
        states={'done': [('readonly', True)], 'approved': [('readonly', True)], 'reported': [('readonly', True)]},
        string="Paid By")

    # EXPENSE STATE COMPUTE FUNCTION
    def _set_visible_state(self, state):
        field_name = 'freelancer_visible_state' if self.payment_mode == 'freelancer' else 'other_visible_state'
        self.write({field_name: state})

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'draft':
                expense.state = "draft"
                expense._set_visible_state('draft')

            elif expense.sheet_id.state == "commercial_director":
                expense.state = "commercial_director"
                expense._set_visible_state('commercial_director')
            elif expense.sheet_id.state == "finance_manager":
                expense.state = "finance_manager"
                expense._set_visible_state('reported')

            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
                expense._set_visible_state('refused')
            elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
                expense.state = "approved"
                expense._set_visible_state('approved')
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
                expense._set_visible_state('reported')
            else:
                expense.state = "done"
                expense._set_visible_state('reported')

    # IT PREPARE VALUES FOR EXPENSE SHEET BASED ON SELECTION
    def _get_default_expense_sheet_values(self):
        if self.payment_mode == 'freelancer':
            # If there is an expense with total_amount_company == 0, it means that expense has not been processed by OCR yet
            expenses_with_amount = self.filtered(lambda expense: not float_compare(expense.total_amount_company, 0.0,
                                                                                   precision_rounding=expense.company_currency_id.rounding) == 0)

            if any(expense.state != 'draft' or expense.sheet_id for expense in expenses_with_amount):
                raise UserError(_("You cannot report twice the same line!"))
            if not expenses_with_amount:
                raise UserError(_("You cannot report the expenses without amount!"))
            if len(expenses_with_amount.mapped('employee_id')) != 1:
                raise UserError(_("You cannot report expenses for different employees in the same report."))
            if any(not expense.product_id for expense in expenses_with_amount):
                raise UserError(_("You can not create report without category."))

            # Check if two reports should be created
            own_expenses = expenses_with_amount.filtered(lambda x: x.payment_mode == 'freelancer')
            company_expenses = expenses_with_amount - own_expenses
            create_two_reports = own_expenses and company_expenses

            sheets = [own_expenses, company_expenses] if create_two_reports else [expenses_with_amount]
            values = []
            for todo in sheets:
                if len(todo) == 1:
                    expense_name = todo.name
                else:
                    dates = todo.mapped('date')
                    min_date = format_date(self.env, min(dates))
                    max_date = format_date(self.env, max(dates))
                    expense_name = min_date if max_date == min_date else "%s - %s" % (min_date, max_date)

                vals = {
                    'company_id': self.company_id.id,
                    'employee_id': self[0].employee_id.id,
                    'name': expense_name,
                    'expense_line_ids': [Command.set(todo.ids)],
                    'state': 'draft',
                }
                values.append(vals)
            return values
        else:
            return super(FeedInheritExpense, self)._get_default_expense_sheet_values()


class PaymentMethod(models.Model):
    _name = 'payment.method'

    name = fields.Char(string="Name")
