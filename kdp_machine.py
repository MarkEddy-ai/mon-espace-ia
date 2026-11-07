"""
kdp_machine.py - Moteur autonome de création de livres professionnels Amazon KDP.
Pilote l'ensemble de la chaîne de production :
1. Architecture & Stratégie SEO (kdp_architect.py)
2. Rédaction approfondie section par section (kdp_writer.py)
3. Mise en page conforme Amazon KDP 6x9 po (kdp_formatter.py)
"""

import sys
import argparse
from pathlib import Path

from kdp_architect import concevoir_livre_kdp, sauvegarder_blueprint
from kdp_writer import orchestrer_redaction_livre
from kdp_formatter import formater_projet_complet

def executer_machine_kdp(
    niche: str,
    cible: str,
    max_chapitres: int = None,
    blueprint_path: str = "book_blueprint.json",
    draft_path: str = "book_draft.json",
    sauter_architecture: bool = False
):
    print("\n" + "=" * 65)
    print("🏭 MACHINE DE CRÉATION DE LIVRES AMAZON KDP PROFESSIONNEL")
    print("=" * 65)
    print(f"🎯 Thématique : {niche}")
    print(f"👥 Cible      : {cible}")
    if max_chapitres:
        print(f"⚡ Mode test  : Limité à {max_chapitres} chapitre(s) pour validation rapide")
    print("=" * 65 + "\n")

    # ÉTAPE 1 : ARCHITECTURE DU LIVRE
    if not sauter_architecture and not Path(blueprint_path).exists():
        print("📌 ÉTAPE 1/3 : Conception de l'architecture éditoriale et SEO...")
        blueprint = concevoir_livre_kdp(niche, cible)
        sauvegarder_blueprint(blueprint, blueprint_path)
    else:
        print(f"📌 ÉTAPE 1/3 : Utilisation du schéma existant ({blueprint_path})")

    # ÉTAPE 2 : RÉDACTION PROFONDE DU CONTENU
    print("\n📌 ÉTAPE 2/3 : Rédaction approfondie des chapitres et sections...")
    draft = orchestrer_redaction_livre(
        blueprint_path=blueprint_path,
        draft_output_path=draft_path,
        limite_chapitres=max_chapitres
    )

    # ÉTAPE 3 : FORMATAGE ET EXPORT KDP 6X9
    print("\n📌 ÉTAPE 3/3 : Formatage éditorial KDP 6x9 et génération des livrables...")
    formater_projet_complet(draft_file=draft_path, blueprint_file=blueprint_path)

    print("\n" + "=" * 65)
    print("🚀 VOTRE LIVRE EST PRÊT POUR PUBLICATION SUR AMAZON KDP !")
    print("=" * 65)
    print("Fichiers créés dans votre dossier :")
    print("  1. 📖 livre_kdp_6x9.html       -> Livre imprimable (Fichier > Imprimer > Enregistrer en PDF)")
    print("  2. 📄 manuscrit_complet.md     -> Manuscrit pour liseuses / Kindle Create")
    print("  3. 🛒 amazon_description.html  -> Description produit optimisée pour votre page Amazon")
    print("  4. 📋 book_blueprint.json      -> Stratégie éditoriale, catégories et 7 mots-clés KDP")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Machine de création de livres Amazon KDP professionnel.")
    parser.add_argument("--niche", type=str, default="Maîtriser ses finances personnelles et investir simplement", help="Thématique / niche du livre")
    parser.add_argument("--cible", type=str, default="Jeunes actifs et débutants sans compétences financières préalables", help="Public cible")
    parser.add_argument("--demo", action="store_true", help="Mode démo rapide : rédige les 2 premiers chapitres pour tester la chaîne")
    parser.add_argument("--max-chapitres", type=int, default=None, help="Nombre maximal de chapitres à rédiger")
    parser.add_argument("--format-only", action="store_true", help="Formater uniquement à partir d'un brouillon existant")
    args = parser.parse_args()

    if args.format_only:
        formater_projet_complet()
        return

    max_ch = 2 if args.demo else args.max_chapitres

    executer_machine_kdp(
        niche=args.niche,
        cible=args.cible,
        max_chapitres=max_ch
    )

if __name__ == "__main__":
    main()
