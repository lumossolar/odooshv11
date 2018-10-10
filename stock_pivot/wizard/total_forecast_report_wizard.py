# -*- coding: utf-8 -*-
from openerp import api, fields, models
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY,WEEKLY
import base64
import xml.etree.ElementTree as ET
from collections import namedtuple

from odoo import api, exceptions, fields, models, _


class total_forecast_report_wizard(models.TransientModel):
    _name = 'total.forecast.report.wizard'
    
    name = fields.Char('Name')

    @api.multi
    def do_open(self):
        cr = self.env.cr
        self.env.cr.execute("""DELETE FROM total_stock_report_forecast;""")
        cr.execute('SELECT id FROM product_product')
        p_ids = cr.fetchall()
        # a = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
        today = datetime.now().date()
        a = today - timedelta(days=today.weekday())
        b = datetime.now().replace(month=12, day=31,hour=0,minute=0,second=0)
        dw_list = [dt for dt in rrule(WEEKLY, dtstart=a, until=b)]
        product_obj = self.env['product.product']
        for p in p_ids:
            prod_id = p[0]
            qty_available = product_obj.browse(prod_id).qty_available or 0.00
            total_qty = 0.00

            for d in dw_list:
                e = d + timedelta(days=7)
                dst = d.strftime("%Y-%m-%d")
                d_list = [a.strftime("%Y-%m-%d") for a in rrule(DAILY, dtstart=d, until=e)]
                tot_qty = 0.00
                for dt in d_list:
                    d_qty = 0.00
                    # cr.execute("SELECT quant.qty AS quantity FROM stock_quant as quant JOIN stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id JOIN stock_move ON stock_move.id = stock_quant_move_rel.move_id LEFT JOIN  stock_production_lot ON stock_production_lot.id = quant.lot_id JOIN stock_location dest_location ON stock_move.location_dest_id = dest_location.id JOIN stock_location source_location ON stock_move.location_id = source_location.id JOIN product_product ON product_product.id = stock_move.product_id JOIN product_template ON product_template.id = product_product.product_tmpl_id WHERE quant.qty > 0 AND stock_move.state = \"done\" AND dest_location.usage in (\"internal\", \"transit\") AND (not (source_location.company_id is null and dest_location.company_id is null) or\n    source_location.company_id != dest_location.company_id or source_location.usage not in (\"internal\", \"transit\"))"
                    #
                    # q = """
                    #            SELECT
                    #                sum(quant.qty) AS quantity, date,
                    # COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                    # source,
                    # string_agg(DISTINCT serial_number, ', ' ORDER BY serial_number) AS serial_number
                    #            FROM
                    #                stock_quant as quant JOIN stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id JOIN
                    #     stock_move ON stock_move.id = stock_quant_move_rel.move_id LEFT JOIN
                    #     stock_production_lot ON stock_production_lot.id = quant.lot_id JOIN
                    #     stock_location dest_location ON stock_move.location_dest_id = dest_location.id JOIN
                    #     stock_location source_location ON stock_move.location_id = source_location.id JOIN
                    #     product_product ON product_product.id = stock_move.product_id
                    # JOIN
                    #     product_template ON product_template.id = product_product.product_tmpl_id
                    #            WHERE
                    #                 quant.qty>0 AND stock_move.state = 'done' AND dest_location.usage in ('internal', 'transit')
                    #                AND quant.product_id = %s
                    #                AND (
                    #                     not (source_location.company_id is null and dest_location.company_id is null) or
                    #                     source_location.company_id != dest_location.company_id or
                    #                     source_location.usage not in ('internal', 'transit'))
                    #            """

                    # self.env.cr.execute(q, (prod_id))

                    # q_ids = cr.fetchone()
                    # quantity_on_hand = [x if x != None else 0 for x in q_ids]

                    # cr.execute("""SELECT sum(q.qty) from stock_quant as q where product_id = %s AND to_char(q.in_date, 'YYYY-MM-DD')=%s""" % (prod_id, str(dt)))
                    # q_ids = cr.fetchall()
                    # qty_available = [x if x != None else 0 for x in q_ids]

                    query = """
                               SELECT
                                   sum(sl.product_uom_qty) * .30
                               FROM
                                   sale_order_line sl
                                   JOIN sale_order s ON sl.order_id=s.id
                               WHERE
                                   s.state IN ('sale')
                                   AND sl.product_id = %s
                                   AND to_char(s.confirmation_date, 'YYYY-MM-DD')=%s
                               """
                    self.env.cr.execute(query, (prod_id,dt))
                    sl_ids = cr.fetchone()
                    s_qty = [x if x!=None else 0 for x in sl_ids]

                    query1 = """
                              SELECT
                                  sum(sl.product_uom_qty)
                              FROM
                                  sale_order_line sl
                                  JOIN sale_order s ON sl.order_id=s.id
                              WHERE
                                  s.state IN ('draft')
                                  AND sl.product_id = %s
                                  AND to_char(s.date_order, 'YYYY-MM-DD')=%s
                              """
                    self.env.cr.execute(query1, (prod_id, dt))
                    sl_d_ids = cr.fetchone()
                    sd_qty = [x if x != None else 0 for x in sl_d_ids]

                    query2 = """
                              SELECT
                                  sum(pl.product_qty)
                              FROM
                                  purchase_order_line pl
                                  JOIN purchase_order p ON pl.order_id=p.id
                              WHERE
                                  p.state IN ('draft')
                                  AND pl.product_id = %s
                                  AND to_char(p.date_order, 'YYYY-MM-DD')=%s
                              """
                    self.env.cr.execute(query2, (prod_id, dt))
                    pl_ids = cr.fetchone()
                    p_qty = [x if x != None else 0 for x in pl_ids]

                    d_qty =  s_qty[0] + sd_qty[0] + p_qty[0]
                    tot_qty+=d_qty

                qty_available +=  tot_qty

                cr.execute("""INSERT INTO total_stock_report_forecast (date, product_id, quantity)
                                                        VALUES (%s, %s, %s)""",
                                 (dst, prod_id,round(qty_available)))

        ir_model_data = self.env['ir.model.data']
        stock_forecast_pivot = ir_model_data.get_object_reference('stock_pivot', 'view_forecast_all_pivot')[1]
        return  {'type': 'ir.actions.act_window',
            'name': 'Stock Level forecast',
            'view_mode': 'pivot',
            'view_type': 'pivot',
            'view_id': stock_forecast_pivot,
            'res_model': 'total.stock.report.forecast',
            'res_id': self.id,
            }


