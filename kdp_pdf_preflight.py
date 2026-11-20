"""
kdp_pdf_preflight.py — CONTRÔLEUR PRÉFLIGHT PDF RÉEL (Phase 3)
===============================================================

Inspecte *réellement* les PDF produits par le pipeline (au contraire d'une
simple estimation sur le Markdown) grâce à **pypdf** (ou PyMuPDF ``fitz``
s'il est installé) :

1. **Dimensions exactes en pouces** — 6,000 x 9,000 po pour l'intérieur,
   9,250 po de haut (9,00 + 2 x 0,125 de fond perdu) et ≥ 12,250 po de large
   pour une couverture 6x9 (soit 2 tranches + dos + fond perdu).
2. **Nombre de pages** — intérieur ≥ 1 page, couverture strictement 1 page.
3. **Pages blanches involontaires** — page sans texte extrait, sans image et
   sans aucune opération de traçage/affichage dans le flux de contenu.
4. **Polices incorporées** — chaque police doit posséder un sous-fichier
   ``/FontFile``, ``/FontFile2`` ou ``/FontFile3`` (exigence d'impression
   Amazon KDP ; les 14 polices standard et les polices système sont refusées).

Le module est autonome : il ne modifie ni ``server.py`` ni les gabarits.

Utilisation en bibliothèque
---------------------------
    from kdp_pdf_preflight import inspecter_dossiers, inspecter_pdf
    rapport = inspecter_dossiers()                       # dict complet
    detail  = inspecter_pdf("interieurs_finaux/Interieur_6.0x9.0.pdf")

Utilisation en ligne de commande
--------------------------------
    .venv\\Scripts\\python.exe kdp_pdf_preflight.py
    .venv\\Scripts\\python.exe kdp_pdf_preflight.py --rapport rapport_preflight_reel.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pypdf
from pypdf.generic import ArrayObject, DictionaryObject

# --------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------

POUCE_EN_POINTS = 72.0          # 1 pouce = 72 points typographiques
TOLERANCE_PO = 0.02             # tolérance de mesure (2 centièmes de pouce)
EPAISSEUR_PAGE_KDP = 0.002252   # pouces / page (papier blanc standard KDP)
FOND_PERDU_PO = 0.125           # 0,125 po de bleed sur tout le pourtour
LARGEUR_MIN_COUVERTURE_6X9 = 2 * 6.0 + (2 * FOND_PERDU_PO)  # 12,250 po

DOSSIERS_INTERIEURS = Path("interieurs_finaux")
DOSSIERS_COUVERTURES = Path("couvertures_finales")
RAPPORT_DEFAUT = Path("rapport_preflight_reel.json")

# Opérateurs de flux de contenu qui produisent effectivement un rendu visible.
# (q/Q/cm/gs/rg/W/n... ne dessinent rien à eux seuls → ignorés.)
OPERATEURS_RENDU = {
    b"m", b"l", b"c", b"v", b"y", b"re",              # construction de chemin
    b"f", b"f*", b"S", b"s", b"B", b"B*", b"b", b"b*",  # peinture
    b"Do", b"ID",                                      # XObject / image en ligne
    b"Tj", b"TJ", b"'", b'"',                          # affichage de texte
}

EXIGENCES: Dict[str, Dict[str, Any]] = {
    "interieur": {
        "largeur_po": 6.0,
        "hauteur_po": 9.0,
        "tolerance_po": TOLERANCE_PO,
        "pages_min": 1,
        "pages_max": None,
    },
    "couverture": {
        "largeur_po": None,               # dépend de l'épaisseur du dos
        "hauteur_po": 9.25,               # 9,00 + 2 x 0,125 de fond perdu
        "largeur_min_po": LARGEUR_MIN_COUVERTURE_6X9,
        "tolerance_po": TOLERANCE_PO,
        "pages_min": 1,
        "pages_max": 1,                   # une couverture = une seule page
    },
}


# --------------------------------------------------------------------------
# Détection : page réellement rendue / blanche
# --------------------------------------------------------------------------

def _operations_rendu(page) -> List[bytes]:
    """Opérateurs de dessin/texte présents dans le flux de contenu de la page."""
    flux = page.get_contents()
    if flux is None:
        return []
    try:
        operations = flux.operations or []
    except Exception:
        return []

    rendus: List[bytes] = []
    for entree in operations:
        # pypdf expose [opérateur, opérandes] (parfois sous forme de tuple).
        if isinstance(entree, (list, tuple)) and len(entree) == 2:
            premier, second = entree
            operateur = premier if isinstance(premier, bytes) else second
        elif isinstance(entree, bytes):
            operateur = entree
        else:
            continue
        if operateur in OPERATEURS_RENDU:
            rendus.append(operateur)
    return rendus


def _compter_images(page) -> int:
    """Nombre d'images (XObject /Image) posées sur la page, flux racine seulement."""
    ressources = page.get("/Resources")
    if not ressources:
        return 0
    xobjects = ressources.get("/XObject")
    if not xobjects:
        return 0
    total = 0
    try:
        for valeur in xobjects.values():
            objet = valeur.get_object()
            if str(objet.get("/Subtype", "")) == "/Image":
                total += 1
    except Exception:
        return total
    return total


def analyser_page(page, numero: int) -> Dict[str, Any]:
    """Diagnostic complet d'une page : texte, images, rendu, statut 'blanche'."""
    try:
        texte = page.extract_text() or ""
    except Exception:
        texte = ""
    texte = texte.strip()
    images = _compter_images(page)
    operations = _operations_rendu(page)
    blanche = not texte and images == 0 and len(operations) == 0
    return {
        "page": numero,
        "caracteres_texte": len(texte),
        "images": images,
        "operations_rendu": len(operations),
        "blanche": blanche,
    }


# --------------------------------------------------------------------------
# Détection : polices incorporées
# --------------------------------------------------------------------------

def _descripteurs_de_police(f_police) -> List[Any]:
    """Descripteurs de police d'une entrée /Font (simple ou Type0/composite)."""
    descripteurs: List[Any] = []
    try:
        if "/FontDescriptor" in f_police:
            descripteurs.append(f_police["/FontDescriptor"])
        for descendant in f_police.get("/DescendantFonts", []) or []:
            descendant = descendant.get_object()
            if "/FontDescriptor" in descendant:
                descripteurs.append(descendant["/FontDescriptor"])
        # Certains générateurs placent directement le sous-fichier dans la police.
        if any(cle in f_police for cle in ("/FontFile", "/FontFile2", "/FontFile3")):
            descripteurs.append(f_police)
    except Exception:
        pass
    return descripteurs


def police_incorporee(f_police) -> bool:
    """
    True si la police embarque réellement ses glyphes.

    - ``/Type3`` : glyphes décrits en opérateurs PDF → intrinsèquement embarqués.
    - sinon : présence obligatoire de ``/FontFile``, ``/FontFile2`` ou
      ``/FontFile3`` sur le descripteur (polices standard 14 = non embarquées).
    """
    try:
        sous_type = str(f_police.get("/Subtype", ""))
    except Exception:
        return False
    if sous_type == "/Type3":
        return True
    for descripteur in _descripteurs_de_police(f_police):
        try:
            descripteur = descripteur.get_object()
            if any(cle in descripteur for cle in ("/FontFile", "/FontFile2", "/FontFile3")):
                return True
        except Exception:
            continue
    return False


def polices_non_incorporees(page) -> List[str]:
    """Noms des polices de la page qui ne sont PAS embarquées dans le PDF."""
    ressources = page.get("/Resources")
    if not ressources:
        return []
    polices = ressources.get("/Font")
    if not polices:
        return []

    manquantes: List[str] = []
    try:
        entrees = polices.items()
    except Exception:
        return []
    for nom, valeur in entrees:
        try:
            f_police = valeur.get_object()
            base = str(f_police.get("/BaseFont") or nom)
            if not police_incorporee(f_police):
                manquantes.append(base.lstrip("/"))
        except Exception:
            manquantes.append(str(nom))
    return sorted(set(manquantes))


# --------------------------------------------------------------------------
# Inspection d'un PDF
# --------------------------------------------------------------------------

def _type_document(chemin: Path, explicite: Optional[str] = None) -> str:
    if explicite in EXIGENCES:
        return explicite
    dossier = chemin.parent.name.lower()
    if "couverture" in dossier or "cover" in dossier:
        return "couverture"
    if "interieur" in dossier or "intérieur" in dossier:
        return "interieur"
    return "inconnu"


def inspecter_pdf(
    chemin: Path | str,
    type_document: Optional[str] = None,
    spec: Optional[Dict[str, Any]] = None,
    pages_interieur: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Inspection complète d'un fichier PDF.

    :param chemin: chemin du PDF
    :param type_document: ``"interieur"``, ``"couverture"`` ou ``None`` (déduit)
    :param spec: surcharge des exigences (voir ``EXIGENCES``)
    :param pages_interieur: nombre de pages de l'intérieur, pour vérifier la
        cohérence de l'épaisseur du dos sur la couverture
    :return: rapport détaillé (statut, dimensions, pages blanches, polices...)
    """
    fichier = Path(chemin)
    categorie = _type_document(fichier, type_document)
    exigences = dict(EXIGENCES.get(categorie, {}))
    if spec:
        exigences.update(spec)

    rapport: Dict[str, Any] = {
        "fichier": str(fichier),
        "type_document": categorie,
        "statut": "ERREUR",
        "pages": 0,
        "largeur_po": None,
        "hauteur_po": None,
        "dimensions_ok": False,
        "pages_blanches": [],
        "polices_non_incorporees": [],
        "anomalies": [],
        "avertissements": [],
    }

    if not fichier.is_file():
        rapport["anomalies"].append(f"ERREUR : fichier introuvable — {fichier}")
        return rapport

    try:
        lecteur = pypdf.PdfReader(str(fichier))
        nb_pages = len(lecteur.pages)
    except Exception as exc:
        rapport["anomalies"].append(f"ERREUR : PDF illisible — {exc}")
        return rapport

    if nb_pages == 0:
        rapport["anomalies"].append("ERREUR : le document ne contient aucune page.")
        return rapport

    # --- dimensions (première page, en pouces) ---------------------------
    page0 = lecteur.pages[0]
    largeur = float(page0.mediabox.width) / POUCE_EN_POINTS
    hauteur = float(page0.mediabox.height) / POUCE_EN_POINTS
    rotation = int(page0.get("/Rotate", 0) or 0) % 360

    rapport["pages"] = nb_pages
    rapport["largeur_po"] = round(largeur, 4)
    rapport["hauteur_po"] = round(hauteur, 4)
    rapport["rotation_deg"] = rotation

    if rotation in (90, 270):
        largeur, hauteur = hauteur, largeur
        rapport["largeur_utile_po"] = round(largeur, 4)
        rapport["hauteur_utile_po"] = round(hauteur, 4)
        rapport["avertissements"].append(
            f"ALERTE : page tournée de {rotation}° (dimensions permutées pour la mesure)."
        )

    # --- exigences de format --------------------------------------------
    tol = float(exigences.get("tolerance_po", TOLERANCE_PO))
    attendu_largeur = exigences.get("largeur_po")
    attendu_hauteur = exigences.get("hauteur_po")
    largeur_min = exigences.get("largeur_min_po")

    dimensions_ok = True
    if attendu_hauteur is not None and abs(hauteur - attendu_hauteur) > tol:
        dimensions_ok = False
        rapport["anomalies"].append(
            f"ERREUR : hauteur {hauteur:.4f} po au lieu de {attendu_hauteur:.4f} po "
            f"(±{tol} po)."
        )
    if attendu_largeur is not None and abs(largeur - attendu_largeur) > tol:
        dimensions_ok = False
        rapport["anomalies"].append(
            f"ERREUR : largeur {largeur:.4f} po au lieu de {attendu_largeur:.4f} po "
            f"(±{tol} po)."
        )
    if largeur_min is not None and largeur < largeur_min - tol:
        dimensions_ok = False
        rapport["anomalies"].append(
            f"ERREUR : largeur {largeur:.4f} po inférieure au minimum {largeur_min:.4f} po "
            "(2 tranches de 6 po + fond perdu)."
        )

    # Cohérence du dos : largeur couverture - (2 x 6 + 2 x 0,125) = tranche.
    if categorie == "couverture" and largeur_min is not None:
        dos_po = largeur - LARGEUR_MIN_COUVERTURE_6X9
        pages_dos = round(dos_po / EPAISSEUR_PAGE_KDP, 1) if dos_po > 0 else 0.0
        rapport["dos_estime_pages"] = pages_dos
        if pages_interieur:
            ecart = abs(pages_dos - pages_interieur)
            if ecart > max(3.0, 0.03 * pages_interieur):
                rapport["avertissements"].append(
                    f"ALERTE : le dos calculé ({pages_dos} pages) diffère de l'intérieur "
                    f"({pages_interieur} pages) — vérifier le nombre de pages KDP."
                )
            else:
                rapport["dos_conforme_intérieur"] = True

    # --- nombre de pages -------------------------------------------------
    pages_min = exigences.get("pages_min")
    pages_max = exigences.get("pages_max")
    if pages_min is not None and nb_pages < pages_min:
        dimensions_ok = False
        rapport["anomalies"].append(
            f"ERREUR : {nb_pages} page(s) au minimum requis : {pages_min}."
        )
    if pages_max is not None and nb_pages > pages_max:
        dimensions_ok = False
        rapport["anomalies"].append(
            f"ERREUR : {nb_pages} pages pour un document autorisé à en avoir {pages_max} au maximum."
        )
    if categorie == "interieur" and 0 < nb_pages < 24:
        rapport["avertissements"].append(
            f"ALERTE : {nb_pages} pages seulement (Amazon KDP impose 24 pages minimum "
            "pour un livre broché)."
        )

    # --- pages blanches + polices incorporées ----------------------------
    polices_manquantes: set = set()
    for numero, page in enumerate(lecteur.pages, start=1):
        diagnostic = analyser_page(page, numero)
        if diagnostic["blanche"]:
            rapport["pages_blanches"].append(numero)
        for nom_police in polices_non_incorporees(page):
            polices_manquantes.add(nom_police)

    rapport["polices_non_incorporees"] = sorted(polices_manquantes)

    if rapport["pages_blanches"]:
        liste = ", ".join(str(p) for p in rapport["pages_blanches"][:15])
        suffixe = "…" if len(rapport["pages_blanches"]) > 15 else ""
        rapport["anomalies"].append(
            f"ERREUR : {len(rapport['pages_blanches'])} page(s) blanche(s) involontaire(s) "
            f"page {liste}{suffixe}."
        )
    if rapport["polices_non_incorporees"]:
        rapport["anomalies"].append(
            "ERREUR : polices non incorporées (refusées à l'impression KDP) : "
            + ", ".join(rapport["polices_non_incorporees"])
        )

    rapport["statut"] = "CONFORME" if not rapport["anomalies"] else "ANOMALIE"
    rapport["dimensions_ok"] = dimensions_ok
    return rapport


# --------------------------------------------------------------------------
# Inspection de dossiers entiers
# --------------------------------------------------------------------------

def inspecter_dossier(
    dossier: Path | str,
    type_document: Optional[str] = None,
    spec: Optional[Dict[str, Any]] = None,
    pages_interieur: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Inspecte tous les ``*.pdf`` d'un dossier (tri alphabétique)."""
    chemin_dossier = Path(dossier)
    if not chemin_dossier.is_dir():
        return []
    return [
        inspecter_pdf(fichier, type_document=type_document, spec=spec,
                      pages_interieur=pages_interieur)
        for fichier in sorted(chemin_dossier.glob("*.pdf"))
    ]


def _pages_interieur_reference(dossier_interieurs: Path) -> Optional[int]:
    """Nombre de pages de l'intérieur de référence (le plus complet du dossier)."""
    if not dossier_interieurs.is_dir():
        return None
    meilleurs: Optional[int] = None
    for fichier in sorted(dossier_interieurs.glob("*.pdf")):
        try:
            nb = len(pypdf.PdfReader(str(fichier)).pages)
        except Exception:
            continue
        if meilleurs is None or nb > meilleurs:
            meilleurs = nb
    return meilleurs


def inspecter_dossiers(
    dossier_interieurs: Path | str = DOSSIERS_INTERIEURS,
    dossier_couvertures: Path | str = DOSSIERS_COUVERTURES,
    spec_interieur: Optional[Dict[str, Any]] = None,
    spec_couverture: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Rapport global : intérieurs **et** couvertures, avec vérification croisée
    dos de couverture ↔ nombre de pages de l'intérieur.
    """
    interieurs = Path(dossier_interieurs)
    couvertures = Path(dossier_couvertures)
    pages_ref = _pages_interieur_reference(interieurs)

    detail_interieurs = inspecter_dossier(
        interieurs, type_document="interieur", spec=spec_interieur
    )
    detail_couvertures = inspecter_dossier(
        couvertures,
        type_document="couverture",
        spec=spec_couverture,
        pages_interieur=pages_ref,
    )

    tous = detail_interieurs + detail_couvertures
    conformes = sum(1 for r in tous if r["statut"] == "CONFORME")
    erreurs = sum(1 for r in tous if r["statut"] == "ERREUR")

    return {
        "genere_le": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "moteur": f"pypdf {pypdf.__version__}",
        "dossiers": {
            "interieurs": str(interieurs),
            "couvertures": str(couvertures),
            "interieurs_trouves": len(detail_interieurs),
            "couvertures_trouvees": len(detail_couvertures),
        },
        "pages_interieur_reference": pages_ref,
        "interieurs": detail_interieurs,
        "couvertures": detail_couvertures,
        "synthese": {
            "total": len(tous),
            "conformes": conformes,
            "avec_anomalies": len(tous) - conformes - erreurs,
            "illisible_ou_absent": erreurs,
            "pages_blanches_total": sum(len(r["pages_blanches"]) for r in tous),
            "polices_non_incorporees_total": sum(
                len(r["polices_non_incorporees"]) for r in tous
            ),
        },
    }


def generer_rapport(rapport: Dict[str, Any],
                    chemin: Path | str = RAPPORT_DEFAUT) -> Path:
    """Sérialise le rapport JSON (UTF-8) et renvoie son chemin."""
    chemin = Path(chemin)
    chemin.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return chemin.resolve()


# --------------------------------------------------------------------------
# Interface ligne de commande
# --------------------------------------------------------------------------

def _afficher_rapport(rapport: Dict[str, Any]) -> None:
    print("=" * 78)
    print("🔬 PRÉFLIGHT PDF RÉEL — CONTRÔLE DE CONFORMITÉ AMAZON KDP")
    print("=" * 78)
    print(f"Moteur : {rapport['moteur']}   |   Généré le : {rapport['genere_le']}")
    print(f"Pages intérieur de référence : {rapport['pages_interieur_reference']}")
    print("-" * 78)

    for cle, libelle in (("interieurs", "INTÉRIEURS 6x9"), ("couvertures", "COUVERTURES")):
        elements = rapport.get(cle) or []
        print(f"\n{libelle}  ({len(elements)} fichier(s))")
        if not elements:
            print("  — aucun fichier PDF trouvé —")
            continue
        for r in elements:
            symbole = {"CONFORME": "✅", "ANOMALIE": "⚠️ ", "ERREUR": "❌"}.get(
                r["statut"], "•"
            )
            dims = (
                f"{r['largeur_po']:.3f} x {r['hauteur_po']:.3f} po"
                if r["largeur_po"]
                else "n/d"
            )
            print(f"  {symbole} {Path(r['fichier']).name}")
            print(f"      pages={r['pages']}  dims={dims}  "
                  f"blanches={len(r['pages_blanches'])}  "
                  f"polices non incorporées={len(r['polices_non_incorporees'])}")
            for anomalie in r["anomalies"]:
                print(f"      • {anomalie}")
            for avertissement in r["avertissements"]:
                print(f"      • {avertissement}")

    synthese = rapport["synthese"]
    print("\n" + "-" * 78)
    print(
        f"SYNTHÈSE : {synthese['conformes']}/{synthese['total']} PDF conformes | "
        f"{synthese['pages_blanches_total']} page(s) blanche(s) | "
        f"{synthese['polices_non_incorporees_total']} police(s) non incorporée(s)"
    )
    print("=" * 78)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Contrôle préflight réel des PDF KDP (pypdf / PyMuPDF)."
    )
    parser.add_argument("--interieurs", default=str(DOSSIERS_INTERIEURS),
                        help="Dossier des intérieurs (défaut : interieurs_finaux)")
    parser.add_argument("--couvertures", default=str(DOSSIERS_COUVERTURES),
                        help="Dossier des couvertures (défaut : couvertures_finales)")
    parser.add_argument("--rapport", default=str(RAPPORT_DEFAUT),
                        help="Fichier JSON de sortie (défaut : rapport_preflight_reel.json)")
    args = parser.parse_args(argv)

    rapport = inspecter_dossiers(
        dossier_interieurs=Path(args.interieurs),
        dossier_couvertures=Path(args.couvertures),
    )
    chemin_rapport = generer_rapport(rapport, args.rapport)
    _afficher_rapport(rapport)
    print(f"📄 Rapport JSON : {chemin_rapport}")

    return 0 if rapport["synthese"]["avec_anomalies"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
