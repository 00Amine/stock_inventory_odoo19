from odoo import models, fields, api

class StockQuantity(models.Model):
    _name = 'stock.quantity'
    _description = 'Quantité de stock par emplacement'

    product_id = fields.Many2one('stock.produits', string="Produit", required=True)
    emplacement_id = fields.Many2one('stock.emplacement', string="Emplacement", required=True)
    quantity = fields.Float(string="Quantité", default=0.0)

    _constraints = [
        models.Constraint(
            "UNIQUE(product_id, emplacement_id)",
            message="Un produit ne peut avoir qu'une seule quantité par emplacement."
        )
    ]
    @api.model
    def update_stock(self, product_id, emplacement_id, quantity_change):
        stock_quantity = self.search([
            ('product_id', '=', product_id),
            ('emplacement_id', '=', emplacement_id)
        ], limit=1)

        if stock_quantity:
            stock_quantity.quantity += quantity_change
        else:
            self.create({
                'product_id': product_id,
                'emplacement_id': emplacement_id,
                'quantity': quantity_change
            })

    # --- THIS IS THE FIX ---
    @api.model
    # --- END OF FIX ---
    def get_stock_quantity(self, product_id, emplacement_id):
        stock_quantity = self.search([
            ('product_id', '=', product_id),
            ('emplacement_id', '=', emplacement_id)
        ], limit=1)
        return stock_quantity.quantity if stock_quantity else 0.0
