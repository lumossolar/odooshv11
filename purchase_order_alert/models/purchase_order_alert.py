from odoo import api, fields, models, _
from datetime import date


class PurchaseorderAlert(models.Model):
    _name = 'purchaseorder.alert'
    _order = 'id desc'
    _description = "Purchase Order Alert"

    def action_done(self):
        for val in self:
            if val.purchaseorder_alert_line:
                for val1 in val.purchaseorder_alert_line:
                    if val1.product_id.seller_ids:
                        vendor = val1.product_id.seller_ids[0]
                        vendor_id = vendor.name
                    else:
                        vendor_id = val.purchase_id.partner_id
                    purchase = self.env['purchase.order'].create({'partner_id':vendor_id.id})
                    self.env['purchase.order.line'].create({'order_id': purchase.id,'name':val1.product_id.name,
                                                            'product_id':val1.product_id.id,
                                                            'product_qty':val1.quantity,'price_unit':val1.price_unit,
                                                            'product_uom':val1.product_id.uom_id.id,
                                                            'date_planned':date.today()})
        self.write({'state':'done'})

    def action_cancel(self):
        self.write({'state':'cancel'})

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('purchase_alert')
        if seq:
            vals['name'] = 'AL' + str(seq)
        seq_id = super(PurchaseorderAlert, self).create(vals)
        return seq_id


    name = fields.Char('Alert No.')
    reference = fields.Char('Reference')
    purchase_id = fields.Many2one('purchase.order','Reference Id')
    date = fields.Datetime('Date', default=lambda self: fields.datetime.now())
    created_by = fields.Many2one('res.users','Create By', default=lambda self: self.env.user)
    purchaseorder_alert_line = fields.One2many('purchaseorder.alert.line','line_id','Line')
    state = fields.Selection([('draft', 'Pending'),
                              ('process', 'Process'),
                              ('done', 'Confirm'),
                              ('cancel', 'Cancel'),],
                             'Status', readonly=True, default="draft")
    remark = fields.Char('Remark', compute='get_remark')

    def get_remark(self):
        for val in self:
            l = len(self.env['purchaseorder.alert.line'].search([('line_id', '=', val.id), ('status', '=', False)]))
            if l:
                val.remark = str(l) + ' ' + 'Lines Pendding'
            else:
                val.remark = 'Complete'
        return True




class PurchaseorderAlertLine(models.Model):
    _name = 'purchaseorder.alert.line'
    _description = "Purchase Order Alert Line"

    def action_done(self):
        for val in self:
            if val.status == False:
                if val.product_id.seller_ids:
                    vendor = val.product_id.seller_ids[0]
                    vendor_id = vendor.name
                else:
                    vendor_id = val.purchase_id.partner_id
                purchase = self.env['purchase.order'].create({'partner_id':vendor_id.id})
                self.env['purchase.order.line'].create({'order_id': purchase.id,'name':val.product_id.name,
                                                        'product_id':val.product_id.id,
                                                        'product_qty':val.quantity,'price_unit':val.price_unit,
                                                        'product_uom':val.product_id.uom_id.id,
                                                        'date_planned':date.today()})

            l = len(self.env['purchaseorder.alert.line'].search([('line_id', '=', val.line_id.id), ('status', '=', False)]))
            if l == 1:
                val.line_id.update({'state': 'done'})
            else:
                val.line_id.update({'state': 'process'})
            val.write({'status':True})

    line_id = fields.Many2one('purchaseorder.alert','Id')
    product_id = fields.Many2one('product.product','Product')
    name = fields.Char('Description')
    quantity = fields.Float('Quantity')
    price_unit = fields.Float('Unit Price')
    status = fields.Boolean('Status', default=False)
    purchase_id = fields.Many2one('purchase.order', 'Reference Id')