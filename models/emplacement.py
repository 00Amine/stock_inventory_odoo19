from odoo import models, fields, api, exceptions

class Emplacement(models.Model):
    _name = 'stock.emplacement'
    _description = 'Emplacements de stockage.'

    name = fields.Char(string="Nom", required=True)
    type = fields.Selection(
        [('int', 'Interne'), ('ext', 'Externe')],
        string="Type",
        required=True
    )
    capacity = fields.Float(string="Capacité", required=True)
    product_ids = fields.One2many('stock.produits', 'emplacement_id', string="Produits")
    @api.constrains('capacity')
    def _check_capacity(self):
        for record in self:
            if record.capacity <= 0:
                raise exceptions.ValidationError("La capacité doit être > 0.")