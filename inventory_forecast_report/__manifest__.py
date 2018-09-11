# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inventory Forecast Report',
    'summary': 'Inventory',
    'description': """
Stock Inventory Forecast Report
===============================
* Stock Inventory Forecast Report
    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'depends': ['sale', 'stock_account', 'purchase'],
    'category': 'Custom Dev',
    'data': [
        'security/ir.model.access.csv',
        'report/stock_inventory_forecast_views.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
