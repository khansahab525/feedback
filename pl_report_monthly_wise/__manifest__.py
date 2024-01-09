# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Profit - Loss report moth wise',
    'summary': '',
    'description': """""",

    'author': '',
    'support': '',

    'category': 'account',
    'version': '10',
    'depends': ['account_dynamic_reports'],

    'data': [
        "security/ir.model.access.csv",
        "data/data_financial_report.xml",
        "wizard/pl_month.xml",
        "wizard/pl_analytic_month_wise.xml"
    ],
    'application': False,
    'license': "OPL-1",
}
