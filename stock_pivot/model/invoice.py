# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('price_unit')
    def _onchange_price_unit_id(self):
        if self.purchase_line_id:
            if self.price_unit != self.purchase_line_id.price_unit:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Unit Price is different from linked purchse order line Price ! Kindly validate it !'),
                }
                return {'warning': warning}