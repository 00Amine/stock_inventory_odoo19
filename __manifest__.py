

{
    'name': 'Gestion de Stock et Inventaire',
    'author': 'Mohamed Amine Nourdine',
    'version': '19.0.1.0',
    'category': 'Inventory',
    'summary': 'Gestion des stocks et inventaire',
    'description': 'Module pour gérer les stocks et les inventaires.',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'report/produit_report.xml',
        'views/categorie_view.xml',
        'views/fournisseur_view.xml',
        'views/emplacement_view.xml',
        'views/produit_view.xml',
        'views/mouvement_view.xml',
        'views/quantity_view.xml',
        'views/menus.xml',

    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'sequence':-1,
    'auto-update': True,

}