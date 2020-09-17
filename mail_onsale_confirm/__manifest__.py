# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mail on sale order confirm',
    'summary': '',
    'description': """
Mail on sale order confirm
===============================
    """,
    'website': 'https://www.flexsin.com',
    'depends': ['sale_management','sale'],
    'category': 'Custom Dev',
    'data': [
        # 'security/ir.model.access.csv',

        'views/mail_template.xml',
    ],
    'installable': True,
    'auto_install': True,
}
