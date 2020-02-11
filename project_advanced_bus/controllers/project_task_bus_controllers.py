import logging

import odoo
from odoo.http import request

_logger = logging.getLogger(__name__)


try:
    from odoo.addons.bus.controllers.main import BusController
except ImportError:
    _logger.error('project inconsisten with odoo version')
    BusController = object


class Controller(BusController):
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
            new_channel = (request.db, 'project.advanced.bus', request.uid)
            channels.append(new_channel)
        return super(Controller, self)._poll(dbname, channels, last, options)