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

odoo.define('generic_grid.GridView', function(require) {
    "use strict";
    var AbstractView = require('web.AbstractView');
    var config = require('web.config');
    var core = require('web.core');
    var GridModel = require('generic_grid.GridModel');
    var GridController = require('generic_grid.GridController');
    var GridRenderer = require('generic_grid.GridRenderer');
    var viewRegistry = require('web.view_registry');
    var pyUtils = require('web.py_utils');
    var _t = core._t;
    var _lt = core._lt;
    var GridView = AbstractView.extend({
        display_name: _lt('Grid'),
        mobile_friendly: true,
        icon: 'fa-th',
        config: _.extend({}, AbstractView.prototype.config, {
            Model: GridModel,
            Controller: GridController,
            Renderer: GridRenderer,
        }),
        viewType: 'grid',
        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            var arch = this.arch;
            var fields = this.fields;
            var rowFields = [];
            var sectionField, colField, cellField, ranges, cellWidget, cellWidgetOptions, measureLabel, readonlyField;
            _.each(arch.children, function(child) {
                if (child.tag === 'field') {
                    if (child.attrs.type === 'row') {
                        if (child.attrs.section === '1' && !sectionField) {
                            sectionField = child.attrs.name;
                        }
                        rowFields.push(child.attrs.name);
                    }
                    if (child.attrs.type === 'col') {
                        colField = child.attrs.name;
                        ranges = self._extract_ranges(child, params.context);
                    }
                    if (child.attrs.type === 'measure') {
                        cellField = child.attrs.name;
                        cellWidget = child.attrs.widget;
                        if (child.attrs.options) {
                            cellWidgetOptions = JSON.parse(child.attrs.options.replace(/'/g, '"'));
                        }
                        measureLabel = child.attrs.string;
                    }
                    if (child.attrs.type === 'readonly') {
                        readonlyField = child.attrs.name;
                    }
                }
            });

            // model
            this.loadParams.ranges = ranges;
            var contextRangeName = params.context.grid_range;
            var contextRange = contextRangeName && _.findWhere(ranges, {
                name: contextRangeName
            });
            this.loadParams.currentRange = contextRange || ranges[0];
            this.loadParams.rowFields = rowFields;
            this.loadParams.sectionField = sectionField;
            this.loadParams.colField = colField;
            this.loadParams.cellField = cellField;
            this.loadParams.groupedBy = params.groupBy;
            this.loadParams.readonlyField = readonlyField;

            // renderer
            this.rendererParams.canCreate = this.controllerParams.activeActions.create;
            this.rendererParams.fields = fields;
            this.rendererParams.measureLabel = measureLabel;
            this.rendererParams.noContentHelper = _.find(arch.children, function(c) {
                return c.tag === 'empty';
            });
            this.rendererParams.editableCells = this.controllerParams.activeActions.edit && arch.attrs.adjustment;
            this.rendererParams.cellWidget = cellWidget;
            this.rendererParams.cellWidgetOptions = cellWidgetOptions;

            // controller
            this.controllerParams.formViewID = false;
            this.controllerParams.listViewID = false;
            _.each(params.actionViews, function(view) {
                if (view.type === 'form') {
                    self.controllerParams.formViewID = view.viewID;
                }
                if (view.type === 'list') {
                    self.controllerParams.listViewID = view.viewID;
                }
            });
            this.controllerParams.context = params.context;
            this.controllerParams.ranges = ranges;
            this.controllerParams.currentRange = this.loadParams.currentRange.name;
            this.controllerParams.navigationButtons = arch.children.filter(function(c) {
                return c.tag === 'button';
            }).map(function(c) {
                return c.attrs;
            });
            this.controllerParams.adjustment = arch.attrs.adjustment;
            this.controllerParams.adjustName = arch.attrs.adjust_name;
        },
        _extract_ranges: function(col_node, context) {
            var ranges = [];
            if (config.device.isMobile) {
                ranges.push({
                    name: 'day',
                    string: _t('Day'),
                    span: 'day',
                    step: 'day',
                });
            }
            var pyevalContext = py.dict.fromJSON(context || {});
            _.each(_.pluck(col_node.children, 'attrs'), function(range) {
                if (range.invisible && pyUtils.py_eval(range.invisible, {
                        'context': pyevalContext
                    })) {
                    return;
                }
                ranges.push(range);
            });
            return ranges;
        },
    });
    viewRegistry.add('grid', GridView);
    return GridView;
});;
