# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
import smtplib, ssl
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        try:
            template = self.env.ref('mail_onsale_confirm.email_template_sale_order_testing')
        except ValueError:
            template = False
        # template.email_to = 'anita@lumossolar.com,brian@lumossolar.com,dinesh@lumossolar.com,gea@lumossolar.com,keith@lumossolar.com,ryan@lumossolar.com,scott@lumossolar.com'
        template.email_to = 'shakyavikas77@gmail.com'

        # template.email_from = 'lumosodooconfirmation@lumossolar.com'
        template.email_from = 'testingodoo18@gmail.com'
        # Send out the e-mail template to the user
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        return True
