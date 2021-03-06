# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'

    name = fields.Char(string='Name', required=True)
    note_field = fields.Html(string='Comment')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
