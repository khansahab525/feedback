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

import collections
from dateutil.relativedelta import relativedelta, MO, SU
from functools import partial
from datetime import datetime

import babel.dates
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression

# set Grid View
_GRID_VIEW = [('grid', "Grid")]

class Base(models.AbstractModel):
    """
        Inherit Base Model .
    """
    _inherit = 'base'

    @api.model
    def read_grid(self, row_fields, col_field, cell_field, domain=None, range=None):
        """
        Current anchor (if sensible for the col_field) can be provided by the
        ``grid_anchor`` value in the context
        :param list[str] row_fields: group row header fields
        :param str col_field: column field
        :param str cell_field: cell field, summed
        :param range: displayed range for the current page
        :returns: dict of prev context, next context, matrix data, row values
                  and column values
        """
        domain = expression.normalize_domain(domain)
        column_info = self._grid_column_information(col_field, range)

        groups = self._read_group_raw(
            expression.AND([domain, column_info.domain]),
            [col_field, cell_field],
            [column_info.grouping] + row_fields,
            lazy=False
        )

        row_key = lambda it, fields=row_fields: tuple(it[field] for field in fields)
        rows = self._get_grid_row_headers(row_fields, groups, key=row_key)
        cols = column_info.values
        cell_map = collections.defaultdict(dict)
        for group in groups:
            row = row_key(group)
            col = column_info.format(group[column_info.grouping])
            cell_map[row][col] = self._grid_format_cell(group, cell_field)

        grid = []
        for row in rows:
            row_list = []
            grid.append(row_list)
            r_k = row_key(row['values'])
            for col in cols:
                col_value = col['values'][col_field][0]
                values = cell_map[r_k].get(col_value)
                if values:
                    row_list.append(values)
                else:
                    dom = expression.AND([row['domain'], col['domain'], domain])
                    row_list.append(self._set_grid_cell_empty(dom))
                row_list[-1]['is_current'] = col.get('is_current', False)

        return {
            'prev': column_info.prev,
            'next': column_info.next,
            'initial': column_info.initial,
            'cols': cols,
            'rows': rows,
            'grid': grid,
        }

    def _set_grid_cell_empty(self, cell_domain):
        """
        Set Empty Value
        :param cell_domain:
        :return:
        """
        return {'size': 0, 'domain': cell_domain, 'value': 0}

    def _grid_format_cell(self, group, cell_field):
        """
        Set Value in Collection
        :param group:
        :param cell_field:
        :return:
        """
        return {
            'size': group['__count'],
            'domain': group['__domain'],
            'value': group[cell_field],
        }

    def _get_grid_row_headers(self, row_fields, groups, key):
        """
        Set Header for the Grid View
        :param row_fields:
        :param groups:
        :param key:
        :return:
        """
        seen = {}
        rows = []
        for cell in groups:
            key_data = key(cell)
            if key_data in seen:
                seen[key_data][1].append(cell['__domain'])
            else:
                value = (
                    {field: cell[field] for field in row_fields},
                    [cell['__domain']],
                )
                seen[key_data] = value
                rows.append(value)

        return [
            {'values': values, 'domain': expression.OR(domains)}
            for values, domains in rows
        ]

    def _grid_column_information(self, name, range):
        """
        :param str name:
        :param range:
        :type range: None | dict
        :rtype: ColMetadata
        """
        if not range:
            range = {}
        field = self._fields[name]
        context_anchor = self.env.context.get('grid_anchor')

        if field.type == 'selection':
            return ColMetadata(
                grouping=name,
                domain=[],
                prev=False,
                next=False,
                initial=False,
                values=[{
                    'values': {name: v},
                    'domain': [(name, '=', v[0])],
                    'is_current': False
                } for v in field._description_selection(self.env)
                ],
                format=lambda a: a,
            )
        elif field.type == 'many2one':
            return ColMetadata(
                grouping=name,
                domain=[],
                prev=False,
                next=False,
                initial=False,
                values=[{
                    'values': {name: v},
                    'domain': [(name, '=', v[0])],
                    'is_current': False
                } for v in self.env[field.comodel_name].search([]).name_get()
                ],
                format=lambda a: a and a[0],
            )
        elif field.type == 'date':
            step = range.get('step', 'day')
            span = range.get('span', 'month')

            today = anchor = field.from_string(field.context_today(self))
            if context_anchor:
                anchor = field.from_string(context_anchor)

            labelize = self._get_date_formatter(
                step, locale=self.env.context.get('lang', 'en_US'))
            rec = self._grid_range_of(span, anchor)
            period_prev, period_next = self._grid_pagination(field, span, anchor)

            return ColMetadata(
                grouping='{}:{}'.format(name, step),
                domain=[
                    '&',
                    (name, '>=', field.to_string(rec.start)),
                    (name, '<=', field.to_string(rec.end))
                ],
                prev=period_prev and {'grid_anchor': period_prev, 'default_%s' % name: period_prev},
                next=period_next and {'grid_anchor': period_next, 'default_%s' % name: period_next},
                initial=period_prev and period_next and {'grid_anchor': field.to_string(today),
                                                         'default_%s' % name: field.to_string(today)},
                values=[{
                    'values': {
                        name: (
                            "%s/%s" % (field.to_string(data), field.to_string(data + self._grid_step_by(step))),
                            labelize(data)
                        )},
                    'domain': ['&',
                               (name, '>=', field.to_string(data)),
                               (name, '<', field.to_string(data + self._grid_step_by(step)))],
                    'is_current': (
                        (data.month == today.month and data.year == today.year) if step == 'month' else data == today),
                } for data in rec.iter(step)
                ],
                format=lambda val: val and val[0],
            )
        else:
            raise ValueError(_("Can not use fields of type %s as grid columns") % field.type)

    @api.model
    def read_grid_domain(self, field, range):
        """ JS grid view may need to know the "span domain" of the grid before
        it has been able to read the grid at all. This provides only that part
        of the grid processing
        """
        if not range:
            range = {}
        field = self._fields[field]
        if field.type == 'selection':
            return []
        elif field.type == 'many2one':
            return []
        elif field.type == 'date':
            span = range.get('span', 'month')

            anchor = field.from_string(field.context_today(self))

            context_anchor = self.env.context.get('grid_anchor')
            if context_anchor:
                anchor = field.from_string(context_anchor)

            gird_range = self._grid_range_of(span, anchor)
            return [
                '&',
                (field.name, '>=', field.to_string(gird_range.start)),
                (field.name, '<=', field.to_string(gird_range.end))
            ]
        raise UserError(_("Can not use fields of type %s as grid columns") % field.type)

    def _get_date_formatter(self, step, locale):
        """ Returns a callable taking a single positional date argument and
        formatting it for the step and locale provided.
        """
        if hasattr(babel.dates, 'format_skeleton'):
            def _format(d, _fmt=babel.dates.format_skeleton, _sk=SKELETONS[step], _l=locale):
                result = _fmt(datetime=d, skeleton=_sk, locale=_l)
                cline = lambda line: sum(len(str) for str in line)
                line1 = result.split(u' ')
                halfway = cline(line1) / 2.
                line2 = collections.deque(maxlen=int(halfway) + 1)
                while cline(line1) > halfway:
                    line2.appendleft(line1.pop())

                middle = line2.popleft()
                if cline(line1) < cline(line2):
                    line1.append(middle)
                else:
                    line2.appendleft(middle)

                return u"%s\n%s" % (
                    u'\u00A0'.join(line1),
                    u'\u00A0'.join(line2),
                )

            return _format
        else:
            return partial(babel.dates.format_date,
                           format=FORMAT[step],
                           locale=locale)

    def _grid_pagination(self, field, span, anchor):
        """
        Add Pagination functionality
        :param field:
        :param span:
        :param anchor:
        :return:
        """
        if field.type == 'date':
            diff = self._grid_step_by(span)
            period_prev = field.to_string(anchor - diff)
            period_next = field.to_string(anchor + diff)
            return period_prev, period_next
        return False, False

    def _grid_step_by(self, span):
        return STEP_BY.get(span)

    def _grid_range_of(self, span, anchor):
        return date_range(self._grid_start_of(span, anchor),
                          self._grid_end_of(span, anchor))

    def _grid_start_of(self, span, anchor):
        return anchor + START_OF[span]

    def _grid_end_of(self, span, anchor):
        return anchor + END_OF[span]


ColMetadata = collections.namedtuple('ColMetadata', 'grouping domain prev next initial values format')


class date_range(object):
    """
    Override Init and Iter function for the date range
    """

    def __init__(self, start, stop):
        # initialization
        assert start < stop
        self.start = start
        self.end = stop

    def iter(self, step):
        # increment value based on step
        start = self.start
        step = STEP_BY[step]
        while start <= self.end:
            yield start
            start += step


START_OF = {
    'week': relativedelta(weekday=MO(-1)),
    'month': relativedelta(day=1),
    'year': relativedelta(yearday=1),
}
END_OF = {
    'week': relativedelta(weekday=SU),
    'month': relativedelta(months=1, day=1, days=-1),
    'year': relativedelta(years=1, yearday=1, days=-1),
}
STEP_BY = {
    'day': relativedelta(days=1),
    'week': relativedelta(weeks=1),
    'month': relativedelta(months=1),
    'year': relativedelta(years=1),
}

FORMAT = {
    'day': u"EEE\nMMM\u00A0dd",
    'month': u'MMMM\u00A0yyyy',
}
SKELETONS = {
    'day': u"MMMEEEdd",
    'month': u'yyyyMMMM',
}
