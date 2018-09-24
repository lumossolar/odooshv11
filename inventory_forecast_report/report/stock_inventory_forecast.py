# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.fields import Datetime as fieldsDatetime


class StockInventoryForecast(models.Model):
    _name = 'stock.inventory.forecast'
    _auto = False
    _order = 'date'

    company_id = fields.Many2one('res.company', 'Company')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity On Hand')
    date = fields.Datetime('Operation Date')
    # source = fields.Datetime('source')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_inventory_forecast')
        self._cr.execute("""
            CREATE VIEW stock_inventory_forecast AS (
              SELECT MIN(id) as id,
                company_id,
                product_id,
                sum(quantity) as quantity,
                date
                FROM
                    (
                        (SELECT
                            sale_order_line.id AS id,
                            sorder.company_id AS company_id,
                            sale_order_line.product_id AS product_id,
                            - sale_order_line.product_uom_qty * 30/100 AS quantity,
                            sorder.date_order AS date
                        FROM
                            sale_order as sorder
                        JOIN
                            sale_order_line ON sale_order_line.order_id = sorder.id
                        JOIN
                            product_product ON product_product.id = sale_order_line.product_id
                        WHERE sorder.state in ('draft', 'sent')
                        )
                        UNION ALL
                        (SELECT
                            (-1) * sale_order_line.id AS id,
                            sorder.company_id AS company_id,
                            sale_order_line.product_id AS product_id,
                            - sale_order_line.product_uom_qty AS quantity,
                            sorder.date_order AS date
                        FROM
                            sale_order as sorder
                        JOIN
                            sale_order_line ON sale_order_line.order_id = sorder.id
                        JOIN
                            product_product ON product_product.id = sale_order_line.product_id
                        WHERE sorder.state = 'sale'
                        )
                        UNION ALL
                        (SELECT
                            purchase_order_line.id AS id,
                            porder.company_id AS company_id,
                            purchase_order_line.product_id AS product_id,
                            purchase_order_line.product_qty AS quantity,
                            porder.date_order AS date
                        FROM
                            purchase_order as porder
                        JOIN
                            purchase_order_line ON purchase_order_line.order_id = porder.id
                        JOIN
                            product_product ON product_product.id = purchase_order_line.product_id
                        WHERE porder.state != 'cancel'
                        )
                        UNION ALL
                        (SELECT MIN(id) as id,
                        company_id,
                        product_id,
                        SUM(quantity) as quantity,
                        date
                        FROM
                        (
                            (SELECT
                                stock_move.id AS id,
                                stock_move.id AS move_id,
                                dest_location.id AS location_id,
                                dest_location.company_id AS company_id,
                                stock_move.product_id AS product_id,
                                product_template.id AS product_template_id,
                                product_template.categ_id AS product_categ_id,
                                quant.qty AS quantity,
                                stock_move.date AS date,
                                quant.cost as price_unit_on_quant,
                                stock_move.origin AS source,
                                stock_production_lot.name AS serial_number
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
                            WHERE quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
                            AND (
                                not (source_location.company_id is null and dest_location.company_id is null) or
                                source_location.company_id != dest_location.company_id or
                                source_location.usage not in ('internal', 'transit'))
                            )
                            UNION ALL
                            (SELECT
                                (-1) * stock_move.id AS id,
                                stock_move.id AS move_id,
                                source_location.id AS location_id,
                                source_location.company_id AS company_id,
                                stock_move.product_id AS product_id,
                                product_template.id AS product_template_id,
                                product_template.categ_id AS product_categ_id,
                                - quant.qty AS quantity,
                                stock_move.date AS date,
                                quant.cost as price_unit_on_quant,
                                stock_move.origin AS source,
                                stock_production_lot.name AS serial_number
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
                            WHERE quant.qty>0 AND stock_move.state = 'done' AND source_location.usage in ('internal', 'transit')
                            AND (
                                not (dest_location.company_id is null and source_location.company_id is null) or
                                dest_location.company_id != source_location.company_id or
                                dest_location.usage not in ('internal', 'transit'))
                            )
                        )AS fooo
                            GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, source, product_template_id
                        )
                    )AS foo
                        GROUP BY company_id, product_id, date
                )""")
