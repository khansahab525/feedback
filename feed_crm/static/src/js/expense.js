odoo.define('feed_crm.project_code_widget', function (require) {
    "use strict";
    console.log('bssssssssssssssssssssssssssssssss')

    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var registry = require('web.field_registry');

    var ProjectCodeWidget = FieldMany2One.extend({
        _render: function () {
            this._super.apply(this, arguments);

            var self = this;
            var project_id = this.display_name;

            // Check if the project_id is valid
            if (project_id) {
                // Fetch the project code using project_id
                this._rpc({
                    model: 'project.project',
                    method: 'read',
                    args: [project_id, ['project_code']],
                }).then(function (result) {
                    if (result.length) {
                        // Render the project code using html method
                        self.$el.html(result[0].project_code);
                    }
                }).catch(function (error) {
                    // Handle any errors or exceptions
                    console.error(error);
                });
            }
        },
    });

    registry.add('project_code_widget', ProjectCodeWidget);

return ProjectCodeWidget;
});
