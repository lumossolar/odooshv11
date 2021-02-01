# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Un-link PO',
    'version' : '1.1',
    'summary': '',
    'description': """
This module help to unlink PO automatically from picking order.
    """,
    'category': 'Custom',
    'website': 'https://www.flexsin.com',
    'images' : [],
    'depends' : ['base','stock'],
    'data': [
        'views/stock_picking.xml',
    ],
    'demo': [],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}