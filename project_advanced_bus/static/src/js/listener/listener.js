var c_p_v_l_s = false;
odoo.define('project_advanced_bus.ActionManager', function (require) {
    "use strict";
    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var _t = core._t;
    var current_env_model_name = '';
    var current_view_type = '';
    var webClient = require('web.WebClient');
    var last_action;

    ActionManager.include({
        custom_events: _.extend({}, ActionManager.prototype.custom_events, {
            env_updated: '_onEnvUpdated',
            switch_view: '_onSwitchView',
        }),
        _onEnvUpdated: function (ev) {
            var self = this;
            current_env_model_name = ev.target.modelName;
            current_view_type = ev.target.renderer.viewType;
            self._updateCurrentProjectViewListener()
            return this._super.apply(this, arguments);
        },
        _onSwitchView: function (ev) {
            current_view_type = ev.target.renderer.viewType;
            return this._super.apply(this, arguments);
        },
        _updateCurrentProjectViewListener: function () {
            var self = this;
            var n_c_p_v_l_s = false;
            if (current_env_model_name === 'project.task' && current_view_type === 'kanban') {
                try {
                    if (self.actions != null) {
                        var last_action_tmp;
                        for (var key in self.actions) {
                            last_action_tmp = self.actions[key];
                        }
                        if (last_action_tmp['xml_id'] == 'project.act_project_project_2_project_task_all') {
                            n_c_p_v_l_s = true;
                            last_action = last_action_tmp;
                        }
                    }
                } catch (e) {
                    console.log(e)
                }
            } else {
                n_c_p_v_l_s = false;
            }
            c_p_v_l_s = n_c_p_v_l_s;
        },
    });
});
odoo.define('project_advanced_bus.WebClient', function (require) {
    "use strict";
    var reload_lock = false;
    var WebClient = require('web.WebClient');
    // var base_bus = require('bus.Longpolling');
    var session = require('web.session');
    var searchView = require('web.SearchView');
    // var BusService = require('bus.BusService');
    WebClient.include({
        show_application: function () {
            var res = this._super();
            this.start_polling();
            return res
        },
        start_polling: function () {
            this.call('bus_service', 'addChannel', 'project_advanced_bus_' + session.uid);
            this.call('bus_service', 'on', 'notification', this, this._project_task_notification_callback);
            this.call('bus_service', 'startPolling');
        },
        _project_task_notification_callback: function (notifications) {
            if (c_p_v_l_s === true) {
                var self = this;
                _.each(notifications, function (notification) {
                    var channel = notification[0];
                    var message = notification[1];
                    if (channel == 'project_advanced_bus_' + session.uid) {
                        if (!reload_lock) {
                            reload_lock = true;
                            setTimeout(function () {
                                reload_lock = false;
                                //do search
                                self._reload_search()
                            }, 100);
                        }
                    }
                });
            }
        },
        _reload_search: function () {
            var self = this;
            $(".o_searchview_input").focus()
            var e = jQuery.Event("keypress");
            e.which = 13;
            e.keyCode = 13;
            $(".o_searchview_input").trigger(e);

            var e = jQuery.Event('keydown', {which: $.ui.keyCode.ENTER});

            $('.o_searchview_input').trigger(e);


            // $('.o_searchview_input').focus()

            // var active_view = self.action_manager.inner_widget.active_view;
            // if (typeof(active_view) != 'undefined') {
            //     try {
            //         var controller = self.action_manager.inner_widget.active_view.controller;
            //         var action = self.action_manager.inner_widget.action;
            //         controller.reload();
            //     } catch (e) {
            //         alert(e);
            //     }
            // }
        },
    });

});
