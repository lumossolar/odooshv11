from odoo import fields, models

class ProductDimensions(models.Model):
    _name = 'product.dimensions'

    def action_done(self):
        for val in self:
            for val1 in val.product_dimensions_line:
                val1.product_id.update({'volume':val1.volume,'weight':val1.weight,'height':val1.height,'width':val1.width,'length':val1.length,})
        self.write({'state':'done'})

    def action_cancel(self):
        self.write({'state':'cancel'})


    name = fields.Char('Reference')
    date = fields.Datetime('Date', default=lambda self: fields.datetime.now())
    created_by = fields.Many2one('res.users','Responsible', default=lambda self: self.env.user)
    product_dimensions_line = fields.One2many('product.dimensions.line','line_id','Line')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel'),],
                             'Status', readonly=True, default="draft")


class ProductDimensionsLine(models.Model):
    _name = 'product.dimensions.line'

    line_id = fields.Many2one('product.dimensions','Id')
    product_id = fields.Many2one('product.product','Product')
    height = fields.Float('Height')
    width = fields.Float('Width')
    length = fields.Float('Length')
    volume = fields.Float('Volume')
    weight = fields.Float('Weight')