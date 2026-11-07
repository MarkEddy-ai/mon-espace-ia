"""
Injecteur d'outils visuels et de fiches de synthèse de fin de chapitre.
Ajoute des matrices de bord et des fiches d'action pour augmenter la valeur perçue du livre.
"""

import re
from pathlib import Path

FICHIER_CIBLE = Path("manuscrit_avec_preface.md") if Path("manuscrit_avec_preface.md").exists() else Path("manuscrit_complet.md")
FICHIER_SORTIE = Path("manuscrit_enrichi.md")


def creer_matrice_fin_chapitre(numero_chapitre: int) -> str:
    """Génère un tableau Markdown élégant et une checklist d'action pour le chapitre."""
    return f"""

> ### 📋 FICHE MÉTHODE : VALIDATION DU CHAPITRE {numero_chapitre}
> 
> | Étape | Action Clé | Livrable Concret | Statut |
> | :--- | :--- | :--- | :---: |
> | **01** | Audit de la situation actuelle | Feuille de calcul remplie | [ ] |
> | **02** | Élimination des points de friction | Arbitrage budgétaire validé | [ ] |
> | **03** | Automatisation des versements | Ordre bancaire programmé | [ ] |
> | **04** | Vérification à 30 jours | Indicateur de progression noté | [ ] |
>
> **Règle d'or :** *Ne passez pas au chapitre suivant tant que les 4 cases ci-dessus ne sont pas cochées.*

---
"""


def enrichir_manuscrit():
    if not FICHIER_CIBLE.exists():
        print(f"❌ {FICHIER_CIBLE} introuvable.")
        return

    contenu = FICHIER_CIBLE.read_text(encoding="utf-8")

    # Découpage par grand chapitre
    pattern_chapitre = r"(# Chapitre (\d+) : .*)"
    
    morceaux = re.split(pattern_chapitre, contenu)
    
    # Reconstruction avec injection de la fiche méthode avant chaque nouveau chapitre (sauf le premier)
    texte_reconstruit = [morceaux[0]]
    
    i = 1
    while i < len(morceaux):
        en_tete_chapitre = morceaux[i]
        num_chap = int(morceaux[i+1])
        corps_chapitre = morceaux[i+2]
        
        # Ajout du chapitre courant
        texte_reconstruit.append(en_tete_chapitre)
        texte_reconstruit.append(corps_chapitre)
        
        # Injection du tableau de synthèse à la fin de chaque chapitre
        texte_reconstruit.append(creer_matrice_fin_chapitre(num_chap))
        
        i += 3

    FICHIER_SORTIE.write_text("".join(texte_reconstruit), encoding="utf-8")
    print(f"✅ Manuscrit enrichi de matrices et checklists : {FICHIER_SORTIE.resolve()}")


if __name__ == "__main__":
    enrichir_manuscrit()