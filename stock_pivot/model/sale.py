# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import smtplib, ssl


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    probability = fields.Float('Probability(%)',default=30)




