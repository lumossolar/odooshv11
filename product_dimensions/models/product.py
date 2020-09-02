from odoo import api, fields, models,_

class ProductTemplate(models.Model):
    _inherit = "product.template"

    height = fields.Float('Height')
    width = fields.Float('Width')
    length = fields.Float('Length')

