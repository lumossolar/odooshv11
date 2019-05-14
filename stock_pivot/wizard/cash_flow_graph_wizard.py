# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api,_

from odoo.exceptions import ValidationError,UserError

from datetime import timedelta, datetime
import arrow
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class CashFLowGraphWizard(models.TransientModel):

    _name = 'cash.flow.graph.wizard'

    name = fields.Char('Name')
    date =fields.Date('Date', default=fields.Date.context_today,readonly=True)
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    report_type = fields.Selection([
        ('this_month', 'This Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
    ], "Report Type",default="this_month")

    @api.model
    def default_get(self, fields):
        result = super(CashFLowGraphWizard, self).default_get(fields)
        result['date_from'] = str(arrow.utcnow().span('month')[0].date())
        result['date_to'] = str(arrow.utcnow().span('month')[-1].date())
        return result

    @api.onchange('report_type')
    def onchange_report_type(self):
        if self.report_type == 'this_month':
            self.date_from = arrow.utcnow().span('month')[0].date()
            self.date_to =  arrow.utcnow().span('month')[-1].date()
        elif self.report_type == 'this_quarter':
            self.date_from = arrow.utcnow().span('quarter')[0].date()
            self.date_to = arrow.utcnow().span('quarter')[-1].date()
        elif self.report_type == 'this_year':
            self.date_from = arrow.utcnow().span('year')[0].date()
            self.date_to = arrow.utcnow().span('year')[-1].date()

    def action_generate_graph(self):
        self.env.cr.execute("""DELETE FROM cash_flow_report_pivot;""")
        report_id = self.env['account.financial.html.report'].search([('name', 'ilike', 'Cash Flow Statement')])
        context_data = self.env['account.report.context.common'].return_context('account.financial.html.report', {},report_id.id)

        self = self.env[context_data[0]].browse(context_data[1])
        self.date_from = self.date_from
        self.date_to = self.date_to
        self.date_filter = 'custom'
        lines = report_id.with_context(no_format=True, print_mode=True).get_lines(self)
        # data = self.env[context_data[0]].browse(context_data[1]).get_html_and_data({'name':"Ruby",'cash_pivot_view':True,'date_from':date_from ,'date_to': '2019-12-31'})
        print("==== lines  in wizard ======", lines)
        parent_id = False
        for l in lines:
            print("lllllllllllll............",l)
            amount = l.get('columns')[0]
            if not amount:
                amount = 0.00
            cr = self._cr
            print("0-9-0809786875764654543............", l.get('level'), l.get('type'))
            if l.get('level') == 0 and l.get('type') == 'line':
                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': None,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                print("====== level 0 and type line   ===", l.get('name'), parent_id)
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                                                                                VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                                                                                RETURNING id """,params)
                # cf_rec = self.env['cash.flow.report.pivot'].browse(cr.fetchone()[0])
                # parent_id = cf_rec.id
            elif l.get('level') == 1 and l.get('type') == 'line':
                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': None,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                print("====== level 1 and type line   ===", l.get('name'), parent_id)
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                                                                               VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                                                                               RETURNING id """, params)
                # cf_rec = self.env['cash.flow.report.pivot'].browse(cr.fetchone()[0])
                # parent_id = cf_rec.id

            elif l.get('level') == 2:

                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': None,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                   VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                   RETURNING id """, params)
                cf_rec = self.env['cash.flow.report.pivot'].browse(cr.fetchone()[0])
                parent_id = cf_rec.id

                print("...level 2........", l.get('name'), parent_id)

            elif l.get('level') == 3:
                print(" ### level 3 ##", l.get('name'), parent_id)

                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': parent_id,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                       VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                       RETURNING id """, params)
                # cf_rec = self.env['cash.flow.report.pivot'].browse(cr.fetchone()[0])
                # parent_id = cf_rec.id
            elif l.get('type') != 'line':
                print("type not line..", l.get('name'), parent_id)
                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': parent_id,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                                       VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                                       RETURNING id """, params)

            else:
                print("In else.", l.get('name'), parent_id)
                params = {
                    'name': l.get('name'),
                    'amount': amount,
                    'parent_id': None,
                    'level': l.get('level'),
                    'date': l.get('parent_id'),
                    'unfoldable': l.get('unfoldable'),
                }
                cr.execute(""" INSERT INTO cash_flow_report_pivot (name,amount,parent_id,level,date,unfoldable)
                                                                      VALUES (%(name)s, %(amount)s, %(parent_id)s, %(level)s, %(date)s,%(unfoldable)s)
                                                                      RETURNING id """, params)

        return {'type': 'ir.actions.act_window',
                'name': 'Cash Flow Report',
                'view_type': 'graph',
                'view_mode': 'graph',
                'res_model': 'cash.flow.report.pivot',
                'res_id': self.id,
                }



