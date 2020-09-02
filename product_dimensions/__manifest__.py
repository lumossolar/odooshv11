# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Dimensions',
    'summary': '',
    'description': """
===============================
    """,
    'website': 'https://www.flexsin.com',
    'depends': ['stock'],
    'category': 'Custom Dev',
    'data': [
        'views/product_dimensions.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'auto_install': True,
}
