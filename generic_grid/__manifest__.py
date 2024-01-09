# -*- coding: utf-8 -*-
##############################################################################
#
#       Odoo Proprietary License v1.0
#
#       This software and associated files (the "Software") may only be used (executed,
#       modified, executed after modifications) if you have purchased a valid license
#       from the authors, typically via Odoo Apps, or if you have received a written
#       agreement from the authors of the Software (see the COPYRIGHT file).
#
#       You may develop Odoo modules that use the Software as a library (typically
#       by depending on it, importing it and using its resources), but without copying
#       any source code or material from the Software. You may distribute those
#       modules under the license of your choice, provided that this license is
#       compatible with the terms of the Odoo Proprietary License (For example:
#       LGPL, MIT, or proprietary licenses similar to this one).
#
#       It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#       or modified copies of the Software.
#
#       The above copyright notice and this permission notice must be included in all
#       copies or substantial portions of the Software.
#
#       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#       IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#       FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT.
#       IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#       DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#       ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#       DEALINGS IN THE SOFTWARE.
#
##############################################################################

{
    'name': "Grid View",
    'summary': "Grid view feature enabled for the modules",
    'description': """Currently, the grid view is available in the enterprise 
                      edition. In this module, we have fully implemented a Grid 
                      view in the community edition with backend & UI""",
    'version': '16.0.1.0.0',
    'website': 'https://www.surekhatech.com',
    'author': 'Surekha Technologies Pvt. Ltd',
    'company': 'Surekha Technologies Pvt Ltd',
    'maintainer': 'Surekha Technologies Pvt Ltd',
    'category': 'Tools',
    'depends': ['web'],
    'sequence': 1,
    'images': ['static/description/Grid-View.png'],
    'license': 'Other proprietary',
    'price': 24.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            '/generic_grid/static/src/css/grid_view.css',
            'generic_grid/static/lib/snabbdom-0.5.0/snabbdom.js',
            'generic_grid/static/src/js/grid_view.js',
            'generic_grid/static/src/js/grid_model.js',
            'generic_grid/static/src/js/grid_controller.js',
            'generic_grid/static/src/js/grid_renderer.js',
            'generic_grid/static/src/xml/grid_view.xml',
        ],

    },
}
