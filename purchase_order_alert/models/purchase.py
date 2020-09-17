from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            for val in order.order_line:
                config = self.env['alert.config'].search([('product_tmpl_id', '=',val.product_id.product_tmpl_id.id),('active', '=',True)], order='id desc')
                if config:
                    alert = self.env['purchaseorder.alert'].create({'reference': order.name,'purchase_id':order.id})
                    for val1 in config[0].alert_config_line:
                        self.env['purchaseorder.alert.line'].create({'line_id': alert.id,
                                                                     'product_id':val1.product_id.id,
                                                                     'name':val1.product_id.name,
                                                                     'price_unit':val1.product_id.standard_price,
                                                                     'quantity':val1.product_qty * val.product_qty,
                                                                     'purchase_id':order.id})
                else:
                    pass

        return True

