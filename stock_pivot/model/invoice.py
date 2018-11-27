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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_get_stock_forecast_tree_view(self):
        ir_model_data = self.env['ir.model.data']
        stock_forecast_tree = ir_model_data.get_object_reference('stock_pivot', 'viewstock_forecast_tree')[1]
        return {'type': 'ir.actions.act_window',
                'domain': [('product_tmpl_id', '=', self.id)],
                'name': 'Stock Level forecast',
                'view_type': 'tree',
                'view_mode': 'tree',
               'view_id': stock_forecast_tree,
                'res_model': 'total.stock.report.forecast',
                'res_id': self.id,
                }