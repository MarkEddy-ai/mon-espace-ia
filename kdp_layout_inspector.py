"""
kdp_layout_inspector.py - Agent 08 : Inspecteur Pré-Presse & Auditeur de Mise en Page.
Analyse chirurgicale page par page et élément par élément pour détecter les anomalies :
1. Dédoublement des titres et numérotations parasites (ex: '2.2 2.2 Titre')
2. Fuites de syntaxe Markdown non interprétée (ex: '###', raw symbols)
3. Césures violentes et mots coupés ('hyphens: auto' sur tableaux et titres)
4. Pages blanches, orphelines ou quasi-vides (séparateur '— ❧ —' isolé)
5. Blocs de citations et encadrés vides ou mal formatés
"""

import json
import re
from pathlib import Path
import pypdf

MANUSCRIT_PATH = Path("manuscrit_complet.md")
HTML_PRINT_PATH = Path("livre_imprimable_kdp.html")
HTML_DIGITAL_PATH = Path("livre_numerique_interactif.html")
PDF_PRINT_PATH = Path("livre_imprimable_kdp.pdf")
RAPPORT_JSON = Path("rapport_audit_mise_en_page.json")


def inspecter_manuscrit_markdown(md_path: Path) -> dict:
    resultats = {
        "doublons_numerotation": [],
        "titres_consecutifs_doubles": [],
        "markdown_brut_dans_callout": [],
        "separateurs_orphelins_avant_chapitre": [],
        "lignes_vides_dans_callouts": 0
    }
    if not md_path.exists():
        return resultats

    texte = md_path.read_text(encoding="utf-8")
    lignes = texte.splitlines()

    # 1. Détection des numérotations doubles dans les titres (ex: ### 2.2 2.2)
    m_num_double = re.findall(r"^###\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(.*)$", texte, re.MULTILINE)
    for m in m_num_double:
        resultats["doublons_numerotation"].append({
            "prefixe_1": m[0],
            "prefixe_2": m[1],
            "titre": m[2],
            "brut": f"### {m[0]} {m[1]} {m[2]}"
        })

    # 2. Détection des titres consécutifs identiques
    lignes_md = [l.strip() for l in lignes]
    for i in range(len(lignes_md) - 2):
        l1 = lignes_md[i]
        l2 = lignes_md[i + 1] if i + 1 < len(lignes_md) else ""
        l3 = lignes_md[i + 2] if i + 2 < len(lignes_md) else ""
        
        # Test si H3 suivi d'une ligne vide puis d'un autre H3 très similaire
        if l1.startswith("### ") and l3.startswith("### "):
            t1 = re.sub(r"^###\s*[\d\.\s]*", "", l1).strip().lower()
            t3 = re.sub(r"^###\s*[\d\.\s]*", "", l3).strip().lower()
            if t1 and t1 == t3:
                resultats["titres_consecutifs_doubles"].append({
                    "ligne_1": l1,
                    "ligne_2": l3
                })

    # 3. Fuite Markdown dans les encadrés (> ### ...)
    m_callouts = re.findall(r"^>\s*###\s*(.*)$", texte, re.MULTILINE)
    for c in m_callouts:
        resultats["markdown_brut_dans_callout"].append(c.strip())

    # 4. Séparateurs orphelins avant un chapitre H1 (--- suivi de # Chapitre)
    for i in range(len(lignes_md) - 1):
        if lignes_md[i] == "---":
            # Vérifie les prochaines lignes non vides
            for j in range(i + 1, min(i + 4, len(lignes_md))):
                if lignes_md[j].startswith("# Chapitre") or lignes_md[j].startswith("# Avant-propos") or lignes_md[j].startswith("# Conclusion"):
                    resultats["separateurs_orphelins_avant_chapitre"].append({
                        "ligne_separateur": i + 1,
                        "titre_suivant": lignes_md[j]
                    })
                    break

    return resultats


def inspecter_html(html_path: Path) -> dict:
    resultats = {
        "balises_h3_doubles": 0,
        "syntaxe_markdown_fuite": [],
        "cesures_tableau_actives": False,
        "paragraphes_vides": 0,
        "blockquotes_vides": 0
    }
    if not html_path.exists():
        return resultats

    html = html_path.read_text(encoding="utf-8")

    # Fuites Markdown
    fuites = re.findall(r"<p>\s*#{1,6}\s*(.*?)</p>", html)
    resultats["syntaxe_markdown_fuite"] = fuites

    # Paragraphes vides
    vides = re.findall(r"<p>\s*</p>", html)
    resultats["paragraphes_vides"] = len(vides)

    # Blockquotes vides
    bq_vides = re.findall(r'<blockquote[^>]*>\s*</blockquote>', html)
    resultats["blockquotes_vides"] = len(bq_vides)

    # Césures dans les tableaux
    if "th {" in html and "hyphens: none" not in html[html.find("th {"):html.find("th {") + 350]:
        resultats["cesures_tableau_actives"] = True

    return resultats


def inspecter_pdf_page_par_page(pdf_path: Path) -> dict:
    resultats = {
        "total_pages": 0,
        "pages_quasi_vides": [],
        "pages_avec_doublon_titre": [],
        "pages_avec_syntaxe_brute": [],
        "cesures_suspectes": []
    }
    if not pdf_path.exists():
        return resultats

    reader = pypdf.PdfReader(str(pdf_path))
    resultats["total_pages"] = len(reader.pages)

    for idx, page in enumerate(reader.pages, start=1):
        texte = page.extract_text() or ""
        mots = texte.split()

        # 1. Page quasi-vide (moins de 25 mots hors couverture/faux-titre)
        if idx > 3 and len(mots) < 25:
            # Vérifier si ce n'est pas simplement une page blanche de fin de chapitre
            if any(terme in texte for terme in ["— ❧ —", "❖", "###", "Chapitre"]):
                resultats["pages_quasi_vides"].append({
                    "page": idx,
                    "nb_mots": len(mots),
                    "apercu": texte.strip()[:100]
                })

        # 2. Titres doubles dans la page (ex: 2.2 2.2)
        if re.search(r"\b(\d+\.\d+)\s+\1\b", texte):
            m = re.search(r"\b(\d+\.\d+)\s+\1\s+([^\n]+)", texte)
            resultats["pages_avec_doublon_titre"].append({
                "page": idx,
                "extrait": m.group(0) if m else "Doublon détecté"
            })

        # 3. Présence de syntaxe Markdown brute non parsée
        if "###" in texte:
            resultats["pages_avec_syntaxe_brute"].append({
                "page": idx,
                "extrait": [l for l in texte.splitlines() if "###" in l][:2]
            })

        # 4. Mots coupés en deux avec tiret à la fin d'une ligne dans les titres ou tableaux
        lignes = texte.splitlines()
        for l in lignes:
            # Détection d'un mot en majuscules coupé en fin de ligne (ex: STRATÉ-, LOGIS-, SE-, etc.)
            if re.search(r"\b[A-ZÀ-Ÿ]{2,}-\s*$", l) or re.search(r"\b(STRATÉ|LOGIS|VRAGE|COMPORTE|AUTOMA|SE)-\s*$", l):
                # Ignorer si c'est simplement un tiret de dialogue ou formule reconnue
                resultats["cesures_suspectes"].append({
                    "page": idx,
                    "ligne": l.strip()
                })

    return resultats


def executer_audit_complet() -> dict:
    print("\n" + "=" * 70)
    print("🔬 AGENT 08 : INSPECTEUR PRÉ-PRESSE & AUDITEUR DE MISE EN PAGE")
    print("   Audit Chirurgical Page par Page & Comparaison Standards KDP")
    print("=" * 70)

    audit_md = inspecter_manuscrit_markdown(MANUSCRIT_PATH)
    audit_html = inspecter_html(HTML_PRINT_PATH)
    audit_pdf = inspecter_pdf_page_par_page(PDF_PRINT_PATH)

    total_defauts = (
        len(audit_md["doublons_numerotation"]) +
        len(audit_md["titres_consecutifs_doubles"]) +
        len(audit_md["markdown_brut_dans_callout"]) +
        len(audit_md["separateurs_orphelins_avant_chapitre"]) +
        len(audit_pdf["pages_quasi_vides"]) +
        len(audit_pdf["pages_avec_doublon_titre"]) +
        len(audit_pdf["pages_avec_syntaxe_brute"]) +
        len(audit_pdf["cesures_suspectes"])
    )

    score_mise_en_page = max(0, 100 - (total_defauts * 3))

    rapport = {
        "score_typographique": score_mise_en_page,
        "total_anomalies_detectees": total_defauts,
        "audit_manuscrit_md": audit_md,
        "audit_html_print": audit_html,
        "audit_pdf_print": audit_pdf
    }

    RAPPORT_JSON.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    # Affichage clair du diagnostic
    print(f"\n📊 SCORE TYPOGRAPHIQUE & MISE EN PAGE : {score_mise_en_page}/100")
    print(f"⚠️  TOTAL ANOMALIES DÉTECTÉES : {total_defauts}\n")

    print("🔴 1. TITRES & NUMÉROTATIONS EN DOUBLE :")
    if audit_md["doublons_numerotation"]:
        print(f"  • {len(audit_md['doublons_numerotation'])} titres avec préfixe redoublé (ex: 2.2 2.2)")
        for d in audit_md["doublons_numerotation"][:3]:
            print(f"    - {d['brut']}")
    if audit_md["titres_consecutifs_doubles"]:
        print(f"  • {len(audit_md['titres_consecutifs_doubles'])} sous-titres consécutifs en doublon")
        for t in audit_md["titres_consecutifs_doubles"][:3]:
            print(f"    - Ligne 1: {t['ligne_1']} | Ligne 2: {t['ligne_2']}")
    if not audit_md["doublons_numerotation"] and not audit_md["titres_consecutifs_doubles"]:
        print("  ✅ Zéro titre dédoublé.")

    print("\n🔴 2. SYNTAXE MARKDOWN NON INTERPRÉTÉE (###) :")
    if audit_md["markdown_brut_dans_callout"]:
        print(f"  • {len(audit_md['markdown_brut_dans_callout'])} encadrés avec balises '###' brutes apparentes")
        for c in audit_md["markdown_brut_dans_callout"][:3]:
            print(f"    - > ### {c}")
    else:
        print("  ✅ Zéro balise markdown brute dans les encadrés.")

    print("\n🔴 3. CÉSURES VIOLENTES & MOTS DÉCOUPÉS :")
    if audit_pdf["cesures_suspectes"]:
        print(f"  • {len(audit_pdf['cesures_suspectes'])} césures indésirables détectées dans les titres/tableaux")
        for cs in audit_pdf["cesures_suspectes"][:3]:
            print(f"    - [Page {cs['page']}] {cs['ligne']}")
    else:
        print("  ✅ Typographie saine (aucune césure abusive).")

    print("\n🔴 4. PAGES QUASI-VIDES & SÉPARATEURS ORPHELINS :")
    if audit_pdf["pages_quasi_vides"]:
        print(f"  • {len(audit_pdf['pages_quasi_vides'])} page(s) quasi-vide(s) avec ornement isolé :")
        for pq in audit_pdf["pages_quasi_vides"]:
            print(f"    - Page {pq['page']} : {pq['nb_mots']} mots. Aperçu : {pq['apercu']}")
    if audit_md["separateurs_orphelins_avant_chapitre"]:
        print(f"  • {len(audit_md['separateurs_orphelins_avant_chapitre'])} séparateur(s) '---' placés juste avant un saut de chapitre")
    if not audit_pdf["pages_quasi_vides"] and not audit_md["separateurs_orphelins_avant_chapitre"]:
        print("  ✅ Aucune page orpheline détectée.")

    print("\n" + "=" * 70)
    print(f"📁 Rapport détaillé écrit dans : {RAPPORT_JSON.resolve()}")
    print("=" * 70 + "\n")
    return rapport


if __name__ == "__main__":
    executer_audit_complet()
