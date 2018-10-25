# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY,WEEKLY
import pandas as pd

class TotalStcokReportForecast(models.Model):
    _name = "total.stock.report.forecast"

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template',related='product_id.product_tmpl_id', readonly=True)
    quantity = fields.Float(readonly=True)
    date = fields.Date('Date')

    @api.multi
    def do_open(self):
        cr = self.env.cr
        self.env.cr.execute("""DELETE FROM total_stock_report_forecast;""")
        is_forecast = 't'
        cr.execute('select p.id from product_template as pt JOIN product_product  p on  p.product_tmpl_id = pt.id where pt.is_forecast = %s ',(is_forecast,))
        p_ids = cr.fetchall()
        today = datetime.now().date()
        a = today - timedelta(days=today.weekday())
        b = datetime.now().replace(month=12, day=31, hour=0, minute=0, second=0)
        dw_list = [dt for dt in rrule(WEEKLY, dtstart=a, until=b)]
        product_obj = self.env['product.product']
        for p in p_ids:
            prod_id = p[0]
            qty_available = product_obj.browse(prod_id).qty_available or 0.00
            for d in dw_list:
                dr = pd.date_range(start=d, periods=7)
                d_start = dr[0].strftime("%Y-%m-%d")
                d_end = dr[-1].strftime("%Y-%m-%d")

                query = """
                          SELECT
                              sum(sl.product_uom_qty) * .30
                          FROM
                              sale_order_line sl
                              JOIN sale_order s ON sl.order_id=s.id
                          WHERE
                              s.state IN ('draft','sent')
                              AND sl.product_id = %s
                              AND (to_char(s.date_order, 'YYYY-MM-DD') BETWEEN %s AND %s)
                          """
                self.env.cr.execute(query, (prod_id, d_start, d_end))
                sl_ids = cr.fetchone()
                s_qty = [x if x != None else 0 for x in sl_ids]

                query1 = """
                             SELECT
                                 sum(sl.product_uom_qty)
                             FROM
                                 sale_order_line sl
                                 JOIN sale_order s ON sl.order_id=s.id
                             WHERE
                                 s.state IN ('sale')
                                 AND sl.product_id = %s
                                 AND (to_char(s.confirmation_date, 'YYYY-MM-DD') BETWEEN %s AND %s)
                             """
                self.env.cr.execute(query1, (prod_id, d_start, d_end))
                sl_d_ids = cr.fetchone()
                sd_qty = [x if x != None else 0 for x in sl_d_ids]
                
                query2 = """
                             SELECT
                                 sum(pl.product_qty)
                             FROM
                                 purchase_order_line pl
                                 JOIN purchase_order p ON pl.order_id=p.id
                             WHERE
                                 p.state not IN ('cancel')
                                 AND pl.product_id = %s
                                 AND (to_char(pl.date_planned, 'YYYY-MM-DD') BETWEEN %s AND %s)
                             """
                self.env.cr.execute(query2, (prod_id, d_start, d_end))
                pl_ids = cr.fetchone()
                p_qty = [x if x != None else 0 for x in pl_ids]
                d_qty = p_qty[0] - (s_qty[0] + sd_qty[0])
                qty_available = round(qty_available + d_qty)
                cr.execute("""INSERT INTO total_stock_report_forecast (date, product_id, quantity)
                                                                       VALUES (%s, %s, %s)""",
                           (d_start, prod_id, qty_available))

        ir_model_data = self.env['ir.model.data']
        stock_forecast_pivot = ir_model_data.get_object_reference('stock_pivot', 'view_forecast_all_pivot')[1]
        return {'type': 'ir.actions.act_window',
                'name': 'Stock Level forecast',
                'view_mode': 'pivot',
                'view_type': 'pivot',
                'view_id': stock_forecast_pivot,
                'res_model': 'total.stock.report.forecast',
                'res_id': self.id,
                }

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(TotalStcokReportForecast, self.with_context(virtual_id=False)).read_group(domain, fields, groupby, offset=offset,
                                                                              limit=limit, orderby=orderby, lazy=lazy)

        p_obj = self.env['product.product']
        for row in result:
            if not row.get('product_id'):
                row['quantity'] = ''
            else:
                if len(row.get('__domain')) == 1:
                    cr = self.env.cr
                    prod_id = row.get('product_id')[0]
                    dt = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
                    dt = dt.strftime("%Y-%m-%d")
                    qty_available  = p_obj.browse(row.get('product_id')[0]).qty_available
                    row['quantity'] = qty_available

        return result

class product_template(models.Model):
    _inherit = "product.template"

    is_forecast = fields.Boolean('Is Forecast')






