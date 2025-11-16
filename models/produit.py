from odoo import models, fields, api, exceptions

class Produit(models.Model):
    _name = 'stock.produits'
    _description = 'Produits en stock.'

    name = fields.Char(string="Nom", required=True)
    reference = fields.Char(
        string="Référence",
        required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.produits')
    )
    barcode = fields.Char(string="Code-barres")
    categorie_id = fields.Many2one('categorie.produit', string="Catégorie", required=True)
    emplacement_id = fields.Many2one('stock.emplacement', string="Emplacement", required=True)
    fournisseur_id = fields.Many2one('fournisseur.model', string="Fournisseur", required=True)
    mouvement_ids = fields.One2many('stock.mouvement', 'product_id', string="Mouvements")

    quantity_ids = fields.One2many('stock.quantity', 'product_id', string="Quantités", readonly=True)
    quantity = fields.Float(
        string="Quantité",
        compute="_compute_quantity",
        inverse="_inverse_quantity",
        store=True
    )

    @api.depends('emplacement_id', 'quantity_ids.quantity')
    def _compute_quantity(self):
        for product in self:
            matching = product.quantity_ids.filtered(
                lambda q: q.emplacement_id.id == product.emplacement_id.id
            )
            product.quantity = matching and matching[0].quantity or 0.0

    def _inverse_quantity(self):
        for product in self:
            computed_quantity = self.env['stock.quantity'].get_stock_quantity(
                product_id=product.id,
                emplacement_id=product.emplacement_id.id
            )
            difference = product.quantity - computed_quantity

            if difference != 0:
                if difference > 0:
                    # Positive adjustment: need to add stock.
                    self.env['stock.mouvement'].create({
                        'product_id': product.id,
                        'quantity': abs(difference),
                        'type': 'adjust',
                        'reason': 'Ajustement manuel (ajout)',
                        'emplacement_destination_id': product.emplacement_id.id,
                        'emplacement_source_id': False,
                    })
                else:
                    # Negative adjustment: need to remove stock.
                    self.env['stock.mouvement'].create({
                        'product_id': product.id,
                        'quantity': abs(difference),
                        'type': 'adjust',
                        'reason': 'Ajustement manuel (retrait)',
                        'emplacement_source_id': product.emplacement_id.id,
                        'emplacement_destination_id': False,
                    })
