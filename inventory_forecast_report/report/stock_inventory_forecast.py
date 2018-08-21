# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.fields import Datetime as fieldsDatetime


class StockInventoryForecast(models.Model):
    _name = 'stock.inventory.forecast'
    _auto = False
    _order = 'date asc'

    company_id = fields.Many2one('res.company', 'Company')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity On Hand')
    date = fields.Datetime('Operation Date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_inventory_forecast')
        self._cr.execute("""
            CREATE VIEW stock_inventory_forecast AS (
              SELECT MIN(foo.id) as id,
                foo.company_id,
                foo.product_id,
                SUM(foo.quantity) - sum(sale_order_line.product_uom_qty) * (30/100) as quantity,
                foo.date
                FROM
                ((SELECT
                    stock_move.id AS id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    quant.qty AS quantity,
                    stock_move.date AS date
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state in ('done', 'draft', 'confirmed', 'waiting', 'assigned') AND dest_location.usage in ('internal', 'transit')
                AND (
                    not (source_location.company_id is null and dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    source_location.usage not in ('internal', 'transit'))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state in ('done', 'draft', 'confirmed', 'waiting', 'assigned') AND source_location.usage in ('internal', 'transit')
                AND (
                    not (dest_location.company_id is null and source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    dest_location.usage not in ('internal', 'transit'))
                ))
                AS foo
                JOIN
                    sale_order_line ON sale_order_line.product_id = foo.product_id
                where sale_order_line.order_id in (select id from sale_order where state in ('draft', 'sent'))
                GROUP BY foo.company_id, foo.product_id, foo.date
                )""")
