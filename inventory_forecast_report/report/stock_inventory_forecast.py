# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.fields import Datetime as fieldsDatetime


class StockInventoryForecast(models.Model):
    _name = 'stock.inventory.forecast'
    _auto = False
    _order = 'date'

    company_id = fields.Many2one('res.company', 'Company')
    product_id = fields.Many2one('product.product', 'Product Variant', required=True)
    product_template_id = fields.Many2one('product.template', 'Product', required=True)
    quantity = fields.Float('Quantity On Hand')
    date = fields.Datetime('Operation Date')
    source = fields.Char('SOURCE')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_inventory_forecast')
        self._cr.execute("""
            CREATE VIEW stock_inventory_forecast AS (
              SELECT MIN(id) AS id,
                   company_id,
                   product_template_id,
                   product_id,
                   SUM(quantity) AS quantity,
                   date, SOURCE as source
            FROM (
                    (SELECT MIN(id) AS id,
                            company_id,
                            product_template_id,
                            product_id,
                            SUM(quantity) AS quantity, date, SOURCE as source
                     FROM
                       (SELECT MIN(id) as id,
                               company_id,
                               product_template_id,
                               product_id,
                               SUM(quantity) AS quantity, date, SOURCE as source
                        FROM (
                                SELECT sale_order_line.id AS id,
                                        sorder.company_id AS company_id,
                                        product_product.product_tmpl_id AS product_template_id,
                                        sale_order_line.product_id AS product_id,
                                        - sale_order_line.product_uom_qty * 30/100 AS quantity,
                                        sorder.date_order AS date,
                                        sorder.name as SOURCE
                                FROM sale_order AS sorder
                                JOIN sale_order_line ON sale_order_line.order_id = sorder.id
                                JOIN product_product ON product_product.id = sale_order_line.product_id
                                JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                WHERE sorder.state IN ('draft','sent') and product_template.is_forecast_report = 't'
                              UNION ALL
                                SELECT sale_order_line.id AS id,
                                        sorder.company_id AS company_id,
                                        product_product.product_tmpl_id AS product_template_id,
                                        sale_order_line.product_id AS product_id,
                                        - (ABS(sale_order_line.product_uom_qty - sale_order_line.qty_delivered)) AS quantity,
                                        sorder.confirmation_date AS date,
                                        sorder.name as SOURCE
                                FROM sale_order AS sorder
                                JOIN sale_order_line ON sale_order_line.order_id = sorder.id
                                JOIN product_product ON product_product.id = sale_order_line.product_id
                                JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                WHERE sorder.state = 'sale' and (sale_order_line.product_uom_qty - sale_order_line.qty_delivered) != 0 and product_template.is_forecast_report = 't'
                                ) AS SaleOrderTable GROUP BY company_id, product_template_id, product_id, SOURCE, date
                              UNION ALL
                                SELECT (-1) * purchase_order_line.id AS id,
                                        porder.company_id AS company_id,
                                        product_product.product_tmpl_id AS product_template_id,
                                        purchase_order_line.product_id AS product_id,
                                        ABS(purchase_order_line.product_qty - purchase_order_line.qty_received) AS quantity,
                                        porder.date_order AS date,
                                        porder.name as SOURCE
                                FROM purchase_order AS porder
                                JOIN purchase_order_line ON purchase_order_line.order_id = porder.id
                                JOIN product_product ON product_product.id = purchase_order_line.product_id
                                JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                WHERE porder.state not in ('cancel') and (purchase_order_line.product_qty - purchase_order_line.qty_received) != 0 and product_template.is_forecast_report = 't'
                            )AS PSOTable GROUP BY company_id, product_template_id, product_id, SOURCE, date
                        )
                        UNION ALL
                        (SELECT MIN(id) AS id,
                                company_id,
                                product_template_id,
                                product_id,
                                SUM(quantity) AS quantity,
                                date,
                                SOURCE as source
                        FROM (
                                (SELECT stock_move.id AS id,
                                         stock_move.id AS move_id,
                                         dest_location.id AS location_id,
                                         dest_location.company_id AS company_id,
                                         stock_move.product_id AS product_id,
                                         product_product.product_tmpl_id AS product_template_id,
                                         product_template.categ_id AS product_categ_id,
                                         quant.qty AS quantity,
                                         stock_move.date AS date,
                                         quant.cost AS price_unit_on_quant,
                                         stock_move.origin AS SOURCE,
                                         stock_production_lot.name AS serial_number
                                FROM stock_quant AS quant
                                JOIN stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                                JOIN stock_move ON stock_move.id = stock_quant_move_rel.move_id
                                LEFT JOIN stock_production_lot ON stock_production_lot.id = quant.lot_id
                                JOIN stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                                JOIN stock_location source_location ON stock_move.location_id = source_location.id
                                JOIN product_product ON product_product.id = stock_move.product_id
                                JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                WHERE quant.qty>0
                                AND product_template.is_forecast_report = 't'
                                AND stock_move.state = 'done'
                                AND dest_location.usage IN ('internal', 'transit')
                                AND (NOT (source_location.company_id IS NULL AND dest_location.company_id IS NULL)
                                     OR source_location.company_id != dest_location.company_id
                                     OR source_location.usage NOT IN ('internal', 'transit')) )
                               UNION ALL
                                (SELECT
                                    (-1) * stock_move.id AS id,
                                    stock_move.id AS move_id,
                                    source_location.id AS location_id,
                                    source_location.company_id AS company_id,
                                    stock_move.product_id AS product_id,
                                    product_product.product_tmpl_id AS product_template_id,
                                    product_template.categ_id AS product_categ_id,
                                    - quant.qty AS quantity,
                                    stock_move.date AS date,
                                    quant.cost AS price_unit_on_quant,
                                    stock_move.origin AS SOURCE,
                                    stock_production_lot.name AS serial_number
                                FROM stock_quant AS quant
                                JOIN stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                                JOIN stock_move ON stock_move.id = stock_quant_move_rel.move_id
                                LEFT JOIN stock_production_lot ON stock_production_lot.id = quant.lot_id
                                JOIN stock_location source_location ON stock_move.location_id = source_location.id
                                JOIN stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                                JOIN product_product ON product_product.id = stock_move.product_id
                                JOIN product_template ON product_template.id = product_product.product_tmpl_id
                                WHERE quant.qty>0
                                    AND product_template.is_forecast_report = 't'
                                    AND stock_move.state = 'done'
                                    AND source_location.usage IN ('internal', 'transit')
                                    AND (NOT (dest_location.company_id IS NULL
                                    AND source_location.company_id IS NULL)
                                        OR dest_location.company_id != source_location.company_id
                                        OR dest_location.usage NOT IN ('internal', 'transit'))
                                )
                                )AS fooo
                                        GROUP BY move_id, location_id, company_id, product_id, product_categ_id, date, SOURCE, product_template_id
                        )) AS fooo
                                GROUP BY company_id, product_template_id, product_id, SOURCE, date
                                order by date
                    )""")
