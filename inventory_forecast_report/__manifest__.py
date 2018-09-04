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
        'views/product_view.xml',
        'report/stock_inventory_forecast_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
