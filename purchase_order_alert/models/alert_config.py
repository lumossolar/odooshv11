from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
class AlertConfig(models.Model):
    _name = 'alert.config'
    _order = 'id desc'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    active = fields.Boolean('Active', default=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product',domain="[('type', 'in', ['product', 'consu'])]", required=True)
    product_id = fields.Many2one('product.product', 'Product Variant',
        domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu'])]",)
    product_qty = fields.Float('Quantity', default=1.0, digits=dp.get_precision('Unit of Measure'), required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id, oldname='product_uom', required=True,)
    sequence = fields.Integer('Sequence')

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.bom'),
        required=True)

    alert_config_line = fields.One2many('alert.config.line','line_id','Line')


    def name_get(self):
        return [(bom.id, '%s' % (bom.product_tmpl_id.display_name)) for bom in self]





class AlertConfigLine(models.Model):
    _name = 'alert.config.line'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    line_id = fields.Many2one('alert.config','Id')
    sequence = fields.Integer('Sequence', default=1,)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float('Product Quantity', default=1.0, digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure',default=_get_default_product_uom_id,oldname='product_uom', required=True,)