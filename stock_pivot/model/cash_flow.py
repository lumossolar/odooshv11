# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import datetime, timedelta,date
from dateutil.rrule import rrule, DAILY,WEEKLY

try:
    import pandas as pd
except ImportError:
    pass


class CashFlowReportPivot(models.Model):
    _name = "cash.flow.report.pivot"

    parent_id = fields.Many2one('cash.flow.report.pivot', string='Parent')
    amount = fields.Float()
    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    level = fields.Char(string="Level")
    unfoldable = fields.Boolean('unfoldable')











