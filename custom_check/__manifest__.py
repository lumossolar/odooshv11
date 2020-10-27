# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Custom Check',
    'version' : '1.1',
    'summary': '',
    'description': """
    """,
    'category': 'Custom',
    'website': 'https://www.flexsin.com',
    'images' : [],
    'depends' : ['product'],
    'data': ['reports/custom_check_report.xml',
                'views/custom_check_template.xml',
    ],
    'demo': [],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}