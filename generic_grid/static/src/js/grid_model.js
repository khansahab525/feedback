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

odoo.define('generic_grid.GridModel', function(require) {
    "use strict";
    var AbstractModel = require('web.AbstractModel');
    var concurrency = require('web.concurrency');
    return AbstractModel.extend({
        /**
         * @override
         */
        init: function() {
            this._super.apply(this, arguments);
            this._gridData = null;
            this._fetchMutex = new concurrency.MutexedDropPrevious();
        },

        /**
         * @override
         * @returns {Object}
         */
        get: function() {
            return this._gridData;
        },

        /**
         * @override
         * @param {Object} context
         * @returns {Object}
         */
        getContext: function(context) {
            var c = _.extend({}, this.context, context);
            return c;
        },

        /**
         * The data from the grid view basically come from a read_group so we don't
         * have any res_ids. A big domain is thus computed with the domain of all
         * cells and this big domain is used to search for res_ids.
         */
        getIds: function() {
            var data = this._gridData;
            if (!_.isArray(data)) {
                data = [data];
            }
            var domain = [];
            // count number of non-empty cells and only add those to the search
            var cells = 0;
            for (var i = 0; i < data.length; i++) {
                var grid = data[i].grid;
                for (var j = 0; j < grid.length; j++) {
                    var row = grid[j];
                    for (var k = 0; k < row.length; k++) {
                        var cell = row[k];
                        if (cell.size !== 0) {
                            cells++;
                            domain.push.apply(domain, cell.domain);
                        }
                    }
                }
            }

            // if there are no elements in the grid we'll get an empty domain
            // which will select all records of the model... that is *not* what
            // we want
            if (cells === 0) {
                return Promise.resolve([]);
            }
            while (--cells > 0) {
                domain.unshift('|');
            }
            return this._rpc({
                model: this.modelName,
                method: 'search',
                args: [domain],
                context: this.getContext(),
            });
        },

        /**
         * @override
         * @param {Object} params
         * @returns {Deferred}
         */
        load: function(params) {
            this.modelName = params.modelName;
            this.rowFields = params.rowFields;
            this.sectionField = params.sectionField;
            this.colField = params.colField;
            this.cellField = params.cellField;
            this.ranges = params.ranges;
            this.currentRange = params.currentRange;
            this.domain = params.domain;
            this.context = params.context;
            var groupedBy = (params.groupedBy && params.groupedBy.length) ? params.groupedBy : this.rowFields;
            this.groupedBy = Array.isArray(groupedBy) ? groupedBy : [groupedBy];
            this.readonlyField = params.readonlyField;
            return this._fetch(this.groupedBy);
        },

        /**
         * @override
         * @param {any} handle this parameter is ignored
         * @param {Object} params
         * @returns {Deferred}
         */
        reload: function(handle, params) {
            if (params === 'special') {
                return Promise.resolve();
            }
            params = params || {};
            if ('context' in params) {
                var old_context = this.context;
                this.context = params.context;
                if (old_context.grid_anchor !== undefined || params.context.grid_anchor !== undefined) {
                    this.context.grid_anchor = old_context.grid_anchor || params.context.grid_anchor;
                }
            }
            if ('domain' in params) {
                this.domain = params.domain;
            }
            if ('pagination' in params) {
                _.extend(this.context, params.pagination);
            }
            if ('range' in params) {
                this.currentRange = _.findWhere(this.ranges, {
                    name: params.range
                });
            }
            if ('groupBy' in params) {
                if (params.groupBy.length) {
                    this.groupedBy = Array.isArray(params.groupBy) ? params.groupBy : [params.groupBy];
                } else {
                    this.groupedBy = this.rowFields;
                }
            }
            return this._fetch(this.groupedBy);
        },

        /**
         * @private
         * @param {string[]} groupBy
         * @returns {Deferred}
         */
        _fetch: function(groupBy) {
            var self = this;
            if (!this.currentRange) {
                return Promise.resolve();
            }
            return this._fetchMutex.exec(function() {
                if (self.sectionField && self.sectionField === groupBy[0]) {
                    return self._getGroupedData(groupBy);
                } else {
                    return self._getUngroupedData(groupBy);
                }
            });
        },

        /**
         * @private
         * @param {string[]} groupBy
         * @returns {Deferred}
         */
        _getGroupedData: function(groupBy) {
            var self = this;
            return this._rpc({
                model: self.modelName,
                method: 'read_grid_domain',
                kwargs: {
                    field: self.colField,
                    range: self.currentRange,
                },
                context: self.getContext(),
            }).then(function(d) {
                return self._rpc({
                    model: self.modelName,
                    method: 'read_group',
                    kwargs: {
                        domain: d.concat(self.domain || []),
                        fields: [self.sectionField],
                        groupby: [self.sectionField],
                    },
                    context: self.getContext()
                });
            }).then(function(groups) {
                if (!groups.length) {
                    // if there are no groups in the output we still need
                    // to fetch an empty grid so we can render the table's
                    // decoration (pagination and columns &etc) otherwise
                    // we get a completely empty grid
                    return Promise.all([self._fetchSectionGrid(groupBy, {
                        __domain: self.domain || [],
                    })]);
                }
                return Promise.all((groups || []).map(function(group) {
                    return self._fetchSectionGrid(groupBy, group);
                }));
            }).then(function(results) {
                self._gridData = results;
                self._gridData.groupBy = groupBy;
                self._gridData.colField = self.colField;
                self._gridData.cellField = self.cellField;
                self._gridData.range = self.currentRange.name;
                self._gridData.context = self.context;

                // set the prev & next in the state for grouped
                var r0 = results[0];
                self._gridData.prev = r0 && r0.prev;
                self._gridData.next = r0 && r0.next;
            });
        },

        /**
         * @private
         * @param {string[]} groupBy
         * @param {Object} sectionGroup
         * @param {Object} [additionalContext]
         * @returns {Deferred}
         */
        _fetchSectionGrid: function(groupBy, sectionGroup, additionalContext) {
            var self = this;
            var rpcProm = this._rpc({
                model: this.modelName,
                method: 'read_grid',
                kwargs: {
                    row_fields: groupBy.slice(1),
                    col_field: this.colField,
                    cell_field: this.cellField,
                    range: this.currentRange,
                    domain: sectionGroup.__domain,
                    readonly_field: this.readonlyField,
                },
                context: this.getContext(additionalContext),
            })
            rpcProm.then(function(grid) {
                grid.__label = sectionGroup[self.sectionField];
            });
            return rpcProm;
        },

        /**
         * @private
         * @param {string[]} groupBy
         * @returns {Deferred}
         */
        _getUngroupedData: function(groupBy) {
            var self = this;
            return this._rpc({
                model: self.modelName,
                method: 'read_grid',
                kwargs: {
                    row_fields: groupBy,
                    col_field: self.colField,
                    cell_field: self.cellField,
                    domain: self.domain,
                    range: self.currentRange,
                    readonly_field: this.readonlyField,
                },
                context: self.getContext(),
            }).then(function(result) {
                self._gridData = result;
                self._gridData.groupBy = groupBy;
                self._gridData.colField = self.colField;
                self._gridData.cellField = self.cellField;
                self._gridData.range = self.currentRange.name;
                self._gridData.context = self.context;
            });
        },
    });
});;
