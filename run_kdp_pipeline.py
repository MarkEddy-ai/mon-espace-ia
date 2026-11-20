"""
PIPELINE MAÎTRE AMAZON KDP (UN SEUL CLIC) - MarkEddy
=====================================================
Ce script unifie et orchestre la production complète du livre KDP :
 1. Lit les chapitres générés dans 'book_state.json' (ou un fichier Markdown source).
 2. Appelle 'interior_artisan_agent.py' pour compiler 'interieurs_finaux/Interieur_6.0x9.0.pdf'.
 3. Appelle automatiquement 'cover_artisan_agent.py' en lui passant ce PDF intérieur
    pour calculer l'épaisseur exacte de la tranche et générer
    'couvertures_finales/Couverture_OFFICIELLE_KDP.pdf'.
"""

import sys
import json
import re
import argparse
from pathlib import Path
from pypdf import PdfReader

# Import des deux moteurs de production
from interior_artisan_agent import fabriquer_interieur
from cover_artisan_agent import fabriquer as fabriquer_couverture


def convertir_markdown_en_html(md_texte: str) -> str:
    """
    Convertisseur Markdown vers HTML autonome en pur Python (zéro dépendance externe).
    Prend en charge titres, gras, italique, listes, tableaux, citations et lettrines.
    """
    lignes = md_texte.splitlines()
    html_blocs = []
    en_liste = False
    en_tableau = False
    lignes_tableau = []
    en_citation = False
    lignes_citation = []
    premier_p_apres_h1 = False

    def vider_liste():
        nonlocal en_liste
        if en_liste:
            html_blocs.append("</ul>")
            en_liste = False

    def vider_citation():
        nonlocal en_citation, lignes_citation
        if en_citation:
            texte_brut = "<br>".join(lignes_citation)
            if "action immédiate" in texte_brut.lower() or "⚡" in texte_brut:
                html_blocs.append(f'<div class="action-box">{texte_brut}</div>')
            else:
                html_blocs.append(f'<blockquote class="callout-box"><p>{texte_brut}</p></blockquote>')
            lignes_citation = []
            en_citation = False

    def vider_tableau():
        nonlocal en_tableau, lignes_tableau
        if en_tableau and lignes_tableau:
            html_blocs.append('<table class="kdp-table">')
            for idx, r in enumerate(lignes_tableau):
                if idx == 0:
                    entetes = "".join(f"<th>{c}</th>" for c in r)
                    html_blocs.append(f"<thead><tr>{entetes}</tr></thead><tbody>")
                else:
                    cellules = "".join(f"<td>{c}</td>" for c in r)
                    html_blocs.append(f"<tr>{cellules}</tr>")
            html_blocs.append("</tbody></table>")
            lignes_tableau = []
            en_tableau = False

    def formater_en_ligne(txt: str) -> str:
        # Gras et italique combinés
        txt = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", txt)
        # Gras
        txt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", txt)
        # Italique
        txt = re.sub(r"\*(.*?)\*", r"<em>\1</em>", txt)
        # Code en ligne
        txt = re.sub(r"`(.*?)`", r"<code>\1</code>", txt)
        return txt

    for ligne in lignes:
        brute = ligne.rstrip()
        nettoyee = brute.strip()

        # Ligne de tableau (| col 1 | col 2 |)
        if nettoyee.startswith("|") and nettoyee.endswith("|"):
            vider_liste()
            vider_citation()
            cellules = [formater_en_ligne(c.strip()) for c in nettoyee[1:-1].split("|")]
            # Détecter ligne de séparation (ex: :--- | :---)
            if all(re.match(r"^:?-+:?$", c) for c in cellules):
                continue
            en_tableau = True
            lignes_tableau.append(cellules)
            continue
        else:
            vider_tableau()

        # Citation / Callout (> citation)
        if nettoyee.startswith(">"):
            vider_liste()
            en_citation = True
            lignes_citation.append(formater_en_ligne(nettoyee.lstrip("> ").strip()))
            continue
        else:
            vider_citation()

        # Ligne vide
        if not nettoyee:
            vider_liste()
            continue

        # Séparateur horizontal (--- ou ***)
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", nettoyee):
            vider_liste()
            html_blocs.append("<hr />")
            continue

        # Titres H1 à H4
        if nettoyee.startswith("# "):
            vider_liste()
            html_blocs.append(f"<h1>{formater_en_ligne(nettoyee[2:].strip())}</h1>")
            premier_p_apres_h1 = True
            continue
        if nettoyee.startswith("## "):
            vider_liste()
            html_blocs.append(f"<h2>{formater_en_ligne(nettoyee[3:].strip())}</h2>")
            continue
        if nettoyee.startswith("### "):
            vider_liste()
            html_blocs.append(f"<h3>{formater_en_ligne(nettoyee[4:].strip())}</h3>")
            continue
        if nettoyee.startswith("#### "):
            vider_liste()
            html_blocs.append(f"<h4>{formater_en_ligne(nettoyee[5:].strip())}</h4>")
            continue

        # Liste à puces (- ou *)
        if nettoyee.startswith("- ") or nettoyee.startswith("* "):
            if not en_liste:
                html_blocs.append("<ul>")
                en_liste = True
            html_blocs.append(f"<li>{formater_en_ligne(nettoyee[2:].strip())}</li>")
            continue
        else:
            vider_liste()

        # Paragraphe standard (avec lettrine sur le premier paragraphe après H1)
        contenu_p = formater_en_ligne(nettoyee)
        if premier_p_apres_h1 and not contenu_p.startswith("<"):
            html_blocs.append(f'<p class="lettrine">{contenu_p}</p>')
            premier_p_apres_h1 = False
        else:
            html_blocs.append(f"<p>{contenu_p}</p>")

    vider_liste()
    vider_citation()
    vider_tableau()

    return "\n".join(html_blocs)


def charger_donnees_livre(fichier_state: str = "book_state.json", fichier_md_secours: str = "manuscrit_complet.md") -> dict:
    """
    Charge les données du livre :
    1. Depuis 'book_state.json' si disponible.
    2. Sinon depuis le fichier Markdown source ('manuscrit_complet.md' ou 'manuscrit_ameliore.md').
    """
    state_path = Path(fichier_state)
    bp_path = Path("book_blueprint.json")

    # Métadonnées de repli depuis le blueprint si existant
    blueprint = {}
    if bp_path.exists():
        try:
            with open(bp_path, "r", encoding="utf-8") as f:
                blueprint = json.load(f)
        except Exception:
            blueprint = {}

    titre_defaut = blueprint.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    sous_titre_defaut = blueprint.get(
        "sous_titre",
        "Reprogrammer son cerveau en 66 jours : la méthode pas-à-pas pour éliminer la procrastination et libérer 3 heures par jour"
    )
    auteur_defaut = blueprint.get("auteur_suggere", "MarkEddy")
    thematique_defaut = "MINDSET"

    # 1. Tentative depuis book_state.json
    if state_path.exists():
        print(f"📖 Chargement de l'état du livre depuis '{state_path.name}'...")
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            return {
                "titre": state.get("titre", titre_defaut),
                "sous_titre": state.get("sous_titre", sous_titre_defaut),
                "auteur": state.get("auteur", auteur_defaut),
                "thematique": state.get("thematique", thematique_defaut),
                "chapitres": state.get("chapitres", []),
                "source": state_path.name
            }
        except Exception as e:
            print(f"⚠️ Erreur de lecture de '{state_path.name}': {e}. Bascule sur le Markdown source.")

    # 2. Secours depuis le fichier Markdown
    md_candidates = [Path(fichier_md_secours), Path("manuscrit_complet.md"), Path("manuscrit_ameliore.md")]
    md_trouve = None
    for cand in md_candidates:
        if cand.exists():
            md_trouve = cand
            break

    if not md_trouve:
        raise FileNotFoundError(
            "❌ Impossible de trouver ni 'book_state.json' ni un manuscrit Markdown ('manuscrit_complet.md')."
        )

    print(f"📄 Extraction des chapitres depuis '{md_trouve.name}'...")
    texte_md = md_trouve.read_text(encoding="utf-8")

    # Découpage par H1 (# Chapitre ou # Section)
    sections_brutes = re.split(r"\n(?=# )", texte_md)
    chapitres = []
    for s in sections_brutes:
        s_clean = s.strip()
        if not s_clean:
            continue
        premiere_ligne = s_clean.splitlines()[0].lstrip("# ").strip()
        chapitres.append({
            "titre": premiere_ligne,
            "contenu_markdown": s_clean
        })

    # Enregistrement synchronisé de book_state.json
    donnees = {
        "titre": titre_defaut,
        "sous_titre": sous_titre_defaut,
        "auteur": auteur_defaut,
        "thematique": thematique_defaut,
        "total_chapitres": len(chapitres),
        "chapitres": chapitres,
        "source": md_trouve.name
    }
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
    print(f"✅ 'book_state.json' synchronisé avec succès ({len(chapitres)} chapitres).")

    return donnees


def assembler_html_livre(donnees_livre: dict) -> str:
    """
    Assemble le corps HTML de l'ensemble des chapitres.
    """
    # Si le livre contient une suite de chapitres
    blocs_html = []
    for chap in donnees_livre.get("chapitres", []):
        md = chap.get("contenu_markdown", "")
        if md:
            blocs_html.append(convertir_markdown_en_html(md))
        elif chap.get("contenu_html"):
            blocs_html.append(chap.get("contenu_html"))
        elif chap.get("titre"):
            blocs_html.append(f"<h1>{chap.get('titre')}</h1>")

    return "\n\n".join(blocs_html)


def executer_pipeline(
    fichier_state: str = "book_state.json",
    fichier_md: str = "manuscrit_complet.md",
    thematique_forcee: str = None
) -> dict:
    """
    Exécute le pipeline complet KDP en un seul clic.
    """
    print("\n" + "=" * 76)
    print("🚀 DÉMARRAGE DU PIPELINE UNIFIÉ AMAZON KDP (UN SEUL CLIC)")
    print("=" * 76)

    # --------------------------------------------------------------------------
    # ÉTAPE A : Lecture des chapitres
    # --------------------------------------------------------------------------
    print("\n[1/3] 📚 ÉTAPE A : LECTURE DE L'ÉTAT DU LIVRE ET DES CHAPITRES")
    donnees = charger_donnees_livre(fichier_state=fichier_state, fichier_md_secours=fichier_md)
    titre = donnees.get("titre", "NEURO-FOCUS : LE POUVOIR DES MICRO-HABITUDES")
    sous_titre = donnees.get("sous_titre", "")
    auteur = donnees.get("auteur", "MarkEddy")
    thematique = thematique_forcee or donnees.get("thematique", "MINDSET")

    print(f"  • Titre de l'ouvrage : {titre}")
    print(f"  • Sous-titre         : {sous_titre}")
    print(f"  • Auteur             : {auteur}")
    print(f"  • Thématique         : {thematique}")
    print(f"  • Nombre de sections : {len(donnees.get('chapitres', []))}")

    # Assemblage du contenu HTML
    contenu_html = assembler_html_livre(donnees)

    # --------------------------------------------------------------------------
    # ÉTAPE B : Compilation de l'intérieur PDF via interior_artisan_agent.py
    # --------------------------------------------------------------------------
    print("\n[2/3] 📐 ÉTAPE B : COMPILATION DE L'INTÉRIEUR (interior_artisan_agent)")
    chemin_interieur_pdf = Path("interieurs_finaux/Interieur_6.0x9.0.pdf")

    pdf_interieur = fabriquer_interieur(
        fichier_html="template_interior.html",
        titre_livre=titre,
        sous_titre=sous_titre,
        auteur=auteur,
        contenu_html=contenu_html,
        largeur_po=6.0,
        hauteur_po=9.0,
        fichier_sortie=chemin_interieur_pdf
    )

    if not pdf_interieur or not Path(pdf_interieur).exists():
        raise RuntimeError(f"❌ Échec de compilation de l'intérieur : {chemin_interieur_pdf}")

    # Contrôle de la pagination
    reader = PdfReader(str(pdf_interieur))
    nb_pages = len(reader.pages)
    print(f"  • Intérieur validé : {pdf_interieur}")
    print(f"  • Pagination exacte : {nb_pages} pages")

    # --------------------------------------------------------------------------
    # ÉTAPE C : Génération de la couverture complète via cover_artisan_agent.py
    # --------------------------------------------------------------------------
    print("\n[3/3] 🎨 ÉTAPE C : GÉNÉRATION COUVERTURE COMPLÈTE (cover_artisan_agent)")
    chemin_couverture_pdf = Path("couvertures_finales/Couverture_OFFICIELLE_KDP.pdf")

    pdf_couverture = fabriquer_couverture(
        pdf_interieur=str(pdf_interieur),
        thematique=thematique,
        titre=titre,
        sous_titre=sous_titre,
        fichier_sortie=chemin_couverture_pdf
    )

    if not pdf_couverture or not Path(pdf_couverture).exists():
        raise RuntimeError(f"❌ Échec de génération de la couverture : {chemin_couverture_pdf}")

    # --------------------------------------------------------------------------
    # SYNTHÈSE FINALE & VALIDATION
    # --------------------------------------------------------------------------
    taille_int_mo = Path(pdf_interieur).stat().st_size / (1024 * 1024)
    taille_couv_mo = Path(pdf_couverture).stat().st_size / (1024 * 1024)
    largeur_tranche_in = nb_pages * 0.002252
    largeur_tranche_mm = largeur_tranche_in * 25.4

    print("\n" + "=" * 76)
    print("🏆 LIVRE AMAZON KDP PRÊT À LA PUBLICATION !")
    print("=" * 76)
    print(f"1. MANUSCRIT INTÉRIEUR :")
    print(f"   - Fichier  : {Path(pdf_interieur).resolve()}")
    print(f"   - Format   : 6.0 x 9.0 pouces (Standard broché)")
    print(f"   - Pages    : {nb_pages} pages")
    print(f"   - Poids    : {taille_int_mo:.2f} Mo")
    print(f"2. COUVERTURE OFFICIELLE COMPLETE :")
    print(f"   - Fichier  : {Path(pdf_couverture).resolve()}")
    print(f"   - Thème    : {thematique}")
    print(f"   - Tranche  : {largeur_tranche_in:.4f} po ({largeur_tranche_mm:.2f} mm)")
    print(f"   - Résol.   : Haute fidélité 300 DPI")
    print(f"   - Poids    : {taille_couv_mo:.2f} Mo")
    print("=" * 76 + "\n")

    return {
        "status": "success",
        "interieur_pdf": str(Path(pdf_interieur).resolve()),
        "couverture_pdf": str(Path(pdf_couverture).resolve()),
        "nb_pages": nb_pages,
        "tranche_in": largeur_tranche_in,
        "tranche_mm": largeur_tranche_mm
    }


def main():
    parser = argparse.ArgumentParser(description="Pipeline Maître KDP en Un Clic")
    parser.add_argument("--state", default="book_state.json", help="Chemin vers book_state.json")
    parser.add_argument("--source", default="manuscrit_complet.md", help="Chemin vers le fichier Markdown source")
    parser.add_argument("--thematique", default=None, help="Thématique de la couverture (MINDSET, FINANCE, TECH_IA, SANTE, IMMOBILIER, PHILOSOPHIE)")

    args = parser.parse_args()
    try:
        executer_pipeline(
            fichier_state=args.state,
            fichier_md=args.source,
            thematique_forcee=args.thematique
        )
    except Exception as e:
        print(f"\n❌ ERREUR DU PIPELINE : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
