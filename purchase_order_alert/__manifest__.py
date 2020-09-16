# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Order Alert',
    'summary': '',
    'description': """
===============================
    """,
    'website': 'https://www.flexsin.com',
    'depends': ['purchase'],
    'category': 'Custom Dev',
    'data': [
        'views/purchase_order_alert.xml',
        'views/alert_config.xml',
        'views/sequence_view.xml',
        'security/for_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': True,
}
