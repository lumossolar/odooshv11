# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

    # @api.multi
    # def action_confirm(self):
    #     # fetch the partner's id and subscribe the partner to the sale order
    #     for order in self:
    #         if order.partner_id not in order.message_partner_ids:
    #             pass
    #             # order.message_subscribe([order.partner_id.id])
    #     return super(SaleOrder, self).action_confirm()



from odoo import _, api, exceptions, fields, models, tools

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        """ Add partners to the records followers. """
        # not necessary for computation, but saves an access right check
        if not partner_ids and not channel_ids:
            return True
        if partner_ids is None:
            partner_ids = []
        if channel_ids is None:
            channel_ids = []

        # TDE CHECK THIS
        if not channel_ids and partner_ids and set(partner_ids) == set([self.env.user.partner_id.id]):
            try:
                self.check_access_rights('read')
                self.check_access_rule('read')
            except exceptions.AccessError:
                return False
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')

        partner_data = dict((pid, subtype_ids) for pid in partner_ids)
        channel_data = dict((cid, subtype_ids) for cid in channel_ids)
        gen, part = self.env['mail.followers']._add_follower_command(self._name, self.ids, partner_data, channel_data,
                                                                     force=force)

        if gen:
            if not gen[0][2]["res_model"] == 'sale.order':
                self.sudo().write({'message_follower_ids': gen})
        for record in self.filtered(lambda self: self.id in part):
            record.write({'message_follower_ids': part[record.id]})

        self.invalidate_cache()
        return True


