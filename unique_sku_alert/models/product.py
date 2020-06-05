from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = 'Product Template'

    @api.constrains('default_code')
    def _check_default_code(self):
        code = self.search([('default_code', '=', self.default_code)])
        print 'lengthhhhhhhhhhhhhhhh',len(code),self.default_code
        if len(code) > 1:
            raise UserError(_('"SKU already exists!"'))

    # _sql_constraints = [
    #     ('default_code_unique', 'unique (default_code)', 'SKU already exists!')]


