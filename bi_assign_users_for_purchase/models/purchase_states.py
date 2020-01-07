# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from odoo.http import request


class PurchaseOrderInherit(models.Model):
	_inherit = 'purchase.order'

	salesperson_id = fields.Many2one('res.users', compute="_compute_salesperson", store=True, string = 'Salesperson')
	auto_user_assign = fields.Boolean(string="Auto User Assign")

	@api.depends('state')
	def _compute_salesperson(self):
		for res in self:
			if res.auto_user_assign != False:
				if res.state == 'draft':
					res.salesperson_id = int(res.env['ir.config_parameter'].sudo().get_param('bi_assign_users_for_purchase.draft_id'))
					res.write({'user_id' : res.salesperson_id.id
						})
				elif res.state == 'sent':
					res.salesperson_id = int(res.env['ir.config_parameter'].sudo().get_param('bi_assign_users_for_purchase.sent_id'))
					res.write({'user_id' : res.salesperson_id.id
						})
				else:
					res.salesperson_id = int(res.env['ir.config_parameter'].sudo().get_param('bi_assign_users_for_purchase.purchase_order_id'))
					res.write({'user_id' : res.salesperson_id.id
						})
				sus_id = res.env['res.partner'].browse(SUPERUSER_ID)
				partner_email = res.partner_id.email
				if not partner_email:
						raise UserError(_('%s customer has no email id please enter email address')
								% (res.partner_id.name))
				else:
					template_id = res.env['ir.model.data'].get_object_reference(
														  'bi_assign_users_for_purchase',
														  'email_template_edi_salesperson_assigned')[1]
					email_template_obj = res.env['mail.template'].browse(template_id)
					if template_id:
						values = email_template_obj.generate_email(res.id, fields=None)
						values['email_from'] = sus_id.email
						values['email_to'] = res.salesperson_id.email

						values['author_id'] = res.env['res.users'].browse(request.env.uid).partner_id.id
						mail_mail_obj = res.env['mail.mail']
						msg_id = mail_mail_obj.sudo().create(values)
						if msg_id:
							msg_id.sudo().send()

			return True
	

	def action_view_invoice(self):
		'''
		This function returns an action that display existing vendor bills of given purchase order ids.
		When only one found, show the vendor bill immediately.
		'''
		action = self.env.ref('account.action_vendor_bill_template')
		result = action.read()[0]
		create_bill = self.env.context.get('create_bill', False)
		# override the context to get rid of the default filtering
		result['context'] = {
			'type': 'in_invoice',
			'default_purchase_id': self.id,
			'default_currency_id': self.currency_id.id,
			'default_company_id': self.company_id.id,
			'default_user_id': self.user_id.id,
			'company_id': self.company_id.id
		}
		# choose the view_mode accordingly
		if len(self.invoice_ids) > 1 and not create_bill:
			result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
		else:
			res = self.env.ref('account.invoice_supplier_form', False)
			result['views'] = [(res and res.id or False, 'form')]
			# Do not set an invoice_id if we want to create a new bill.
			if not create_bill:
				result['res_id'] = self.invoice_ids.id or False
		return result			

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: