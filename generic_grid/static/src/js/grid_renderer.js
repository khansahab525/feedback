/*# -*- coding: utf-8 -*-
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
##############################################################################*/

odoo.define('generic_grid.GridRenderer', function(require) {
    "use strict";
    var AbstractRenderer = require('web.AbstractRenderer');
    var core = require('web.core');
    var utils = require('web.utils');
    var fieldUtils = require('web.field_utils');
    var patch = require('snabbdom.patch');
    var h = require('snabbdom.h');
    var _t = core._t;
    return AbstractRenderer.extend({
        custom_events: _.extend({}, AbstractRenderer.prototype.custom_events, {
            'grid_cell_edited': '_onGridCellBlurEdit',
            'grid_cell_refresh': '_onGridCellBlurRefresh',
        }),
        events: {
            'blur .o_grid_input': "_onGridCellBlur",
            'keydown .o_grid_input': "_onGridCellKeydown",
        },

        /**
         * @override
         * @param {Widget} parent
         * @param {Object} state
         * @param {Object} params
         */
        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.canCreate = params.canCreate;
            this.fields = params.fields;
            this.noContentHelper = params.noContentHelper;
            this.editableCells = params.editableCells;
            this.measureLabel = params.measureLabel;
            this.header_label = params.arch.attrs.string;
            this.cellWidget = params.cellWidget;
            this.cellWidgetOptions = params.cellWidgetOptions || {};
            // this.formatType = this.CellWidgetInstance && this.CellWidgetInstance.formatType ? this.CellWidgetInstance.formatType : this.fields[this.state.cellField].type;
            this.formatType = this.cellWidget || this.fields[this.state.cellField].type;
        },

        /**
         * @override
         */
        start: function() {
            this._state = document.createElement('div');
            this.el.appendChild(this._state);
            return this._super();
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Object} root
         */
        _convertToVNode: function(root) {
            var self = this;
            return h(root.tag, {
                'attrs': root.attrs
            }, _.map(root.children, function(child) {
                if (child.tag) {
                    return self._convertToVNode(child);
                }
                return child;
            }));
        },

        /**
         * @private
         * @param {any[]} grid
         * @returns {{super: number, rows: {}, columns: {}}}
         */
        _computeTotals: function(grid) {
            var totals = {
                super: 0,
                rows: {},
                columns: {}
            };
            for (var i = 0; i < grid.length; i++) {
                var row = grid[i];
                for (var j = 0; j < row.length; j++) {
                    var cell = row[j];
                    totals.super += cell.value;
                    totals.rows[i] = (totals.rows[i] || 0) + cell.value;
                    totals.columns[j] = (totals.columns[j] || 0) + cell.value;
                }
            }
            return totals;
        },

        /**
         * @private
         * @param {any} value
         * @returns {string}
         */
        _format: function(value) {
            if (value === undefined) {
                return '';
            }
            if (this.CellWidgetInstance) {
                return this.CellWidgetInstance.format(value);
            }
            var cellField = this.fields[this.state.cellField];
            return fieldUtils.format[this.formatType](value, cellField, this.cellWidgetOptions);
        },
        _hasContent: function() {
            var state = _.isArray(this.state) ? this.state[0] : this.state;
            return state.rows[0] !== undefined;
        },

        /**
         * @private
         * @param {Object} cell
         * @param {boolean} cell.readonly
         * @returns {boolean}
         */
        _isCellReadonly: function(cell) {
            return !this.editableCells || cell.readonly;
        },

        /**
         * @private
         * @param {string} value
         * @returns {*}
         */
        _parse: function(value) {
            if (this.CellWidgetInstance) {
                return this.CellWidgetInstance.parse(value);
            }
            var cellField = this.fields[this.state.cellField];
            return fieldUtils.parse[this.formatType](value, cellField, this.cellWidgetOptions);
        },

        /**
         * @private
         * @param {Array<Array>} grid actual grid content
         * @param {Array<String>} groupFields
         * @param {Array} path object path to `grid` from the object's state
         * @param {Array} rows list of row keys
         * @param {Object} totals row-keyed totals
         * @returns {snabbdom[]}
         */
        _field2label: function(value_to_display, field_type) {
            if (!value_to_display) {
                return _t('Unknown');
            }
            if (["many2one", "many2many", "one2many", "selection"].indexOf(field_type) > -1) {
                return value_to_display[1];
            } else if (["date"].indexOf(field_type) > -1) {
                return Array.isArray(value_to_display) ? value_to_display.slice(1).join(' ') : value_to_display;
            } else {
                return value_to_display;
            }
        },

        /**
         * @private
         * @returns {Deferred}
         */
        _render: function() {
            var self = this;
            var vnode;
            if (_.isArray(this.state)) {
                if (!(_.isEmpty(this.state) || _.reduce(this.state, function(m, it) {
                        return _.isEqual(m.cols, it.cols) && m;
                    }))) {
                    throw new Error(_t("The sectioned grid view can't handle groups with different columns sets"));
                }
                vnode = this._renderGroupedGrid();
            } else {
                vnode = this._renderUngroupedGrid();
            }
            this._state = patch(this._state, vnode);
            setTimeout(function() {
                var rowHeaders = self.el.querySelectorAll('tbody th:first-child div');
                for (var k = 0; k < rowHeaders.length; k++) {
                    var header = rowHeaders[k];
                    if (header.scrollWidth > header.clientWidth) {
                        $(header).addClass('overflow');
                    }
                }
            }, 0);
            return Promise.resolve();
        },

        /**
         * @private
         * @param {Object} cell
         * @param {any} path
         * @returns {snabbdom}
         */
        _renderCell: function(cell, path) {
            var is_readonly = this._isCellReadonly(cell);
            var classmap = {
                o_grid_cell_container: true,
                o_grid_cell_empty: !cell.size,
                o_grid_cell_readonly: is_readonly,
            };
            // merge in class info from the cell
            // classes may be completely absent, _.each treats that as an empty array
            _.each(cell.classes, function(cls) {
                if (!(cls in classmap)) {
                    // don't allow overwriting initial values
                    classmap[cls] = true;
                }
            });
            return h('td', {
                class: {
                    o_grid_current: cell.is_current
                }
            }, [this._renderCellContent(cell.value, is_readonly, classmap, path)]);
        },

        /**
         * @private
         * @param {any} cell_value
         * @param {boolean} isReadonly
         * @param {any} classmap
         * @param {any} path
         * @returns {snabbdom}
         */
        _renderCellContent: function(cell_value, isReadonly, classmap, path) {
            return h('div', {
                class: classmap,
                attrs: {
                    'data-path': path
                }
            }, [h('i.fa.fa-search-plus.o_grid_cell_information', {
                attrs: {
                    title: _t("See all the records aggregated in this cell")
                }
            }, []), this._renderCellInner(cell_value, isReadonly, path)]);
        },

        /**
         * @private
         * @param {string} formattedValue
         * @param {boolean} isReadonly
         * @returns {snabbdom}
         */
        _renderCellInner: function(cellValue, isReadonly, path) {
            var formattedValue = this._format(cellValue);
            if (this.CellWidgetInstance) {
                return this._renderCellInnerWidget(cellValue, isReadonly, path)
            } else if (isReadonly) {
                return h('div.o_grid_show', formattedValue);
            } else {
                return h('div.o_grid_input', {
                    attrs: {
                        contentEditable: "true"
                    }
                }, formattedValue);
            }
            return '';
        },
        _renderCellInnerWidget: function(cellValue, isReadonly, path) {
            var widget_instance = this.CellWidgetInstance;
            var render_method = widget_instance.render(isReadonly, path);
            return render_method.call(this, cellValue);
        },

        /**
         * @private
         * @param {any} empty
         * @returns {snabbdom}
         */
        _renderEmptyWarning: function(empty) {
            if (!empty || !this.noContentHelper || !this.noContentHelper.children.length || !this.canCreate) {
                return [];
            }
            return h('div.o_grid_nocontent_container', [h('div.o_view_nocontent oe_edit_only', _.map(this.noContentHelper.children, this._convertToVNode.bind(this)))]);
        },
        _renderGridColumnTotalCell: function(node, value) {
            if (this.state.range === 'day') {
                return [];
            }
            return [h(node, value)];
        },

        _renderGridRows: function(grid, groupFields, path, rows, totals) {
            var self = this;
            return _.map(grid, function(row, rowIndex) {
                var rowValues = [];
                var rowKeys = [];
                for (var i = 0; i < groupFields.length; i++) {
                    var row_field = groupFields[i];
                    var value = rows[rowIndex].values[row_field];
                    var fieldName = row_field.split(':')[0];
                    var field_type = self.fields[fieldName].type;
                    if (field_type === 'selection') {
                        value = self.fields[fieldName].selection.find(function(choice) {
                            return choice[0] === value;
                        });
                    }
                    let key = ['selection', 'many2one'].includes(field_type) ? value[0] : value;
                    rowKeys.push(key);
                    rowValues.push(self._field2label(value, field_type));
                }
                var rowKey = rowKeys.join('|');
                return h('tr', {
                    key: rowKey
                }, [h('th', {}, [h('div', _.map(rowValues, function(label) {
                    var klass = label !== _t('Unknown') ? '' : 'o_grid_text_muted';
                    return h('div', {
                        attrs: {
                            title: label,
                            class: klass
                        }
                    }, label);
                }))])].concat(_.map(row, function(cell, cell_index) {
                    return self._renderCell(cell, path.concat([rowIndex, cell_index]).join('.'));
                }), self._renderGridColumnTotalCell('td.o_grid_total', self._format(totals[rowIndex]))));
            });
        },

        /**
         * @private
         * @returns {snabbdom}
         */
        _renderGroupedGrid: function() {
            var self = this;
            var columns = this.state.length ? this.state[0].cols : [];
            var superTotals = this._computeTotals(_.flatten(_.pluck(this.state, 'grid'), true));
            var vnode = this._renderTable(columns, superTotals.columns, superTotals.super);
            var gridBody = vnode.children[0].children;
            for (var n = 0; n < this.state.length; n++) {
                var grid = this.state[n];
                var totals = this._computeTotals(grid.grid);
                var rows = this._renderGridRows(grid.grid || [], this.state.groupBy.slice(1), [n, 'grid'], grid.rows || [], totals.rows);
                gridBody.push(h('tbody', {
                    class: {
                        o_grid_section: true
                    }
                }, [h('tr', [h('th', {}, [(grid.__label || [])[1] || _t('Unknown')])].concat(_(columns).map(function(column, column_index) {
                    return h('td', {
                        class: {
                            o_grid_current: column.is_current,
                        }
                    }, self._format(totals.columns[column_index]));
                }), self._renderGridColumnTotalCell('td.o_grid_total', self._format(totals.super))))].concat(rows)));
            }
            return vnode;
        },

        /**
         * Generates the header and footer for the grid's table. If
         * totals and super_total are provided they will be formatted and
         * inserted into the table footer, otherwise the cells will be left empty
         *
         * @private
         * @param {Array} columns
         * @param {Object} [totals]
         * @param {Number} [super_total]
         * @param {boolean} [empty=false]
         * @returns {snabbdom}
         */
        _renderTable: function(columns, totals, super_total, empty) {
            var self = this;
            var col_field = this.state.colField;
            var total_label;
            var header_label = '';
            if (this.measureLabel) {
                total_label = _.str.sprintf(_t("Total (%s)"), this.measureLabel);
            } else {
                total_label = _t("Total");
            }
            if (this.header_label) {
                header_label = this.header_label;
            }
            return h('div.o_view_grid.table-responsive', [h('table.table.table-sm.table-striped', [h('thead', [h('tr', [h('th.o_grid_title_header', header_label), ].concat(_.map(columns, function(column) {
                return h('th', {
                    class: {
                        o_grid_current: column.is_current
                    }
                }, column.values[col_field][1]);
            }), self._renderGridColumnTotalCell('th.o_grid_total', total_label)))]), h('tfoot', [h('tr', [h('td', totals ? total_label : [])].concat(_.map(columns, function(column, column_index) {
                var cell_content = !totals ? [] : self._format(totals[column_index]);
                return h(totals && totals[column_index] ? 'td' : 'td.text-muted', {
                    class: {
                        o_grid_current: column.is_current,
                    }
                }, cell_content);
            }), self._renderGridColumnTotalCell('td', !super_total ? [] : self._format(super_total))))]), ])].concat(this._renderEmptyWarning(empty)));
        },

        /**
         * @private
         * @returns {snabbdom}
         */
        _renderUngroupedGrid: function() {
            var self = this;
            var vnode;
            var columns = this.state.cols;
            var rows = this.state.rows;
            var grid = this.state.grid;
            var totals = this._computeTotals(grid);
            vnode = this._renderTable(columns, totals.columns, totals.super, !grid.length);
            vnode.children[0].children.push(h('tbody', this._renderGridRows(grid, this.state.groupBy, ['grid'], rows, totals.rows).concat(_.times(Math.max(5 - rows.length, 0), function() {
                return h('tr.o_grid_padding', [h('th', {}, "\u00A0")].concat(_.map(columns, function(column) {
                    return h('td', {
                        class: {
                            o_grid_current: column.is_current
                        }
                    }, []);
                }), self._renderGridColumnTotalCell('td.o_grid_total', [])));
            }))));
            return vnode;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {MouseEvent} e
         */
        _onGridCellBlur: function(e) {
            var $target = $(e.target);
            var value;
            try {
                value = this._parse(e.target.textContent.trim());
                $target.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
            } catch (_) {
                $target.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                return;
            }
            var cell_path = $target.parent().attr('data-path').split('.');
            var grid_path = cell_path.slice(0, -3);
            var row_path = grid_path.concat(['rows'], cell_path.slice(-2, -1));
            var col_path = grid_path.concat(['cols'], cell_path.slice(-1));
            this.trigger_up('cell_edited', {
                cell_path: cell_path,
                row_path: row_path,
                col_path: col_path,
                value: value,
            });
        },

        /**
         * @private
         * @param {KeyboardEvent} e
         */
        _onGridCellKeydown: function(e) {
            switch (e.which) {
                case $.ui.keyCode.ENTER:
                    e.preventDefault();
                    e.stopPropagation();
                    break;
            }
        },

        /**
         * @private
         * @param {Edit} e
         */
        _onGridCellBlurEdit: function(e) {
            var path = e.data.path;
            var button = this.$("div[data-path='" + path + "']").find('button');
            var value;
            try {
                value = this._parse(button.text());
            } catch (_) {
                return;
            }
            var cell_path = path.split('.');
            var grid_path = cell_path.slice(0, -3);
            var row_path = grid_path.concat(['rows'], cell_path.slice(-2, -1));
            var col_path = grid_path.concat(['cols'], cell_path.slice(-1));
            button.prop('disabled', true);
            this.trigger_up('cell_edited', {
                cell_path: cell_path,
                row_path: row_path,
                col_path: col_path,
                value: value,
                doneCallback: function() {
                    button.prop('disabled', false);
                }
            });
        },

        /**
         * @private
         * @param {Refresh} e
         */
        _onGridCellBlurRefresh: function(e) {
            try {
                var value = e.data.formattedValue;
                var path = e.data.path;
                var selector = e.data.selector || false;
                var $cell = this.$("div[data-path='" + path + "']")
                if (selector) {
                    $cell.find(selector).text(value);
                } else {
                    $cell.text(value);
                }
            } catch (_) {
                return;
            }
        }
    });
});;
