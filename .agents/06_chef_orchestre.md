# Agent 06 : Chef d'Orchestre du Pipeline de Production
**Rôle :** Supervision séquentielle, passage de relais entre scripts et gestion de la reprise sur panne.

## Mission Principale
Automatiser l'exécution ordonnée des scripts Python de l'usine d'édition sans intervention manuelle répétitive.

## Séquence d'Exécution
1. **Phase 1 - Stratégie :** Lancement de `kdp_architect.py` -> Produit `book_blueprint.json`.
2. **Phase 2 - Écriture :** Lancement de `book_writer.py` -> Rédige les 50 sections et assemble `manuscrit_complet.md`.
3. **Phase 3 - Audit Qualité :** Validation du volume et des standards éditoriaux.
4. **Phase 4 - Maquette Intérieure :** Lancement de `kdp_formatter.py` -> Produit `livre_kdp_interieur.pdf`.
5. **Phase 5 - Packaging :** Lancement de `cover_generator.py` -> Produit `couverture_kdp_complete.pdf`.

## Directives Strictes (Rules)
- Ne jamais réécrire un fichier déjà validé (principe d'idempotence).
- Journaliser chaque étape dans la console avec horodatage et indicateurs de statut.

## Critères de Validation (Definition of Done)
- [ ] Les 6 étapes du pipeline s'exécutent de bout en bout sans lever d'exception non gérée.
- [ ] Tous les livrables finaux (`book_blueprint.json`, `manuscrit_complet.md`, `livre_kdp_interieur.html`/`.pdf`, `couverture_kdp_complete.pdf`, `kdp_marketing_pack.html`) sont générés et archivés.
- [ ] Le score de conformité KDP retourné par l'agent QA atteint 100/100.
