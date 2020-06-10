
from odoo import fields, models

class AccountJournal(models.Model):

    _inherit = 'account.journal'

    active = fields.Boolean(default=True)