import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def write(self, vals):
        try:
            if vals.get('stage_id'):
                notifications = []
                message = {
                    'info': 'project tasks changed',
                    'action': 'reload',
                    'create_uid': self._uid
                }
                self.env.cr.execute("""select id
                from res_users
                where partner_id is not null
                  and partner_id in (select partner_id
                                     from mail_followers
                                     where res_model like 'project.project'
                                       and res_id in %s)""", (tuple(self.project_id.ids),))
                followers = self.env.cr.fetchall()
                if followers is not None and len(followers) > 0:
                    follower_ids = [e[0] for e in followers]
                    # follower_bus = ['project_advanced_bus_' + str(e[0]) for e in followers]
                    # self.env.cr.execute(
                    #     """select channel from bus_bus where channel like '"project_advanced_bus_7"' and create_date > current_timestamp  - interval '1 second' and channel in %s""",
                    #     (tuple(follower_bus),))
                    # notified_channels = self.env.cr.fetchall()
                    # if notified_channels is not None and len(notified_channels) > 0:
                    #     notified_channels = [e[0].replace('project_advanced_bus_', '') for e in notified_channels]
                    #     follower_ids_tmp = []
                    #     for e in follower_ids:
                    #         if e not in notified_channels:
                    #             follower_ids_tmp.append(e)
                    #     follower_ids = follower_ids_tmp
                    for follower in follower_ids:
                        if follower != self.env.uid:
                            notifications.append(('project_advanced_bus_' + str(follower), message))
                self.env['bus.bus'].sudo().sendmany(notifications)
        except Exception as ex:
            _logger.info("project task bus : " + str(ex))
        return super(ProjectTask, self).write(vals)
