from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = 'Product Template'

    custom_field = fields.Char("Testing Field")

