# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_forecast_report = fields.Boolean('Is Forecast Report Show')

    @api.multi
    def action_stock_inventory_forecast(self):
        self.ensure_one()
        action_data = self.env.ref('inventory_forecast_report.action_stock_inventory_forecast').read()[0]
        action_data['domain'] = [('product_id.product_tmpl_id', '=', self.id), ('product_template_id', '=', self.id)]
        return action_data


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def action_stock_inventory_forecast(self):
        self.ensure_one()
        action_data = self.product_tmpl_id.action_stock_inventory_forecast()
        action_data['domain'] = [('product_id', '=', self.id), ('product_template_id', '=', self.product_tmpl_id.id)]
        return action_data
