# Each tuple: (category_name, [keywords to match against narration + merchant])
# Keywords are matched case-insensitively against the concatenated text.
# ORDER MATTERS — first matching rule wins. Put more specific rules first.
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ('Revenu', [
        'salaire', 'virement employeur', 'salary', 'paie', 'traitement',
    ]),
    ('E-commerce', [
        'amazon', 'aliexpress', 'ali express', 'ebay',
        'jumia', 'noon', 'shein', 'wish', 'etsy',
    ]),
    ('Shopping', [
        # International fashion
        'nike', 'adidas', 'puma', 'reebok', 'new balance',
        'zara', 'h&m', 'hm', 'h and m', 'mango', 'bershka',
        'pull&bear', 'stradivarius', 'massimo dutti',
        'sephora', 'gucci', 'louis vuitton', 'dior', 'chanel',
        'fnac', 'virgin megastore',
        # Tech
        'apple store', 'apple', 'samsung', 'iphone', 'huawei',
        # Generic
        'vetements', 'vêtements', 'chaussures', 'accessoires',
        'bijouterie', 'maroquinerie', 'lingerie',
    ]),
    ('Transport', [
        'transport', 'careem', 'taxi', 'carburant', 'shell', 'total energies',
        'afriquia', 'ziz', 'ctm', 'oncf', 'autoroute', 'parking', 'vignette',
    ]),
    ('Alimentation', [
        'supermarche', 'supermarché', 'carrefour', 'marjane', 'acima', 'aswak',
        'bim', 'epicerie', 'épicerie', 'boulangerie',
        'restaurant', 'cafe', 'café', 'mcdo', 'mcdonald', 'kfc',
        'pizza', 'livreur', 'glovo', 'traiteur',
    ]),
    ('Logement', [
        'loyer', 'radeema', 'redal', 'onee', 'eau', 'electricite', 'électricité',
        'syndic', 'amenagement', 'location',
    ]),
    ('Santé', [
        'pharmacie', 'clinique', 'medecin', 'médecin', 'hopital', 'hôpital',
        'labo', 'laboratoire', 'optique', 'dentiste',
    ]),
    ('Éducation', [
        'ecole', 'école', 'universite', 'université', 'frais scolaires',
        'cours', 'formation', 'inscription',
    ]),
    ('Loisirs', [
        'cinema', 'netflix', 'spotify', 'youtube', 'jeux', 'sport',
        'hammam', 'hotel', 'hôtel', 'voyage', 'tourisme',
    ]),
    ('Télécommunications', [
        'maroc telecom', 'orange', 'inwi', 'internet', 'telephone', 'mobile',
        'recharge', 'forfait',
    ]),
    ('Banque & Finance', [
        'virement employeur',   # already caught above, kept for safety
        'retrait', 'depot', 'dépôt', 'commission', 'frais bancaires',
        'remboursement', 'atm', 'prelevement',
    ]),
    ('Épargne & Placement', [
        'epargne', 'épargne', 'placement', 'assurance', 'cnss', 'retraite',
    ]),
]

OTHER_CATEGORY = 'Autre'
