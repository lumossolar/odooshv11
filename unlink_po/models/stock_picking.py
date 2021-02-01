from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_unlink(self):
        for obj in self:
            if obj.picking_type_id.sequence_code =='PICK':
                stock_move = obj.env['stock.move'].search([('picking_id', '=', obj.id),('state', '=', 'waiting'),('procure_method', '=', 'make_to_order')])
                for move in stock_move:
                    move.update({'procure_method':'make_to_stock'})
                obj.call_unlink = 1
            else:
                obj.call_unlink = 0

    def call_action_unlink(self):
        for val in self:
            val.action_unlink()


    call_unlink = fields.Integer(compute='call_action_unlink', string='Call action unlink',default=0)





