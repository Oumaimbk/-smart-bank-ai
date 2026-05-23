Dataset synthétique conçu pour un projet d'analyse bancaire.

1) transactions_bancaires_synthetiques_brutes.csv = dataset principal à utiliser.
   - Il ne contient PAS de catégorie métier, pour permettre une segmentation from scratch.
   - Il contient des transactions de débit et de crédit, avec libellés clairs.

2) transactions_bancaires_verite_terrain.csv = fichier de validation.
   - À garder de côté au départ.
   - Il contient la catégorie réelle, les labels d'anomalie et de fraude.
   - Il sert uniquement à évaluer votre segmentation ou votre détection.

Contexte:
- Pays: Maroc (synthétique)
- 75 clients
- période: 2024-01-01 à 2024-12-31
- transactions avec narrations réalistes et claires
- quelques cas anormaux et frauduleux injectés volontairement
