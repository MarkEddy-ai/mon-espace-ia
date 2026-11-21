import json
from datetime import datetime
from pathlib import Path
from kdp_universal_publishing_engine import compiler_livre_sur_mesure

def convertir_manuscrit_en_pdf(chemin_md="manuscrit_complet.md", sortie_html="livre_kdp_interieur.html", sortie_pdf="livre_kdp_interieur.pdf"):
    compiler_livre_sur_mesure(
        chemin_manuscrit=chemin_md,
        chemin_sortie_html=sortie_html,
        format_choisi="6x9",
        thematique_choisie="NON_FICTION",
        titre_livre="LIVRE KDP"
    )
    return Path(sortie_html)

def markdown_vers_html_haute_couture(md_texte: str) -> str:
    from run_kdp_pipeline import convertir_markdown_en_html
    return convertir_markdown_en_html(md_texte)

def generer_manuscrit_markdown(draft: dict, chemin_md: str = "manuscrit_complet.md") -> Path:
    meta = draft.get("metadata", {})
    lignes = [
        f"# {meta.get('titre', 'LIVRE')}",
        f"*{meta.get('sous_titre', '')}*\n",
        f"**Par {meta.get('auteur_suggere', 'MarkEddy')}**\n",
        "---\n",
        f"# Introduction\n\n{draft.get('introduction', '')}\n"
    ]
    for c in draft.get("chapitres_rediges", []):
        lignes.append(f"\n# Chapitre {c.get('numero', 1)} : {c.get('titre', '')}\n")
        for s in c.get("sections_redigees", []):
            # H1 (chapitre) -> H2 (section) : hiérarchie uniforme, le H3 est
            # réservé aux sous-points écrits dans le contenu lui-même.
            lignes.append(f"\n## {s.get('titre', '')}\n\n{s.get('contenu', '')}\n")
    lignes.append(f"\n# Conclusion\n\n{draft.get('conclusion', '')}\n")

    p = Path(chemin_md)
    p.write_text("\n".join(lignes), encoding="utf-8")
    return p

def generer_livre_html_kdp(draft: dict, chemin_html: str = "livre_kdp_interieur.html") -> Path:
    meta = draft.get("metadata", {})
    titre = meta.get("titre", "LIVRE KDP")
    sous_titre = meta.get("sous_titre", "")
    auteur = meta.get("auteur_suggere", "MarkEddy")

    css = """
    @page {
        size: 6in 9in;
        margin: 0.85in;
        @bottom-center { content: counter(page); font-size: 9pt; }
    }
    /* Gouttière KDP : 0.85in à l'intérieur, 0.55in à l'extérieur. */
    @page :left {
        margin-left: 0.55in;
        margin-right: 0.85in;
        @bottom-center { content: counter(page); font-size: 9pt; }
    }
    @page :right {
        margin-left: 0.85in;
        margin-right: 0.55in;
        @bottom-center { content: counter(page); font-size: 9pt; }
    }
    body {
        font-family: 'EB Garamond', Georgia, serif;
        font-size: 10.5pt;
        line-height: 1.45;
        text-align: justify;
        hyphens: auto;
    }
    h1 { font-size: 18pt; text-align: center; page-break-before: always; margin-top: 2in; }
    h2 { font-size: 14pt; margin-top: 1.5em; }
    h3 { font-size: 12pt; margin-top: 1.2em; }
    p { text-indent: 1.2em; margin: 0; }
    .lettrine::first-letter { font-size: 3.2em; float: left; margin-right: 0.1em; line-height: 0.8; }
    """

    corps_html = []
    corps_html.append(f"<h1 style='margin-top: 3in;'>{titre}</h1>")
    if sous_titre:
        corps_html.append(f"<p style='text-align: center; font-style: italic;'>{sous_titre}</p>")
    corps_html.append(f"<p style='text-align: center; margin-top: 2em;'><b>{auteur}</b></p>")

    # Page de copyright immédiatement après la page de titre (règle KDP).
    corps_html.append(
        "<section class='copyright-page' style='page-break-before: always;'>"
        "<h2>Mentions légales</h2>"
        f"<p>© {datetime.now().year} {auteur}. Tous droits réservés.</p>"
        "<p>Aucune partie de cet ouvrage ne peut être reproduite, stockée dans un système "
        "de recherche ou transmise sous quelque forme que ce soit sans autorisation écrite préalable.</p>"
        "<p>Édition Amazon KDP — Dépot légal effectué à la publication.</p>"
        "</section>"
    )

    if draft.get("introduction"):
        corps_html.append(f"<h1>Introduction</h1><p class='lettrine'>{draft.get('introduction')}</p>")

    for c in draft.get("chapitres_rediges", []):
        corps_html.append(f"<h1>Chapitre {c.get('numero')} : {c.get('titre')}</h1>")
        for s in c.get("sections_redigees", []):
            corps_html.append(f"<h2>{s.get('titre')}</h2>")
            corps_html.append(f"<p>{s.get('contenu')}</p>")

    if draft.get("conclusion"):
        corps_html.append(f"<h1>Conclusion</h1><p>{draft.get('conclusion')}</p>")

    document = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>{titre}</title>
    <style>{css}</style>
</head>
<body>
{''.join(corps_html)}
</body>
</html>"""

    p = Path(chemin_html)
    p.write_text(document, encoding="utf-8")
    return p

def generer_description_amazon_kdp(metadata: dict, chemin_desc: str = "kdp_marketing_pack.html") -> Path:
    titre = metadata.get("titre", "")
    sous_titre = metadata.get("sous_titre", "")
    promesse = metadata.get("promesse_client", "")
    html = f"""<h2><b>{titre}</b></h2>
<p><i>{sous_titre}</i></p>
<p><b>{promesse}</b></p>
<h3>Ce que vous découvrirez dans ce livre :</h3>
<ul>
  <li>Méthode pas-à-pas accessible immédiatement</li>
  <li>Cas concrets, calculs précis et études de cas chiffrées</li>
  <li>Plan d'action sous 24h pour des résultats durables</li>
</ul>
<p><b>👉 Cliquez sur « Acheter cet article » pour commencer dès aujourd'hui !</b></p>"""
    p = Path(chemin_desc)
    p.write_text(html, encoding="utf-8")
    return p

def formater_projet_complet(draft_path="book_draft.json", output_dir="."):
    if not Path(draft_path).exists():
        return
    draft = json.loads(Path(draft_path).read_text(encoding="utf-8"))
    generer_manuscrit_markdown(draft, str(Path(output_dir) / "manuscrit_complet.md"))
    generer_livre_html_kdp(draft, str(Path(output_dir) / "livre_kdp_interieur.html"))
    generer_description_amazon_kdp(draft.get("metadata", {}), str(Path(output_dir) / "kdp_marketing_pack.html"))
