"""
kdp_epub_exporter.py — EXPORTATEUR KINDLE / EPUB AUTONOME (Phase 3)
====================================================================

Convertit un livre structuré (titre, auteur, liste de chapitres HTML ou
Markdown) en un fichier ``.epub`` valide, conforme aux spécifications
EPUB 3.0 avec rétrocompatibilité EPUB 2 (NCX) :

    mimetype              (premier de l'archive, NON compressé — exigé par EPUB)
    META-INF/container.xml
    OEBPS/content.opf     (métadonnées DC + manifeste + spine)
    OEBPS/nav.xhtml       (table des matières EPUB 3)
    OEBPS/toc.ncx         (table des matières EPUB 2 / Kindle ancien)
    OEBPS/styles.css      (feuille de style propre, sans dépendance externe)
    OEBPS/text/*.xhtml    (chapitres XHTML strictement bien formés)
    OEBPS/images/*        (couverture facultative)

Aucune dépendance externe au projet : ``markdown``, ``lxml``, ``zipfile``.

Utilisation en bibliothèque
---------------------------
    from kdp_epub_exporter import construire_epub, livre_depuis_manuscrit

    livre = {
        "titre": "Neuro-Focus",
        "auteur": "MarkEddy",
        "chapitres": [
            {"titre": "Chapitre 1", "contenu": "## Sous-titre\n\nDu **texte**."},
        ],
    }
    chemin = construire_epub(livre)          # -> ebooks_finaux/neuro-focus.epub

Utilisation en ligne de commande
--------------------------------
    .venv\\Scripts\\python.exe kdp_epub_exporter.py
    .venv\\Scripts\\python.exe kdp_epub_exporter.py --manuscrit manuscrit_complet.md
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
from xml.sax.saxutils import escape as _echapper_xml

import markdown as _markdown
from lxml import etree, html as _lxml_html

# --------------------------------------------------------------------------
# Constantes du module
# --------------------------------------------------------------------------

DOSSIER_SORTIE = Path("ebooks_finaux")
MIME_EPUB = "application/epub+zip"
NAMESPACE_XHTML = "http://www.w3.org/1999/xhtml"
NAMESPACE_OPF = "http://www.idpf.org/2007/opf"
NAMESPACE_DC = "http://purl.org/dc/elements/1.1/"
NAMESPACE_NCX = "http://www.daisy.org/z3986/2005/ncx/"
NAMESPACE_EPUB_OPS = "http://www.idpf.org/2007/ops"

# Balises supprimées de tous les chapitres (sécurité + propreté EPUB).
_BALISES_REFUSEES = ("script", "style", "iframe", "object", "embed", "link", "meta")

# Étendues Markdown : tableaux, notes, code entre délimiteurs, listes saines.
_ETENDUES_MARKDOWN = ["extra", "sane_lists", "nl2br"]

CSS_EPUB = """/* Feuille de style EPUB — design sobre type livre imprimé 6x9 */
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0 6%;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1em;
  line-height: 1.55;
  text-align: justify;
  hyphens: auto;
}
h1, h2, h3, h4 {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  text-align: left;
  page-break-after: avoid;
  margin: 1.6em 0 0.6em;
}
h1 { font-size: 1.6em; line-height: 1.2; }
h2 { font-size: 1.25em; }
h3 { font-size: 1.08em; }
p { margin: 0 0 0.85em; orphans: 2; widows: 2; }
a { color: inherit; }
hr { border: 0; border-top: 1px solid #999; margin: 1.6em 15%; }
blockquote {
  margin: 1.2em 0;
  padding: 0.2em 1em;
  border-left: 3px solid #888;
  font-style: italic;
  color: #333;
}
ul, ol { margin: 0.8em 0; padding-left: 1.6em; }
li { margin-bottom: 0.35em; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  font-size: 0.92em;
}
th, td { border: 1px solid #999; padding: 0.4em 0.6em; text-align: left; }
th { background: #f0f0f0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
code, pre {
  font-family: "Courier New", Courier, monospace;
  font-size: 0.9em;
}
pre {
  background: #f6f6f6;
  padding: 0.8em;
  overflow-x: auto;
  white-space: pre-wrap;
}
img { max-width: 100%; height: auto; }
.page-titre { text-align: center; margin-top: 22%; }
.page-titre h1 { font-size: 2em; margin-bottom: 0.3em; }
.page-titre .sous-titre { font-style: italic; color: #444; margin-bottom: 2.5em; }
.page-titre .auteur {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 1em;
}
.page-titre .editeur { margin-top: 4em; font-size: 0.85em; color: #666; }
"""

LIVRE_DEFAUT: Dict[str, Any] = {
    "titre": "Livre KDP sans titre",
    "sous_titre": "",
    "auteur": "Auteur indépendant",
    "langue": "fr",
    "editeur": "Publication indépendante Amazon KDP",
    "chapitres": [
        {
            "titre": "Chapitre 1 : Premiers pas",
            "contenu": (
                "## Objectif de ce chapitre\n\n"
                "Ce chapitre pose les bases de la méthode présentée dans cet ouvrage.\n\n"
                "- Une idée par ligne\n"
                "- Une action concrète\n"
                "- Un résultat mesurable\n\n"
                "> **Encadré d'action :** notez dès maintenant votre premier objectif."
            ),
        },
        {
            "titre": "Chapitre 2 : Mise en pratique",
            "contenu": (
                "## De la théorie à l'action\n\n"
                "Appliquez le protocole pendant **7 jours consécutifs**, puis mesurez "
                "l'écart entre votre situation de départ et votre situation actuelle.\n\n"
                "| Jour | Action | Mesure |\n| --- | --- | --- |\n"
                "| 1 | Définir l'objectif | 1 ligne |\n"
                "| 7 | Bilan hebdomadaire | 1 chiffre |"
            ),
        },
    ],
}


# --------------------------------------------------------------------------
# Petits utilitaires
# --------------------------------------------------------------------------

def _slugifier(texte: str, defaut: str = "livre") -> str:
    """Titre -> nom de fichier ASCII sûr (sans accent, sans espace parasite)."""
    brut = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode("ascii")
    brut = re.sub(r"[^a-zA-Z0-9]+", "-", brut).strip("-").lower()
    return brut[:60] or defaut


def _echapper(texte: Any) -> str:
    """Échappement XML simple (texte injecté dans les titres / métadonnées)."""
    return _echapper_xml(str(texte if texte is not None else ""))


def _horaire_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# Conversion HTML / Markdown -> XHTML strict
# --------------------------------------------------------------------------

def markdown_vers_html(texte: str) -> str:
    """Markdown -> fragment HTML (étendues extra + listes saines + retours ligne)."""
    if not texte:
        return ""
    return _markdown.markdown(str(texte), extensions=_ETENDUES_MARKDOWN)


def fragment_en_xhtml(fragment: str) -> str:
    """
    Rend un fragment HTML *bien formé* (XML) : indispensable pour que le
    navigateur Kindle n'abandonne pas la feuille XHTML.

    - analyse tolérante via lxml.html (accepte ``<br>``, ``&nbsp;``, HTML brut)
    - sérialisation XML (``<br/>``, ``&amp;``, entités résolues)
    - suppression des balises non autorisées (script, style, iframe...)
    """
    if not fragment or not str(fragment).strip():
        return ""

    try:
        boite = _lxml_html.fragment_fromstring(str(fragment), create_parent="div")
    except Exception:
        # Fragment exotique : on échappe tout plutôt que de produire un EPUB cassé.
        return f"<p>{_echapper(str(fragment))}</p>"

    for balise in _BALISES_REFUSEES:
        for noeud in boite.xpath(f".//{balise}"):
            parent = noeud.getparent()
            if parent is not None:
                parent.remove(noeud)

    # Les attributs onXXX (onclick, onload...) n'ont aucun sens dans un livre.
    for noeud in boite.iter():
        for attribut in list(noeud.attrib):
            if attribut.lower().startswith("on"):
                del noeud.attrib[attribut]

    corps = etree.tostring(boite, method="xml", encoding="unicode")
    # Retrait de l'enveloppe <div> de travail (conservation du texte nu).
    corps = re.sub(r"^<div[^>]*>", "", corps.strip())
    corps = re.sub(r"</div>$", "", corps)
    return corps.strip()


def _contenu_chapitre(titre: str, contenu: str, est_markdown: bool = True) -> str:
    """
    Corps XHTML d'un chapitre : conversion (si Markdown) puis insertion d'un
    <h1> issu du titre si le contenu n'en porte pas déjà un.
    """
    brut = "" if contenu is None else str(contenu)
    fragment = markdown_vers_html(brut) if est_markdown else brut
    xhtml = fragment_en_xhtml(fragment)

    if not re.search(r"<h1[\s>]", xhtml, flags=re.IGNORECASE):
        xhtml = f"<h1>{_echapper(titre)}</h1>\n{xhtml}".strip()
    return xhtml or f"<h1>{_echapper(titre)}</h1>"


# --------------------------------------------------------------------------
# Normalisation du livre en entrée
# --------------------------------------------------------------------------

def _normaliser_chapitre(index: int, brut: Any) -> Dict[str, Any]:
    """Accepte : dict(titre/contenu|html|markdown), dict(nom/texte) ou simple texte."""
    if isinstance(brut, dict):
        titre = (
            brut.get("titre")
            or brut.get("title")
            or brut.get("nom")
            or brut.get("heading")
            or f"Chapitre {index}"
        )
        contenu = (
            brut.get("contenu")
            or brut.get("content")
            or brut.get("html")
            or brut.get("markdown")
            or brut.get("texte")
            or brut.get("body")
            or ""
        )
        est_markdown = not (
            brut.get("html")
            or str(brut.get("format", "")).lower() in ("html", "xhtml")
        )
    else:
        titre = f"Chapitre {index}"
        contenu = str(brut)
        est_markdown = True

    return {
        "id": f"chapitre_{index:02d}",
        "titre": str(titre).strip(),
        "contenu": str(contenu),
        "est_markdown": bool(est_markdown),
    }


def normaliser_livre(livre: Any) -> Dict[str, Any]:
    """
    Forme canonique du livre :
    ``{titre, sous_titre, auteur, langue, editeur, couverture, chapitres[]}``
    """
    if livre is None:
        source: Dict[str, Any] = dict(LIVRE_DEFAUT)
    elif isinstance(livre, dict):
        source = dict(livre)
    elif isinstance(livre, (list, tuple)):
        source = {"titre": "Livre", "auteur": "Auteur", "chapitres": list(livre)}
    else:
        raise TypeError(f"Format de livre non pris en charge : {type(livre)!r}")

    chapitres_bruts = (
        source.get("chapitres")
        or source.get("chapters")
        or source.get("sections")
        or source.get("parties")
        or []
    )
    if isinstance(chapitres_bruts, dict):  # {titre: contenu}
        chapitres_bruts = [
            {"titre": titre, "contenu": contenu}
            for titre, contenu in chapitres_bruts.items()
        ]

    chapitres = [
        _normaliser_chapitre(i, brut)
        for i, brut in enumerate(chapitres_bruts, start=1)
        if (brut if not isinstance(brut, dict) else True)
    ]
    chapitres = [c for c in chapitres if (c["contenu"] or "").strip() or c["titre"]]

    if not chapitres:
        chapitres = [
            _normaliser_chapitre(i, c) for i, c in enumerate(LIVRE_DEFAUT["chapitres"], 1)
        ]

    return {
        "titre": str(source.get("titre") or source.get("title") or LIVRE_DEFAUT["titre"]),
        "sous_titre": str(source.get("sous_titre") or source.get("subtitle") or ""),
        "auteur": str(source.get("auteur") or source.get("author") or LIVRE_DEFAUT["auteur"]),
        "langue": str(source.get("langue") or source.get("language") or "fr"),
        "editeur": str(source.get("editeur") or source.get("publisher") or ""),
        "couverture": source.get("couverture"),
        "chapitres": chapitres,
    }


# --------------------------------------------------------------------------
# Fabrication des documents internes
# --------------------------------------------------------------------------

def _document_xhtml(titre: str, corps: str, href_css: str = "styles.css",
                    langue: str = "fr") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!DOCTYPE html>\n"
        f'<html xmlns="{NAMESPACE_XHTML}" xml:lang="{langue}" lang="{langue}">\n'
        "<head>\n"
        '<meta charset="UTF-8" />\n'
        f"<title>{_echapper(titre)}</title>\n"
        f'<link rel="stylesheet" type="text/css" href="{href_css}" />\n'
        "</head>\n"
        "<body>\n"
        f"{corps}\n"
        "</body>\n"
        "</html>\n"
    )


def _page_titre_xhtml(livre: Dict[str, Any]) -> str:
    parties = [f'<h1>{_echapper(livre["titre"])}</h1>']
    if livre["sous_titre"]:
        parties.append(f'<p class="sous-titre">{_echapper(livre["sous_titre"])}</p>')
    else:
        parties.append('<p class="sous-titre">&nbsp;</p>')
    parties.append(f'<p class="auteur">{_echapper(livre["auteur"])}</p>')
    if livre["editeur"]:
        parties.append(f'<p class="editeur">{_echapper(livre["editeur"])}</p>')
    return _document_xhtml(
        livre["titre"],
        '<div class="page-titre">\n' + "\n".join(parties) + "\n</div>",
    )


def _container_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        "  <rootfiles>\n"
        '    <rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n"
        "</container>\n"
    )


def _content_opf(livre: Dict[str, Any], uid: str, fichiers: Sequence[Dict[str, str]],
                 manifeste_couverture: Optional[Dict[str, str]]) -> str:
    items = []
    items.append(
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" '
        'properties="nav"/>'
    )
    items.append('    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    items.append('    <item id="css" href="styles.css" media-type="text/css"/>')
    items.append(
        '    <item id="page_titre" href="text/page_titre.xhtml" '
        'media-type="application/xhtml+xml"/>'
    )
    for f in fichiers:
        items.append(
            f'    <item id="{f["id"]}" href="{f["href"]}" '
            'media-type="application/xhtml+xml"/>'
        )
    if manifeste_couverture:
        items.append(
            f'    <item id="{manifeste_couverture["id"]}" '
            f'href="{manifeste_couverture["href"]}" '
            f'media-type="{manifeste_couverture["media_type"]}" '
            'properties="cover-image"/>'
        )

    itemrefs = ['    <itemref idref="page_titre"/>']
    itemrefs += [f'    <itemref idref="{f["id"]}"/>' for f in fichiers]

    meta_couverture = ""
    if manifeste_couverture:
        meta_couverture = (
            f'\n    <meta name="cover" content="{manifeste_couverture["id"]}"/>'
        )

    date_modif = _horaire_iso()
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<package xmlns="{NAMESPACE_OPF}" version="3.0" unique-identifier="bookid">\n'
        "  <metadata>\n"
        f'    <dc:identifier id="bookid">{_echapper(uid)}</dc:identifier>\n'
        f"    <dc:title>{_echapper(livre['titre'])}</dc:title>\n"
        f"    <dc:creator>{_echapper(livre['auteur'])}</dc:creator>\n"
        f"    <dc:language>{_echapper(livre['langue'])}</dc:language>\n"
        f"    <dc:publisher>{_echapper(livre['editeur'])}</dc:publisher>\n"
        f'    <dc:date>{datetime.now(timezone.utc).strftime("%Y-%m-%d")}</dc:date>\n'
        f'    <meta property="dcterms:modified">{date_modif}</meta>'
        f"{meta_couverture}\n"
        "  </metadata>\n"
        "  <manifest>\n"
        + "\n".join(items)
        + "\n  </manifest>\n"
        "  <spine toc=\"ncx\">\n"
        + "\n".join(itemrefs)
        + "\n  </spine>\n"
        "</package>\n"
    )


def _toc_ncx(livre: Dict[str, Any], uid: str, fichiers: Sequence[Dict[str, str]]) -> str:
    points = [
        '    <navPoint id="navpoint-titre" playOrder="1">\n'
        "      <navLabel><text>Page de titre</text></navLabel>\n"
        '      <content src="text/page_titre.xhtml"/>\n'
        "    </navPoint>"
    ]
    for i, f in enumerate(fichiers, start=2):
        points.append(
            f'    <navPoint id="navpoint-{i}" playOrder="{i}">\n'
            f"      <navLabel><text>{_echapper(f['titre'])}</text></navLabel>\n"
            f'      <content src="{f["href"]}"/>\n'
            "    </navPoint>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<ncx xmlns="{NAMESPACE_NCX}" version="2005-1">\n'
        "  <head>\n"
        f'    <meta name="dtb:uid" content="{_echapper(uid)}"/>\n'
        '    <meta name="dtb:depth" content="1"/>\n'
        '    <meta name="dtb:totalPageCount" content="0"/>\n'
        '    <meta name="dtb:maxPageNumber" content="0"/>\n'
        "  </head>\n"
        f"  <docTitle><text>{_echapper(livre['titre'])}</text></docTitle>\n"
        f"  <docAuthor><text>{_echapper(livre['auteur'])}</text></docAuthor>\n"
        "  <navMap>\n"
        + "\n".join(points)
        + "\n  </navMap>\n"
        "</ncx>\n"
    )


def _nav_xhtml(livre: Dict[str, Any], fichiers: Sequence[Dict[str, str]]) -> str:
    entrees = [
        '      <li><a href="text/page_titre.xhtml">Page de titre</a></li>'
    ]
    for f in fichiers:
        entrees.append(
            f'      <li><a href="{f["href"]}">{_echapper(f["titre"])}</a></li>'
        )

    corps = (
        f'<nav epub:type="toc" id="toc">\n'
        f"  <h1>Table des matières</h1>\n"
        f"  <ol>\n" + "\n".join(entrees) + "\n  </ol>\n</nav>"
    )
    document = _document_xhtml(f"Table des matières — {livre['titre']}", corps)
    # Déclaration du préfixe epub requis par la spécification EPUB 3.
    document = document.replace(
        f'<html xmlns="{NAMESPACE_XHTML}"',
        f'<html xmlns="{NAMESPACE_XHTML}" xmlns:epub="{NAMESPACE_EPUB_OPS}"',
        1,
    )
    return document


# --------------------------------------------------------------------------
# Assemblage de l'archive
# --------------------------------------------------------------------------

def construire_epub(
    livre: Any,
    dossier_sortie: Optional[Path] = None,
    chemin_sortie: Optional[Path] = None,
    nom_fichier: Optional[str] = None,
) -> Path:
    """
    Fabrique le fichier ``.epub`` et renvoie son chemin absolu.

    :param livre: dictionnaire structuré (titre, auteur, chapitres[...])
    :param dossier_sortie: dossier cible (défaut : ``ebooks_finaux/``)
    :param chemin_sortie: chemin complet prioritaires sur dossier + nom
    :param nom_fichier: nom de fichier optionnel (défaut : slug du titre)
    :return: chemin absolu du fichier .epub créé
    """
    data = normaliser_livre(livre)

    if chemin_sortie is None:
        dossier = Path(dossier_sortie) if dossier_sortie else DOSSIER_SORTIE
        fichier = f"{_slugifier(data['titre'])}.epub"
        if nom_fichier:
            fichier = nom_fichier if nom_fichier.endswith(".epub") else f"{nom_fichier}.epub"
        chemin_sortie = dossier / fichier
    chemin_sortie = Path(chemin_sortie)
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"kdp:{data['titre']}:{data['auteur']}"))
    langue = data["langue"]

    # --- chapitres -> fichiers XHTML ------------------------------------
    fichiers: List[Dict[str, str]] = []
    contenus: List[Dict[str, str]] = []
    for chapitre in data["chapitres"]:
        href = f"text/{chapitre['id']}.xhtml"
        corps = _contenu_chapitre(chapitre["titre"], chapitre["contenu"], chapitre["est_markdown"])
        document = _document_xhtml(chapitre["titre"], corps, href_css="../styles.css",
                                   langue=langue)
        fichiers.append({"id": chapitre["id"], "href": href, "titre": chapitre["titre"]})
        contenus.append({"href": href, "document": document})

    # --- couverture facultative ----------------------------------------
    manifeste_couverture: Optional[Dict[str, str]] = None
    donnees_couverture: Optional[bytes] = None
    chemin_couverture = data.get("couverture")
    if chemin_couverture:
        source = Path(chemin_couverture)
        if source.is_file():
            extension = source.suffix.lower().lstrip(".")
            types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                     "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}
            media_type = types.get(extension, "image/jpeg")
            extension = "jpg" if media_type == "image/jpeg" else extension
            manifeste_couverture = {
                "id": "cover-image",
                "href": f"images/cover.{extension}",
                "media_type": media_type,
            }
            donnees_couverture = source.read_bytes()

    # --- écriture de l'archive -----------------------------------------
    with zipfile.ZipFile(chemin_sortie, "w") as archive:
        # 1) mimetype : PREMIER élément, NON compressé (exigence EPUB/Kindle).
        info = zipfile.ZipInfo("mimetype", date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = 0o644 << 16
        archive.writestr(info, MIME_EPUB)

        # 2) conteneur OEBPS
        _ecrire(archive, "META-INF/container.xml", _container_xml())
        _ecrire(archive, "OEBPS/content.opf",
                _content_opf(data, uid, fichiers, manifeste_couverture))
        _ecrire(archive, "OEBPS/toc.ncx", _toc_ncx(data, uid, fichiers))
        _ecrire(archive, "OEBPS/nav.xhtml", _nav_xhtml(data, fichiers))
        _ecrire(archive, "OEBPS/styles.css", CSS_EPUB)

        # 3) texte
        _ecrire(archive, "OEBPS/text/page_titre.xhtml", _page_titre_xhtml(data))
        for entree in contenus:
            _ecrire(archive, f"OEBPS/{entree['href']}", entree["document"])

        # 4) couverture
        if manifeste_couverture and donnees_couverture is not None:
            _ecrire_binaire(archive, f"OEBPS/{manifeste_couverture['href']}", donnees_couverture)

    return chemin_sortie.resolve()


def _ecrire(archive: zipfile.ZipFile, nom: str, texte: str) -> None:
    archive.writestr(
        zipfile.ZipInfo(nom, date_time=(1980, 1, 1, 0, 0, 0)),
        texte.encode("utf-8"),
        compress_type=zipfile.ZIP_DEFLATED,
    )


def _ecrire_binaire(archive: zipfile.ZipFile, nom: str, donnees: bytes) -> None:
    archive.writestr(
        zipfile.ZipInfo(nom, date_time=(1980, 1, 1, 0, 0, 0)),
        donnees,
        compress_type=zipfile.ZIP_DEFLATED,
    )


# --------------------------------------------------------------------------
# Chargement d'un livre depuis l'état du pipeline
# --------------------------------------------------------------------------

def _chapitres_depuis_markdown(texte: str) -> List[Dict[str, Any]]:
    """Découpe un manuscrit Markdown sur les titres de niveau 1 (``# ``)."""
    chapitres: List[Dict[str, Any]] = []
    titre_courant = "Ouvrage"
    lignes_courantes: List[str] = []

    def _verser() -> None:
        contenu = "\n".join(lignes_courantes).strip()
        if contenu or titre_courant:
            chapitres.append({"titre": titre_courant, "contenu": contenu})

    for ligne in str(texte).splitlines():
        if re.match(r"^#\s+\S", ligne):
            _verser()
            titre_courant = re.sub(r"^#\s+", "", ligne).strip()
            lignes_courantes = []
        else:
            lignes_courantes.append(ligne)
    _verser()

    # Le premier bloc (souvent un titre de couverture) n'est pas un chapitre utile
    # s'il est vide : on le garde quand même s'il contient du texte.
    return [c for c in chapitres if (c["contenu"] or c["titre"])]


def livre_depuis_etat(
    chemin_etat: Path = Path("book_state.json"),
    chemin_manuscrit: Path = Path("manuscrit_complet.md"),
    titre_defaut: str = "",
    auteur_defaut: str = "Auteur indépendant",
) -> Dict[str, Any]:
    """
    Charge le livre structuré du pipeline, avec repli dégradé :

    1. ``book_state.json`` (plusieurs structures acceptées)
    2. ``manuscrit_complet.md`` découpé sur les titres ``# ``
    3. le livre par défaut du module
    """
    etat = Path(chemin_etat)
    if etat.is_file():
        try:
            brut = json.loads(etat.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            brut = None
        if isinstance(brut, dict):
            source = brut.get("livre") if isinstance(brut.get("livre"), dict) else brut
            chapitres = (
                source.get("chapitres")
                or source.get("chapters")
                or source.get("sections")
                or []
            )
            if chapitres:
                livre = {
                    "titre": source.get("titre") or titre_defaut or LIVRE_DEFAUT["titre"],
                    "sous_titre": source.get("sous_titre", ""),
                    "auteur": source.get("auteur") or auteur_defaut,
                    "langue": source.get("langue", "fr"),
                    "editeur": source.get("editeur", ""),
                    "couverture": source.get("couverture"),
                    "chapitres": chapitres,
                }
                return normaliser_livre(livre)
            # État sans chapitres exploitables mais avec un manuscrit inline.
            for clee in ("manuscrit", "markdown", "contenu", "texte"):
                if isinstance(source.get(clee), str) and source[clee].strip():
                    return livre_depuis_manuscrit(
                        source[clee],
                        titre=source.get("titre") or titre_defaut,
                        auteur=source.get("auteur") or auteur_defaut,
                    )

    manuscrit = Path(chemin_manuscrit)
    if manuscrit.is_file():
        texte = manuscrit.read_text(encoding="utf-8", errors="replace")
        if texte.strip():
            return livre_depuis_manuscrit(texte, titre=titre_defaut, auteur=auteur_defaut)

    livre_defaut = dict(LIVRE_DEFAUT)
    if titre_defaut:
        livre_defaut["titre"] = titre_defaut
    if auteur_defaut:
        livre_defaut["auteur"] = auteur_defaut
    return normaliser_livre(livre_defaut)


def livre_depuis_manuscrit(
    texte_markdown: str,
    titre: str = "",
    auteur: str = "Auteur indépendant",
    sous_titre: str = "",
) -> Dict[str, Any]:
    """Manuscrit Markdown -> livre structuré (titre extrait du 1er ``# `` si absent)."""
    chapitres = _chapitres_depuis_markdown(texte_markdown)
    if not titre:
        titre = chapitres[0]["titre"] if chapitres else "Livre KDP"
        if chapitres:
            chapitres = chapitres[1:] or chapitres
    return normaliser_livre(
        {
            "titre": titre,
            "sous_titre": sous_titre,
            "auteur": auteur,
            "chapitres": chapitres,
        }
    )


# --------------------------------------------------------------------------
# Interface ligne de commande
# --------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exporte un livre structuré en fichier .epub Kindle valide."
    )
    parser.add_argument("--etat", default="book_state.json",
                        help="Fichier d'état JSON du pipeline (défaut : book_state.json)")
    parser.add_argument("--manuscrit", default="manuscrit_complet.md",
                        help="Manuscrit Markdown de repli (défaut : manuscrit_complet.md)")
    parser.add_argument("--titre", default="", help="Titre du livre (optionnel)")
    parser.add_argument("--auteur", default="Auteur indépendant", help="Auteur du livre")
    parser.add_argument("--sortie", default=str(DOSSIER_SORTIE),
                        help="Dossier de sortie (défaut : ebooks_finaux)")
    parser.add_argument("--fichier", default=None, help="Nom de fichier .epub optionnel")
    args = parser.parse_args(argv)

    livre = livre_depuis_etat(
        chemin_etat=Path(args.etat),
        chemin_manuscrit=Path(args.manuscrit),
        titre_defaut=args.titre,
        auteur_defaut=args.auteur,
    )
    chemin = construire_epub(
        livre,
        dossier_sortie=Path(args.sortie),
        nom_fichier=args.fichier,
    )

    with zipfile.ZipFile(chemin) as archive:
        poids = archive.getinfo("mimetype").file_size
        nb_fichiers = len(archive.namelist())

    print("=" * 70)
    print("📦 EXPORT EPUB / KINDLE")
    print("=" * 70)
    print(f"Titre        : {livre['titre']}")
    print(f"Auteur       : {livre['auteur']}")
    print(f"Chapitres    : {len(livre['chapitres'])}")
    print(f"Fichier      : {chemin}")
    print(f"Taille       : {chemin.stat().st_size / 1024:.1f} Ko ({nb_fichiers} entrées)")
    print(f"mimetype     : {poids} octets, non compressé, en tête d'archive ✔")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
