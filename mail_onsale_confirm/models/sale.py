# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import smtplib, ssl


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                order.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        try:
            template = self.env.ref('mail_onsale_confirm.email_template_sale_order')
        except ValueError:
            template = False
        template.email_to = 'anita@lumossolar.com,brian@lumossolar.com,dinesh@lumossolar.com,gea@lumossolar.com,keith@lumossolar.com,ryan@lumossolar.com,scott@lumossolar.com'
        # template.email_to = 'vikas_kumar@seologistics.com'

        template.email_from = 'lumosodooconfirmation@lumossolar.com'
        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        return True


