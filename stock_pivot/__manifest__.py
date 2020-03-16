# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Modified Pivot View in ERP Application',
    'version' : '1.1',
    'summary': 'Pivot View',
    'sequence': 30,
    'description': """
This module modify stock pivot view.
    """,
    'category': 'Custom',
    'website': 'https://www.flexsin.com',
    'images' : [],
    'depends' : ['stock','product','sale','purchase'],
    'data': [
        'views/stock_pivot_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
