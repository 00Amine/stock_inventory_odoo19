# Gestion de Stock et Inventaire (Odoo 18)

## 1. Introduction

Ce projet est un module Odoo conçu pour la gestion des stocks et des inventaires, destiné notamment à l'ENSAO au Maroc. Il permet de :
- Organiser les produits en catégories.
- Gérer les emplacements de stockage (internes et externes).
- Gérer les fournisseurs.
- Suivre les mouvements de stock (entrées, sorties, ajustements).
- Calculer la quantité disponible pour chaque produit.
- Générer des rapports PDF récapitulatifs.

Ce module est entièrement documenté et fournit de nombreux cas d'utilisation afin de faciliter son utilisation et sa maintenance.

---

## 2. Structure du Module

La structure du module est la suivante :

```
stock_inventory_project/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── categorie.py
│   ├── stock_emplacement.py
│   ├── fournisseur.py
│   ├── stock_mouvement.py
│   ├── produit.py
│   └── stock_quantity.py
├── views/
│   ├── categorie_view.xml
│   ├── emplacement_view.xml
│   ├── fournisseur_view.xml
│   ├── produit_view.xml
│   ├── mouvement_view.xml
│   └── stock_quantity_views.xml
├── reports/
│   └── stock_report.xml

```

Le fichier `__manifest__.py` définit les métadonnées du module (nom, version, dépendances, fichiers à charger, etc.).

---

## 3. Modèles (Models)

### 3.1. Categorie (categorie.produit)
**Fichier : `models/categorie.py`**

```python
from odoo import models, fields

class Categorie(models.Model):
    _name = 'categorie.produit'
    _description = 'Organise les produits en catégories.'

    name = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")
```

**Documentation :**  
Ce modèle permet d'organiser les produits en catégories.
- **name** : Nom de la catégorie (obligatoire).
- **description** : Description détaillée de la catégorie.

**Cas d'utilisation :**  
- Création d'une nouvelle catégorie (ex. "Materiel Informatique").

---

### 3.2. Emplacement (stock.emplacement)
**Fichier : `models/stock_emplacement.py`**

```python
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
```

**Documentation :**  
Ce modèle gère les emplacements de stockage.
- **name** : Nom de l'emplacement (obligatoire).
- **type** : Type d'emplacement (Interne ou Externe).
- **capacity** : Capacité maximale (obligatoire).
- **product_ids** : Liste des produits stockés dans cet emplacement.

**Cas d'utilisation :**  
- Création d'un emplacement "Magasin Central" avec une capacité de 1000 unités.

---

### 3.3. Fournisseur (fournisseur.model)
**Fichier : `models/fournisseur.py`**

```python
from odoo import models, fields

class Fournisseur(models.Model):
    _name = 'fournisseur.model'
    _description = 'Gérer les fournisseurs'

    name = fields.Char(string="Nom", required=True)
    phone = fields.Char(string="Téléphone", required=True)
    address = fields.Char(string="Adresse", required=True)
    email = fields.Char(string="Email")
```

**Documentation :**  
Ce modèle gère les fournisseurs.
- **name** : Nom du fournisseur (obligatoire).
- **phone** : Téléphone du fournisseur (obligatoire).
- **address** : Adresse complète (obligatoire).
- **email** : Email du fournisseur.

**Cas d'utilisation :**  
- Ajout d'un fournisseur "Fournisseur Informatique ENSAO".

---

### 3.4. StockMouvement (stock.mouvement)
**Fichier : `models/stock_mouvement.py`**

```python
from odoo import models, fields, api, exceptions

class StockMouvement(models.Model):
    _name = 'stock.mouvement'
    _description = 'Mouvements de stock.'

    product_id = fields.Many2one('stock.produits', string="Produit", required=True)
    quantity = fields.Float(string="Quantité", required=True)
    type = fields.Selection(
        [('in', 'Entrée'), ('out', 'Sortie'), ('adjust', 'Ajustement')],
        string="Type", 
        required=True
    )
    emplacement_source_id = fields.Many2one('stock.emplacement', string="Source")
    emplacement_destination_id = fields.Many2one('stock.emplacement', string="Destination")
    reason = fields.Text(string="Raison")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)

    @api.constrains('type', 'quantity', 'emplacement_source_id')
    def _check_stock_availability(self):
        for mouvement in self:
            if mouvement.quantity <= 0:
                raise exceptions.ValidationError("La quantité doit être supérieure à 0.")
            if mouvement.type == 'out':
                available_qty = self.env['stock.quantity'].get_stock_quantity(
                    product_id=mouvement.product_id.id,
                    emplacement_id=mouvement.emplacement_source_id.id
                )
                if mouvement.quantity > available_qty:
                    raise exceptions.ValidationError(
                        f"Stock insuffisant. Disponible: {available_qty}"
                    )

    def _update_stock_quantity(self):
        """Met à jour la quantité en stock après un mouvement."""
        for mouvement in self:
            if mouvement.type == 'in':
                self.env['stock.quantity'].update_stock(
                    product_id=mouvement.product_id.id,
                    emplacement_id=mouvement.emplacement_destination_id.id,
                    quantity_change=mouvement.quantity
                )
            elif mouvement.type == 'out':
                self.env['stock.quantity'].update_stock(
                    product_id=mouvement.product_id.id,
                    emplacement_id=mouvement.emplacement_source_id.id,
                    quantity_change=-mouvement.quantity
                )
            elif mouvement.type == 'adjust':
                if mouvement.emplacement_destination_id:
                    self.env['stock.quantity'].update_stock(
                        product_id=mouvement.product_id.id,
                        emplacement_id=mouvement.emplacement_destination_id.id,
                        quantity_change=mouvement.quantity
                    )
                elif mouvement.emplacement_source_id:
                    self.env['stock.quantity'].update_stock(
                        product_id=mouvement.product_id.id,
                        emplacement_id=mouvement.emplacement_source_id.id,
                        quantity_change=-mouvement.quantity
                    )

    @api.model
    def create(self, vals):
        mouvement = super(StockMouvement, self).create(vals)
        mouvement._update_stock_quantity()
        return mouvement
```

**Documentation :**  
Ce modèle enregistre les mouvements de stock.
- **product_id** : Produit concerné.
- **quantity** : Quantité déplacée.
- **type** : Type de mouvement ("Entrée", "Sortie" ou "Ajustement").
- **emplacement_source_id** : Emplacement de départ (pour les sorties).
- **emplacement_destination_id** : Emplacement d'arrivée (pour les entrées).
- **reason** : Raison du mouvement.
- **date** : Date du mouvement (par défaut la date actuelle).

**Cas d'utilisation :**  
- **Entrée** : Réception de produits dans l'entrepôt.
- **Sortie** : Expédition ou vente de produits.
- **Ajustement** : Correction d'inventaire (ajout ou retrait manuel).

---

### 3.5. Produit (stock.produits)
**Fichier : `models/produit.py`**

```python
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
                    self.env['stock.mouvement'].create({
                        'product_id': product.id,
                        'quantity': abs(difference),
                        'type': 'adjust',
                        'reason': 'Ajustement manuel (ajout)',
                        'emplacement_destination_id': product.emplacement_id.id,
                        'emplacement_source_id': False,
                    })
                else:
                    self.env['stock.mouvement'].create({
                        'product_id': product.id,
                        'quantity': abs(difference),
                        'type': 'adjust',
                        'reason': 'Ajustement manuel (retrait)',
                        'emplacement_source_id': product.emplacement_id.id,
                        'emplacement_destination_id': False,
                    })
```

**Documentation :**  
Ce modèle représente les produits en stock.
- **name** : Nom du produit.
- **reference** : Référence unique (générée automatiquement).
- **barcode** : Code-barres.
- **categorie_id** : Catégorie du produit.
- **emplacement_id** : Emplacement de stockage.
- **fournisseur_id** : Fournisseur associé.
- **mouvement_ids** : Historique des mouvements de stock.
- **quantity_ids** : Enregistrements de quantité pour ce produit.
- **quantity** : Quantité totale (calculée via le modèle StockQuantity).

**Cas d'utilisation :**  
- Création et modification d'un produit.
- Calcul automatique et ajustement manuel de la quantité en stock.

---

### 3.6. StockQuantity (stock.quantity)
**Fichier : `models/stock_quantity.py`**

```python
from odoo import models, fields, api

class StockQuantity(models.Model):
    _name = 'stock.quantity'
    _description = 'Quantité de stock par emplacement'

    product_id = fields.Many2one('stock.produits', string="Produit", required=True)
    emplacement_id = fields.Many2one('stock.emplacement', string="Emplacement", required=True)
    quantity = fields.Float(string="Quantité", default=0.0)

    _sql_constraints = [
        ('unique_product_location', 'UNIQUE(product_id, emplacement_id)',
         'Un produit ne peut avoir qu\'une seule quantité par emplacement.')
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

    def get_stock_quantity(self, product_id, emplacement_id):
        stock_quantity = self.search([
            ('product_id', '=', product_id),
            ('emplacement_id', '=', emplacement_id)
        ], limit=1)
        return stock_quantity.quantity if stock_quantity else 0.0
```

**Documentation :**  
Ce modèle gère la quantité de stock par emplacement.
- **product_id** : Produit concerné.
- **emplacement_id** : Emplacement de stockage.
- **quantity** : Quantité en stock.
- **update_stock** : Met à jour le stock lors d'un mouvement.
- **get_stock_quantity** : Récupère la quantité en stock pour un produit et un emplacement.

**Cas d'utilisation :**  
- Mise à jour automatique du stock lors des mouvements d'entrée, sortie ou ajustement.
- Consultation du stock actuel pour un produit dans un emplacement donné.

---

## 4. Vues

Les vues (formulaires, listes, recherches) permettent d'interagir avec les enregistrements de chaque modèle.

### Exemples :
- **Categorie** :  
  - *Form View* et *List View* pour créer et afficher les catégories (fichier `views/categorie_view.xml`).
- **Emplacement** :  
  - *Form View* et *List View* pour gérer les emplacements (fichier `views/emplacement_view.xml`).
- **Fournisseur** :  
  - *Form View* et *List View* pour gérer les fournisseurs (fichier `views/fournisseur_view.xml`).
- **Produit** :  
  - *Form View* détaillé et *List View* pour gérer les produits (fichier `views/produit_view.xml`).
- **StockMouvement** :  
  - *Form View* et *List View* pour les mouvements de stock (fichier `views/mouvement_view.xml`).
- **StockQuantity** :  
  - *Tree*, *Form* et *Search Views* pour consulter et modifier les quantités de stock (fichier `views/stock_quantity_views.xml`).

---

## 5. Rapports (Reports)

### Rapport Produit (PDF)
**Fichier : `reports/stock_report.xml`**

**Description :**  
Ce rapport génère un PDF affichant les informations d'un produit (Nom, Référence, Catégorie, Fournisseur, Emplacement, Quantité).  
- Lorsqu'un utilisateur clique sur le bouton **"Imprimer le Rapport"** dans la fiche produit, le rapport est généré via le moteur QWeb et wkhtmltopdf.

**Exemple de rapport :**
- **Nom** : Ordinateur Portable Dell  
- **Référence** : (générée automatiquement)  
- **Catégorie** : Materiel Informatique  
- **Fournisseur** : Fournisseur Informatique ENSAO  
- **Emplacement** : Salle Informatique  
- **Quantité** : Calculée automatiquement via StockQuantity

---

## 6. Menus

Les menus permettent d'accéder aux différentes fonctionnalités du module :

- **Menu Principal** : "Stock et Inventaire ERP"
- **Sous-menus** :
  - Produits
  - Catégories
  - Mouvements
  - Fournisseurs
  - Emplacements
  - Quantités

**Fichier :** `views/menus.xml`

---

## 7. Sécurité

Les règles d'accès sont définies dans le fichier `security/ir.model.access.csv` pour contrôler les droits (lecture, écriture, création, suppression) sur chaque modèle pour le groupe utilisateur de base (`base.group_user`).

---

## 8. Fichier Manifeste

**Fichier :** `__manifest__.py`

Ce fichier définit les métadonnées du module, ses dépendances et liste les fichiers à charger, tels que :
- `data/sequences.xml`
- `security/ir.model.access.csv`
- Vues (dans `views/*.xml`)
- Rapports (dans `reports/stock_report.xml`)
- Menus (dans `views/menus.xml`)

---

## 9. Cas d'Utilisation (Use Cases)

### 9.1. Gestion des Catégories
- **Exemple** :  
  - Ajouter une catégorie "Materiel Informatique" via le menu "Catégories".
- **Résultat attendu** :  
  - La catégorie est enregistrée et disponible pour l'association aux produits.

### 9.2. Gestion des Emplacements
- **Exemple** :  
  - Créer un emplacement "Magasin Central" avec une capacité de 1000 unités.
- **Résultat attendu** :  
  - L'emplacement est créé et la contrainte vérifie que la capacité est > 0.

### 9.3. Gestion des Fournisseurs
- **Exemple** :  
  - Ajouter un fournisseur "Fournisseur Informatique ENSAO" avec ses coordonnées.
- **Résultat attendu** :  
  - Le fournisseur est enregistré et peut être associé aux produits.

### 9.4. Gestion des Produits
- **Exemple** :  
  - Créer un produit "Ordinateur Portable Dell" en précisant la catégorie, l'emplacement et le fournisseur.
- **Résultat attendu** :  
  - Le produit est créé, la référence est générée automatiquement, et la quantité initiale est calculée via le modèle StockQuantity.

### 9.5. Mouvements de Stock

#### Types de Mouvement

**Entrée (Type: in)**
- **Description** :  
  - Enregistrement de l'ajout de produits dans le stock.
- **Cas d'utilisation** :  
  - Réception de produits d'un fournisseur.  
  - Retour de produits d'un client.  
  - Ajout manuel de produits dans le stock.
- **Exemple** :  
  - Produit : "Ordinateur Portable XYZ"  
  - Quantité : 10  
  - Emplacement de destination : "Entrepôt Principal"  
  - Raison : "Réception de la commande fournisseur #12345"

**Sortie (Type: out)**
- **Description** :  
  - Enregistrement de la sortie de produits du stock.
- **Cas d'utilisation** :  
  - Vente de produits à un client.  
  - Envoi de produits à un autre emplacement.  
  - Retrait manuel de produits du stock.
- **Exemple** :  
  - Produit : "Ordinateur Portable XYZ"  
  - Quantité : 5  
  - Emplacement source : "Entrepôt Principal"  
  - Raison : "Vente au client #67890"

**Ajustement (Type: adjust)**
- **Description** :  
  - Correction des quantités de stock en cas d'écart entre le stock théorique et le stock physique.
- **Cas d'utilisation** :  
  - Correction d'une erreur de saisie.  
  - Ajustement après un inventaire physique.  
  - Ajout ou retrait de produits pour des raisons techniques (exemple : produits endommagés).
- **Exemple** :  
  - Produit : "Ordinateur Portable XYZ"  
  - Quantité : 2  
  - Pour un ajustement positif (ajout) : Emplacement de destination "Entrepôt Principal".  
  - Pour un ajustement négatif (retrait) : Emplacement source "Entrepôt Principal".  
  - Raison : "Ajustement après inventaire physique : écart de 2 unités"

#### Comment Utiliser les Mouvements de Stock

1. **Créer un Mouvement :**
   - Aller dans le menu **Mouvements**.
   - Cliquer sur **Créer**.
   - Remplir les champs (Produit, Quantité, Type, Emplacement Source/Emplacement de Destination, Raison).
   - Cliquer sur **Enregistrer**.

2. **Vérification des Contraintes :**
   - Pour les sorties, le système vérifie que la quantité demandée est disponible dans l'emplacement source.
   - Pour les ajustements, le système met à jour le stock en fonction de la différence entre le stock théorique et le stock réel.

3. **Consultation :**
   - Les mouvements sont affichés dans la liste des mouvements.
   - Chaque mouvement est lié au produit concerné et à son emplacement.

**Exemples Concrets :**

- **Réception de Marchandise (Entrée) :**
  - Type : **in**
  - Produit : "Clavier USB"  
  - Quantité : 50  
  - Emplacement de destination : "Entrepôt Principal"  
  - Raison : "Réception de la commande fournisseur #98765"

- **Vente à un Client (Sortie) :**
  - Type : **out**
  - Produit : "Souris Sans Fil"  
  - Quantité : 10  
  - Emplacement source : "Entrepôt Principal"  
  - Raison : "Vente au client #54321"

- **Ajustement après Inventaire (Ajustement) :**
  - Type : **adjust**
  - Produit : "Ecran 24 Pouces"  
  - Quantité : 3  
  - Pour un retrait : Emplacement source "Entrepôt Principal"  
  - Raison : "Ajustement après inventaire physique : écart de 3 unités"

---

## 10. Rapport PDF

Le rapport PDF permet d'imprimer les informations d'un produit.  
- **Action** : Dans la fiche produit, cliquez sur **"Imprimer le Rapport"**.
- **Rapport** : Le rapport PDF est généré via le moteur QWeb (fichier `reports/stock_report.xml`) et inclut les informations suivantes :
  - Nom
  - Référence
  - Catégorie
  - Fournisseur
  - Emplacement
  - Quantité

---

## 11. Menus

Le module intègre plusieurs menus pour faciliter la navigation :
- **Stock et Inventaire ERP** (Menu Principal)
- **Sous-menus** :
  - Produits
  - Catégories
  - Mouvements
  - Fournisseurs
  - Emplacements
  - Quantités

Ces menus sont définis dans le fichier `views/menus.xml`.

---

## 12. Sécurité

Les règles d'accès sont configurées via le fichier `security/ir.model.access.csv`.  
Chaque modèle dispose d'un accès (lecture, écriture, création, suppression) pour le groupe d'utilisateurs de base (`base.group_user`).

---

## 13. Installation et Déploiement

### Installation
1. **Pré-requis :**
   - PostgreSQL, Python, Odoo 19
2. **Dépendances :**
   - Le module dépend de `base` et `web`.
3. **Procédure :**
   - Copier le module dans le répertoire `addons` d'Odoo.
   - Mettre à jour la liste des modules via l'interface d'administration ou en ligne de commande.
   - Installer le module "Gestion de Stock et Inventaire".

### Déploiement
- **Mise à jour :**
  - Pour modifier les vues ou les données, effectuez une mise à jour du module (ex. `odoo-bin -u stock_inventory_project -d votre_base`).
- **Tests :**
  - Vérifiez la création et la modification des enregistrements pour chaque modèle.
  - Testez le calcul des quantités et l'impression des rapports PDF.

---

## 14. Contribution

Les contributions sont les bienvenues !  
- Pour proposer des améliorations ou corriger des erreurs, créez une pull request ou soumettez une issue sur GitHub.

