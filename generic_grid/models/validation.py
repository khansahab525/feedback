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
#       FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#       IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#       DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#       ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#       DEALINGS IN THE SOFTWARE.
#
##############################################################################
"""Initialize required modules """

import logging
import os

from lxml import etree
from odoo import tools
from odoo.loglevels import ustr
from odoo.tools import misc, view_validation

_logger = logging.getLogger(__name__)

_GridValidator = None


@view_validation.validate('grid')
def schema_grid(arch, **kwargs):
    """ Check the grid view against its schema
    :type arch: etree._Element
    """
    global _GridValidator

    if _GridValidator is None:
        with tools.file_open(os.path.join('generic_grid', 'views', 'grid.rng')) as f:
            _GridValidator = etree.RelaxNG(etree.parse(f))

    if _GridValidator.validate(arch):
        return True

    for error in _GridValidator.error_log:
        _logger.error(ustr(error))
    return False


@view_validation.validate('grid')
def valid_field_types(arch, **kwargs):
    """ Each of the row, col and measure <field>s must appear once and only
    once in a grid view
    :type arch: etree._Element
    """
    types = {'col', 'measure'}
    for f in arch.iterdescendants('field'):
        field_type = f.get('type')
        if field_type == 'row':
            continue

        if field_type in types:
            types.remove(field_type)
        else:
            return False

    return True
