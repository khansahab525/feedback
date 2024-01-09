# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Timesheet Grid View',
    'version': '1.0',
    'category': 'Services/Timesheets',
    'sequence': 23,
    'summary': 'Timesheet Grid View',
    'description': """
This module implements a timesheet system.
==========================================
* Timesheet Grid View
    """,
    'website': '',
    'depends': ['hr_timesheet', 'generic_grid'],
    'data': [
        'views/hr_timesheet_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
