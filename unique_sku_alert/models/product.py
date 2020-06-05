from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = 'Product Template'

    _sql_constraints = [
        ('default_code_unique', 'unique (default_code)', 'SKU already exists!')]


