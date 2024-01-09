# -*- coding: utf-8 -*-
{
    'name': "feed_crm",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'project', 'hr', 'contacts', 'account', 'hr_expense','sale_crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/job_order_wizard.xml',
        'wizard/reject_comment.xml',
        # 'data/project_task.xml',
        'views/account.xml',
        'views/field.xml',
        'views/proposal.xml',
        'views/client_quote.xml',
        'views/customer.xml',
        'views/industry_type.xml',
        'data/industry_data.xml',
        'views/lead_view.xml',
        'views/views.xml',
        'views/crm_view.xml',
        'views/job_order.xml',
        'views/feed_project.xml',
        'views/expense.xml',
        'views/templates.xml',
        'security/field_groups.xml',
        'security/expense_groups.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets':
        { 'web.assets_frontend': ['feed_crm/static/src/js/expense.js' ] }
}
