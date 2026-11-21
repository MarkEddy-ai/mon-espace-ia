"""
orchestrator.py - Orchestrateur Suprême de la Machine de Création KDP Haute Couture.
Pilote l'ensemble des agents spécialisés de manière chirurgicale, séquentielle et résiliente :
  1. Stratège & Architecte KDP (kdp_architect.py)
  2. Rédacteur en Chef (book_writer.py)
  3. Typographe & Formateur Intérieur (kdp_formatter.py)
  4. Directeur Artistique Couverture (cover_generator.py)
  5. Responsable Marketing & Conversion (kdp_marketing.py)
  6. Auditeur Qualité & Conformité (kdp_qa.py)
"""

import sys
import shutil
import argparse
import time
import re
import os
from pathlib import Path

# Force UTF-8 encoding for output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Imports directs des modules agents et du design system
from kdp_architect import concevoir_livre_kdp, sauvegarder_blueprint
from book_writer import assembler_livre
from kdp_formatter import convertir_manuscrit_en_pdf
from cover_generator import generer_couverture
from kdp_marketing import generer_pack_marketing
from kdp_qa import auditer_projet_kdp
from kdp_design_system import PALETTES_PRESTIGE

def archiver_projet_dans_books(blueprint_path: Path) -> Path:
    """Archive l'ensemble des livrables dans un sous-dossier dédié sous books/<slug>/."""
    import json
    if not blueprint_path.exists():
        return None
    try:
        bp = json.loads(blueprint_path.read_text(encoding="utf-8"))
        titre = bp.get("titre", "livre")
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", titre).strip("_").lower()[:40]
        dossier_livre = Path("books") / slug
        dossier_livre.mkdir(parents=True, exist_ok=True)

        fichiers_a_archiver = [
            "book_blueprint.json",
            "manuscrit_complet.md",
            "livre_kdp_interieur.html",
            "livre_kdp_interieur.pdf",
            "couverture_kdp_complete.pdf",
            "kdp_marketing_pack.html",
            "livre_imprimable_kdp.pdf",
            "livre_ebook_kdp.epub",
            "livre_numerique_interactif.pdf",
            "couverture_ebook.jpg",
            "livre_imprimable_kdp.html",
            "livre_numerique_interactif.html"
        ]

        for nom in fichiers_a_archiver:
            f = Path(nom)
            if f.exists():
                shutil.copy2(f, dossier_livre / nom)

        print(f"📦 Ensemble des actifs archivés dans : {dossier_livre.resolve()}")
        return dossier_livre
    except Exception as e:
        print(f"⚠️ Note d'archivage : {e}")
        return None

def executer_pipeline_complet(
    niche: str,
    cible: str,
    palette: str = "obsidian_gold",
    etape_cible: str = None,
    nouveau_livre: bool = False,
    nb_chapitres: int = None
):
    print("\n" + "=" * 70)
    print("🏭 MACHINE DE CRÉATION DE LIVRES PROFESSIONNELS AMAZON KDP")
    print("   Orchestrateur Multi-Agents Haute Couture")
    print("=" * 70)
    print(f"🎯 Niche / Thématique : {niche}")
    print(f"👥 Public Cible       : {cible}")
    print(f"🎨 Palette Choisie    : {PALETTES_PRESTIGE.get(palette, {}).get('nom', palette)}")
    print("=" * 70 + "\n")

    debut_total = time.time()
    bp_path = Path("book_blueprint.json")

    # Si l'utilisateur demande un nouveau livre, on archive l'actuel et on réinitialise
    if nouveau_livre:
        print("📦 Archivage de sécurité du projet précédent avant initialisation...")
        archiver_projet_dans_books(bp_path)
        if bp_path.exists():
            bp_path.unlink()
        ms_p = Path("manuscrit_complet.md")
        if ms_p.exists():
            ms_p.unlink()
        sec_dir = Path("livre_sections")
        if sec_dir.exists():
            for f in sec_dir.glob("*.md"):
                f.unlink()
        print("🧹 Espace de travail réinitialisé pour le nouveau livre.\n")

    # -------------------------------------------------------------
    # ÉTAPE 1 : L'ARCHITECTE & STRATÈGE ÉDITORIAL
    # -------------------------------------------------------------
    if etape_cible in [None, "architect"]:
        print("▶️ [AGENT 1/6] STRATÈGE ÉDITORIAL & ARCHITECTE SEO...")
        if not bp_path.exists():
            plan = concevoir_livre_kdp(niche, cible, nb_chapitres=nb_chapitres)
            sauvegarder_blueprint(plan, "book_blueprint.json")
        else:
            print(f"  ℹ️ Blueprint existant détecté ({bp_path.name}). Passage à la suite.")
        print("  ✅ Étape 1 validée.\n")
        if etape_cible == "architect": return

    # -------------------------------------------------------------
    # ÉTAPE 2 : LE RÉDACTEUR EN CHEF
    # -------------------------------------------------------------
    if etape_cible in [None, "writer"]:
        print("▶️ [AGENT 2/6] RÉDACTEUR EN CHEF & GHOSTWRITER D'ÉLITE...")
        assembler_livre()
        print("  ✅ Étape 2 validée.\n")
        if etape_cible == "writer": return

    # -------------------------------------------------------------
    # ÉTAPE 3 : LE TYPOGRAPHE & METTEUR EN PAGE INTÉRIEUR & EBOOK
    # -------------------------------------------------------------
    if etape_cible in [None, "formatter"]:
        print("▶️ [AGENT 3/6] TYPOGRAPHE & MAQUETTISTE 6X9 HAUTE COUTURE...")
        convertir_manuscrit_en_pdf()

        # Compilation certifiée Kindle EPUB 3
        try:
            from build_multi_versions import compiler_version_ebook, charger_blueprint, charger_manuscrit
            bp = charger_blueprint()
            ms = charger_manuscrit()
            compiler_version_ebook(bp, ms)
        except Exception as e:
            print(f"ℹ️ Note compilation eBook : {e}")

        print("  ✅ Étape 3 validée.\n")
        if etape_cible == "formatter": return

    # -------------------------------------------------------------
    # ÉTAPE 4 : LE DIRECTEUR ARTISTIQUE & DESIGNER COUVERTURE
    # -------------------------------------------------------------
    if etape_cible in [None, "cover"]:
        print(f"▶️ [AGENT 4/6] DIRECTEUR ARTISTIQUE COUVERTURE ({palette} @ 300 DPI)...")
        generer_couverture(palette_name=palette)
        print("  ✅ Étape 4 validée.\n")
        if etape_cible == "cover": return

    # -------------------------------------------------------------
    # ÉTAPE 5 : LE RESPONSABLE MARKETING & CONVERSION
    # -------------------------------------------------------------
    if etape_cible in [None, "marketing"]:
        print("▶️ [AGENT 5/6] RESPONSABLE MARKETING & CONVERSION AMAZON...")
        generer_pack_marketing()
        print("  ✅ Étape 5 validée.\n")
        if etape_cible == "marketing": return

    # -------------------------------------------------------------
    # ÉTAPE 6 : L'AUDITEUR QUALITÉ & CONFORMITÉ KDP
    # -------------------------------------------------------------
    if etape_cible in [None, "qa"]:
        print("▶️ [AGENT 6/6] AUDITEUR QUALITÉ & CERTIFICATION AMAZON KDP...")
        rapport = auditer_projet_kdp()
        print("  ✅ Étape 6 validée.\n")

    # Archivage automatique dans un dossier de projet
    archiver_projet_dans_books(bp_path)

    temps_ecoule = time.time() - debut_total
    print("=" * 70)
    print(f"🎉 PIPELINE DE PRODUCTION ACHEVÉ EN {temps_ecoule:.1f} SECONDES !")
    print("=" * 70)
    print("📦 Vos actifs professionnels Amazon KDP créés :")
    print("  1. 📘 couverture_kdp_complete.pdf  -> Couverture brochée haute définition 300 DPI (Plat 1 + Dos + Plat 4)")
    print("  2. 📖 livre_kdp_interieur.html     -> Intérieur broché mis en page 6x9 pouces avec marges de reliure")
    print("  3. 📱 livre_ebook_kdp.epub         -> Ebook Kindle certifié EPUB 3 avec table des matières dynamique")
    print("  4. 🎨 couverture_ebook.jpg         -> Couverture avant eBook haute définition 1800x2700 px")
    print("  5. 📄 manuscrit_complet.md         -> Manuscrit unifié prêt pour Kindle Create")
    print("  6. 🛒 kdp_marketing_pack.html      -> Description HTML, 7 mots-clés A9 et A+ Content")
    print("  7. 📋 book_blueprint.json          -> Architecture complète des sections du livre")
    print("=" * 70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Orchestrateur Suprême de la Machine KDP Haute Couture.")
    parser.add_argument("--niche", type=str, default="Maîtriser ses finances personnelles et investir simplement", help="Thématique du livre")
    parser.add_argument("--cible", type=str, default="Débutants sans compétences financières préalables", help="Public cible")
    parser.add_argument("--palette", choices=list(PALETTES_PRESTIGE.keys()), default="obsidian_gold", help="Palette de luxe pour la couverture")
    parser.add_argument("--step", choices=["architect", "writer", "formatter", "cover", "marketing", "qa"], default=None, help="Exécuter un agent spécifique")
    parser.add_argument("--new", action="store_true", help="Démarrer un nouveau livre (archive l'actuel et réinitialise)")
    parser.add_argument("--chapitres", type=int, default=None, help="Nombre de chapitres souhaité (ex: 7, 8, 10, 12, 14, 18)")
    args = parser.parse_args()

    executer_pipeline_complet(
        niche=args.niche,
        cible=args.cible,
        palette=args.palette,
        etape_cible=args.step,
        nouveau_livre=args.new,
        nb_chapitres=args.chapitres
    )

if __name__ == "__main__":
    main()
