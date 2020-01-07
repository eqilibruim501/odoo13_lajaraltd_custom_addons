odoo.define('project_advanced_bus.WebClient', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var base_bus = require('bus.Longpolling');
    var session = require('web.session');
    require('bus.BusService');
    WebClient.include({
        show_application: function () {
            var res = this._super();
            this.start_polling();
            return res
        },
        start_polling: function () {
            this.call('bus_service', 'addChannel', 'project_advanced_bus_' + session.uid);
            this.call('bus_service', 'on', 'notification', this, this.bus_notification);
            this.call('bus_service', 'startPolling');
        },
        bus_notification: function (notifications) {
            console.log('hoang1')
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                console.log(notification)
                console.log('______________1111')
            });
        },
    });

});
