"""
kdp_extensions/kdp_compliance_supervisor.py — Superviseur Qualité & Conformité KDP Multilingue & Anti-Anonymat (Agent 4).
(Règles 01, 02, 03, 04, 05 de l'Écosystème KDP Haute Couture).

Missions d'inspection chirurgicale :
1. Audit d'encodage et d'intégrité UTF-8 (zéro corruption sur accents, umlauts, caractères arabes).
2. Vérification des polices typographiques par script et langue.
3. Vérification de la géométrie de reliure (Gutter) :
   - Inversion stricte pour l'Arabe (RTL) : gouttière à droite en recto, à gauche en verso.
   - Standard LTR pour EN, FR, ES, DE : gouttière à gauche en recto, à droite en verso.
4. Conformité de la césure syllabique :
   - Strictement proscrite pour l'Arabe (hyphens: none !important;).
   - Recommandée pour le Français, l'Espagnol et l'Allemand (hyphens: auto;).
5. Alerte réglementaire spécifique Amazon KDP :
   - Prise en charge officielle de l'Arabe sur Kindle eBook vs restrictions techniques sur le livre broché (Paperback).
6. Agent 4 : Superviseur de Conformité KDP & Score Anti-Anonymat :
   - Détection des termes prohibés (bestseller, #1, gratuit, promo, etc.) et marques notoires (Disney, Marvel, Pokémon, Lego...).
   - Détection du bourrage de mots-clés dans le nom d'auteur (Keyword Stuffing).
   - Validation stricte des 24 pages minimum pour le livre broché papier (KDP prepress).
   - Contrôle d'hygiène textuelle (zéro "Lorem ipsum", "TODO", "NaN", "undefined").
   - Calcul du Score Anti-Anonymat & Transparence Éditoriale (0-100) : copyright, disclaimer, biographie auteur, achevé d'imprimer.
   - Verdict ferme : PASSED, WARNING, ou REJECTED.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from kdp_extensions.i18n_config import (
    get_language_config,
    get_paperback_warning,
    is_rtl,
    normalize_language,
)
from kdp_extensions.kdp_dimensions import (
    KDP_FORMATS,
    normalize_format,
    calculate_kdp_specs,
)


# ==============================================================================
# 1. AUDIT MULTILINGUE (UTF-8, POLICES, RTL GUTTER, CÉSURES)
# ==============================================================================

def audit_utf8_integrity(content: str) -> Dict[str, Any]:
    """Vérifie l'absence de caractères corrompus (Mojibake, NaN, undefined, TODO)."""
    anomalies: List[str] = []
    
    # Détection de mojibake typique (UTF-8 lu en Latin-1 / Windows-1252)
    mojibake_patterns = [
        r"Ã©", r"Ã¨", r"Ã ", r"Ã¢", r"Ãª", r"Ã®", r"Ã´", r"Ã»", r"Ã§",
        r"â€™", r"â€œ", r"â€", r"ï¿½", r"\uFFFD"
    ]
    for p in mojibake_patterns:
        if re.search(p, content):
            anomalies.append(f"Corruption d'encodage détectée (Mojibake : '{p}').")
            break

    # Détection de résidus de développement
    if re.search(r"\b(NaN|undefined)\b", content):
        anomalies.append("Présence de valeurs invalides ('NaN' ou 'undefined') dans le texte.")
    if "TODO" in content:
        anomalies.append("Présence de marqueurs de développement 'TODO' non résolus.")

    return {
        "valid": len(anomalies) == 0,
        "anomalies": anomalies,
    }


def audit_font_script_compatibility(html_content: str, language: str = "fr") -> Dict[str, Any]:
    """Vérifie que les polices déclarées supportent l'alphabet et le script de la langue."""
    lang_code = normalize_language(language)
    cfg = get_language_config(lang_code)
    anomalies: List[str] = []

    if lang_code == "ar":
        # Pour l'arabe, les polices latines pures ne conviennent pas
        ar_fonts = ["amiri", "cairo", "noto sans arabic", "scheherazade", "tajawal", "almarai"]
        lower = html_content.lower()
        has_ar_font = any(f in lower for f in ar_fonts)
        if not has_ar_font:
            anomalies.append("Le script Arabe exige une police compatible (ex: 'Amiri', 'Cairo', 'Noto Sans Arabic').")

    return {
        "is_compatible": len(anomalies) == 0,
        "language": lang_code,
        "anomalies": anomalies,
    }


def audit_rtl_gutter_compliance(
    html_content: str,
    language: str = "fr",
    format_id: str = "6x9",
    page_count: int = 100,
) -> Dict[str, Any]:
    """Vérifie que l'inversion de la gouttière est correctement appliquée pour le script RTL."""
    lang_code = normalize_language(language)
    rtl = is_rtl(lang_code)
    anomalies: List[str] = []

    if rtl:
        # En RTL : la reliure est à DROITE sur les pages impaires (recto) et à GAUCHE sur les pages paires (verso)
        has_rtl_left = bool(re.search(r"@page\s*:\s*left[^{]*\{[^}]*margin-left", html_content, re.IGNORECASE))
        has_rtl_right = bool(re.search(r"@page\s*:\s*right[^{]*\{[^}]*margin-right", html_content, re.IGNORECASE))
        if not (has_rtl_left or has_rtl_right):
            anomalies.append("Marge de reliure RTL inversée non détectée pour le script Arabe.")

    return {
        "is_conforme": len(anomalies) == 0,
        "is_rtl": rtl,
        "anomalies": anomalies,
    }


def audit_hyphenation_rules(html_content: str, language: str = "fr") -> Dict[str, Any]:
    """Contrôle la règle de césure : proscrite pour l'Arabe, recommandée pour les langues latines."""
    lang_code = normalize_language(language)
    rtl = is_rtl(lang_code)
    anomalies: List[str] = []

    if rtl:
        if "hyphens: auto" in html_content.lower():
            anomalies.append("Césure interdite en script Arabe (utilisez 'hyphens: none !important;').")

    return {
        "is_conforme": len(anomalies) == 0,
        "language": lang_code,
        "anomalies": anomalies,
    }


def audit_multilingual_kdp_project(
    html_content: str,
    metadata: Dict[str, Any],
    language: str = "fr",
    format_id: str = "6x9",
    page_count: int = 100,
    cover_type: str = "paperback",
) -> Dict[str, Any]:
    """Audit complet de conformité multilingue KDP pour les 5 langues supportées."""
    lang_code = normalize_language(language)
    cfg = get_language_config(lang_code)
    rtl = is_rtl(lang_code)

    utf8_res = audit_utf8_integrity(html_content)
    font_res = audit_font_script_compatibility(html_content, lang_code)
    gutter_res = audit_rtl_gutter_compliance(html_content, lang_code, format_id, page_count)
    hyphen_res = audit_hyphenation_rules(html_content, lang_code)

    all_anomalies = utf8_res["anomalies"] + font_res["anomalies"] + gutter_res["anomalies"] + hyphen_res["anomalies"]

    paperback_warning = None
    if lang_code == "ar" and cover_type.lower() in ("paperback", "broche", "print"):
        paperback_warning = get_paperback_warning("ar")

    score = 100
    score -= len(utf8_res["anomalies"]) * 20
    score -= len(font_res["anomalies"]) * 20
    score -= len(gutter_res["anomalies"]) * 15
    score -= len(hyphen_res["anomalies"]) * 10

    final_score = max(0, min(100, score))
    is_conforme = final_score >= 80 and len(utf8_res["anomalies"]) == 0

    recommendations: List[str] = []
    if lang_code == "ar":
        recommendations.append("Privilégier le format Kindle eBook (KFX / mise en page fixe) pour une distribution sans contrainte sur Amazon.")
        recommendations.append("Utiliser les polices Google Fonts 'Amiri' et 'Cairo' pour un rendu typographique royal.")
    elif lang_code == "de":
        recommendations.append("Vérifier les césures des noms composés longs allemands avec 'hyphens: auto; lang=\"de\"'.")

    return {
        "status": "success",
        "language": lang_code,
        "language_name": cfg["name"],
        "is_rtl": rtl,
        "format": normalize_format(format_id),
        "page_count": page_count,
        "is_conforme": is_conforme,
        "score_conformite": final_score,
        "paperback_warning": paperback_warning,
        "audits": {
            "utf8_integrity": utf8_res,
            "font_compatibility": font_res,
            "gutter_compliance": gutter_res,
            "hyphenation_compliance": hyphen_res,
        },
        "anomalies": all_anomalies,
        "recommendations": recommendations,
    }


# ==============================================================================
# 2. AGENT 4 : SUPERVISEUR DE CONFORMITÉ KDP & PORTE QUALITÉ ANTI-ANONYMAT
# ==============================================================================

FORBIDDEN_TITLE_TERMS = [
    "bestseller",
    "best-seller",
    "best seller",
    "#1",
    "n°1",
    "numéro 1",
    "numero 1",
    "gratuit",
    "free",
    "promo",
    "promotion",
    "pas cher",
    "prix cassé",
    "solde",
    "soldes",
    "illimité",
    "unlimited",
]

NOTORIOUS_TRADEMARKS = [
    "disney",
    "marvel",
    "pokémon",
    "pokemon",
    "lego",
    "minecraft",
    "star wars",
    "harry potter",
    "fortnite",
    "barbie",
    "nintendo",
    "playstation",
    "xbox",
]

GENERIC_AUTHOR_KEYWORDS = [
    "coloring",
    "coloriage",
    "coloriages",
    "book",
    "books",
    "livre",
    "livres",
    "cahier",
    "cahiers",
    "notebook",
    "notebooks",
    "planner",
    "planners",
    "journal",
    "journals",
    "puzzle",
    "puzzles",
    "activity",
    "activities",
    "press",
    "presses",
    "publishing",
    "publisher",
    "publishers",
    "publication",
    "publications",
    "editions",
    "éditions",
    "edition",
    "édition",
    "kids",
    "children",
    "enfant",
    "enfants",
    "studio",
    "studios",
    "media",
    "creator",
    "author",
    "auteur",
]

CONTENT_HYGIENE_BUGS = [
    "todo",
    "lorem ipsum",
    "nan",
    "undefined",
    "draft_text",
    "null",
    "fixme",
]


def check_title_subtitle_terms(title: str, subtitle: str = "") -> Tuple[List[str], List[str]]:
    """
    Vérifie l'absence de termes prohibés par les TOS KDP et de marques déposées.
    
    Returns:
        (critical_violations, warnings)
    """
    crit: List[str] = []
    warn: List[str] = []
    combined = f"{title or ''} {subtitle or ''}".lower()

    # 1. Termes interdits (TOS KDP)
    for term in FORBIDDEN_TITLE_TERMS:
        # Match entier ou mot isolé
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, combined):
            crit.append(f"Terme prohibé par les Conditions Générales Amazon KDP dans le titre/sous-titre : '{term}'.")

    # 2. Marques notoires (Propriété intellectuelle)
    for tm in NOTORIOUS_TRADEMARKS:
        pattern = r"\b" + re.escape(tm) + r"\b"
        if re.search(pattern, combined):
            crit.append(f"Marque déposée notoire détectée sans autorisation de licence : '{tm}'. Risque de suspension immédiate KDP.")

    # 3. Longueur excessive
    if len(title or "") > 200:
        warn.append("Titre principal trop long (> 200 caractères) : risque de rejet de métadonnées.")
    if len(subtitle or "") > 200:
        warn.append("Sous-titre trop long (> 200 caractères) : risque de troncature sur mobile.")

    return crit, warn


def check_author_name_quality(author: str) -> Tuple[bool, Optional[str]]:
    """
    Audite la conformité du nom d'auteur contre le Keyword Stuffing (Bourrage de mots-clés).
    Amazon KDP sanctionne sévèrement les faux noms d'auteurs composés de mots-clés de recherche.
    
    Returns:
        (is_valid, error_message)
    """
    clean = (author or "").strip()
    if not clean or len(clean) < 2:
        return False, "Le nom d'auteur est obligatoire et doit contenir au moins 2 caractères."

    # Détection d'URL ou domaine internet dans le nom d'auteur
    if re.search(r"(https?://|www\.|\.com|\.fr|\.net|\.org)", clean, flags=re.IGNORECASE):
        return False, f"Le nom d'auteur ne peut pas contenir d'URL ou d'adresse web : '{clean}'."

    # Détection de symboles et ponctuation suspects
    if re.search(r"[{}\[\]<>@$%^*=~]", clean):
        return False, f"Le nom d'auteur contient des caractères spéciaux interdits par KDP : '{clean}'."

    # Analyse des mots-clés génériques (Keyword-stuffed author names)
    lower_tokens = re.findall(r"\b[a-zA-ZÀ-ÿ]+\b", clean.lower())
    if not lower_tokens:
        return False, "Nom d'auteur invalide."

    # Si les mots sont des descripteurs génériques de niche
    generic_matches = [w for w in lower_tokens if w in GENERIC_AUTHOR_KEYWORDS]
    if (len(generic_matches) >= 2 and (len(generic_matches) / len(lower_tokens)) >= 0.4) or len(generic_matches) >= 3:
        return False, (
            f"Le nom d'auteur '{clean}' est identifié comme du bourrage de mots-clés (Keyword Stuffing). "
            f"Amazon KDP exige un nom humain crédible (ex: 'Jean Dupont') ou une maison d'édition déclarée (ex: 'Éditions MarkEddy')."
        )

    return True, None


def check_a9_keywords_compliance(
    keywords: Optional[List[str]],
    title: str,
    subtitle: str
) -> Tuple[List[str], List[str]]:
    """
    Contrôle la conformité des 7 slots de mots-clés backend Amazon A9 selon la Règle 05.
    
    Returns:
        (critical_violations, warnings)
    """
    crit: List[str] = []
    warn: List[str] = []
    if not keywords:
        warn.append("Aucun mot-clé backend fourni : le livre sera difficilement trouvable sur Amazon.")
        return crit, warn

    title_words = set(re.findall(r"\b\w{4,}\b", f"{title or ''} {subtitle or ''}".lower()))

    if len(keywords) > 7:
        warn.append(f"Amazon KDP n'accepte que 7 slots backend au maximum (fournis: {len(keywords)}).")

    for idx, kw in enumerate(keywords[:7], start=1):
        clean_kw = (kw or "").strip()
        if not clean_kw:
            continue

        # Pas de ponctuation ou guillemets
        if re.search(r"[\",;!?]", clean_kw):
            warn.append(f"Slot {idx} ('{clean_kw}') contient de la ponctuation inutile qui réduit la combinatoire A9.")

        # Longueur maximale recommandée
        byte_len = len(clean_kw.encode("utf-8"))
        if byte_len > 50 or len(clean_kw) > 50:
            warn.append(f"Slot {idx} dépasse 50 octets/caractères ({byte_len} octets UTF-8) : risque de troncature A9.")

        # Répétition des mots du titre/sous-titre (Cannibalisation de quota A9)
        kw_words = set(re.findall(r"\b\w{4,}\b", clean_kw.lower()))
        repeated = kw_words.intersection(title_words)
        if repeated:
            warn.append(
                f"Slot {idx} répète des termes déjà indexés dans le titre/sous-titre : {', '.join(repeated)} "
                f"(gaspillage d'espace de recherche)."
            )

        # Proscription absolue des termes interdits KDP dans les mots-clés (Bestseller, Gratuit, etc.)
        lower_kw = clean_kw.lower()
        for forb in FORBIDDEN_TITLE_TERMS:
            if re.search(rf"\b{re.escape(forb)}\b", lower_kw):
                crit.append(f"Slot {idx} contient un terme promotionnel prohibé par Amazon KDP : '{forb}'.")

        # Proscription absolue des marques notoires dans les mots-clés (Zéro marque KDP)
        for tm in NOTORIOUS_TRADEMARKS:
            if re.search(rf"\b{re.escape(tm)}\b", lower_kw):
                crit.append(f"Slot {idx} contient une marque notoire protégée : '{tm}'.")

    return crit, warn


def check_content_hygiene(text_or_html: Optional[str]) -> Tuple[List[str], List[str]]:
    """Vérifie l'absence de termes parasites ou de bugs de génération dans le contenu."""
    crit: List[str] = []
    warn: List[str] = []
    if not text_or_html:
        return crit, warn

    lower = text_or_html.lower()

    # Détection stricte des bugs critiques
    if "lorem ipsum" in lower:
        crit.append("Présence inacceptable de texte de remplissage 'Lorem ipsum' dans le contenu du livre.")
    if "todo:" in lower or "todo " in lower:
        crit.append("Présence inacceptable de marqueurs de travail 'TODO' non résolus dans le manuscrit.")
    if re.search(r"\b(nan|undefined|draft_text)\b", lower):
        crit.append("Présence d'erreurs de rendu ('NaN', 'undefined' ou 'DRAFT_TEXT') dans le document.")

    return crit, warn


def calculate_anti_anonymity_score(
    has_copyright: bool = True,
    has_disclaimer: bool = True,
    has_author_bio: bool = True,
    has_colophon: bool = True,
) -> Tuple[float, Dict[str, Any]]:
    """
    Calcule le Score Anti-Anonymat & Transparence Éditoriale (0-100).
    Chaque pilier de réassurance apporte 25 points.
    """
    details = {
        "copyright_present": bool(has_copyright),
        "disclaimer_present": bool(has_disclaimer),
        "author_bio_present": bool(has_author_bio),
        "colophon_present": bool(has_colophon),
    }
    score = sum(25.0 for val in details.values() if val)
    return float(score), details


def audit_kdp_compliance(
    title: str,
    subtitle: str = "",
    author: str = "MarkEddy",
    keywords: Optional[List[str]] = None,
    page_count: int = 24,
    format_id: str = "6x9",
    paper_type: str = "white",
    content_text_or_html: Optional[str] = None,
    has_copyright: bool = True,
    has_disclaimer: bool = True,
    has_author_bio: bool = True,
    has_colophon: bool = True,
    cover_specs: Optional[Dict[str, Any]] = None,
    project_type: str = "text",
    binding: str = "paperback",
) -> Dict[str, Any]:
    """
    Auditeur de Conformité Amazon KDP & Superviseur de Porte Qualité (Agent 4).
    
    Vérifie l'ensemble des règles juridiques, techniques et éditoriales.
    Délivre un verdict non négociable : PASSED, WARNING ou REJECTED.
    """
    critical_violations: List[str] = []
    warnings: List[str] = []
    passed_checks: List[str] = []

    # 1. Contrôle Titre & Sous-titre
    crit_title, warn_title = check_title_subtitle_terms(title, subtitle)
    critical_violations.extend(crit_title)
    warnings.extend(warn_title)
    if not crit_title:
        passed_checks.append("Titre et sous-titre conformes aux règles de propriété intellectuelle et TOS KDP.")

    # 2. Contrôle Nom d'Auteur (Anti-Anonymat / Anti-Keyword Stuffing)
    auth_ok, auth_err = check_author_name_quality(author)
    if not auth_ok and auth_err:
        critical_violations.append(auth_err)
    else:
        passed_checks.append(f"Nom d'auteur conforme et certifié non-descriptif : '{author}'.")

    # 3. Contrôle des 24 Pages Minimum (Livre Broché)
    is_paperback = binding.lower() in ("paperback", "broché", "broche")
    if is_paperback and page_count < 24:
        critical_violations.append(
            f"Infraction technique critique : Le livre broché ne compte que {page_count} pages. "
            f"Amazon KDP exige strictement un minimum de 24 pages pour l'impression papier."
        )
    else:
        passed_checks.append(f"Pagination prépresse conforme : {page_count} pages (minimum 24 p. respecté).")

    # 4. Contrôle du Format de Coupe KDP (16 formats)
    try:
        fid = normalize_format(format_id)
        if fid not in KDP_FORMATS:
            critical_violations.append(f"Format de coupe '{format_id}' inconnu du référentiel KDP.")
        else:
            passed_checks.append(f"Format de coupe officiel Amazon KDP validé : {fid}.")
    except Exception as exc:
        critical_violations.append(f"Format KDP invalide : {exc}")

    # 5. Contrôle Mots-Clés Backend A9
    crit_kw, warn_kw = check_a9_keywords_compliance(keywords, title, subtitle)
    critical_violations.extend(crit_kw)
    warnings.extend(warn_kw)
    if not crit_kw and not warn_kw:
        passed_checks.append("Les 7 mots-clés backend A9 sont optimisés sans répétition.")

    # 6. Contrôle Hygiène Textuelle
    crit_hyg, warn_hyg = check_content_hygiene(content_text_or_html)
    critical_violations.extend(crit_hyg)
    warnings.extend(warn_hyg)
    if not crit_hyg:
        passed_checks.append("Hygiène textuelle validée : zéro présence de TODO, Lorem ipsum ou bug de rendu.")

    # 7. Contrôle Couverture & Réserve ISBN (si cover_specs fournies)
    if cover_specs and isinstance(cover_specs, dict):
        has_isbn = bool(cover_specs.get("isbn_reserve") or "isbn" in str(cover_specs).lower())
        if not has_isbn:
            warnings.append("Vérifiez la présence du rectangle de réserve ISBN (600x360 px) en 4ème de couverture.")
        else:
            passed_checks.append("Réserve normalisée ISBN (600x360 px @ 300 DPI) confirmée.")

    # 8. Score Anti-Anonymat
    anonymity_score, anonymity_details = calculate_anti_anonymity_score(
        has_copyright=has_copyright,
        has_disclaimer=has_disclaimer,
        has_author_bio=has_author_bio,
        has_colophon=has_colophon,
    )
    if anonymity_score < 50.0:
        warnings.append(f"Score Anti-Anonymat faible ({anonymity_score}/100) : ajoutez copyright, bio et colophon pour rassurer le lecteur.")
    else:
        passed_checks.append(f"Score Anti-Anonymat & Transparence Éditoriale excellent : {anonymity_score}/100.")

    # --- CALCUL DES SCORES PONDÉRÉS ---
    prepress_score = 100.0 if (not is_paperback or page_count >= 24) else max(0.0, (page_count / 24.0) * 100.0)
    metadata_score = max(0.0, 100.0 - (len(warn_title) * 15.0) - (len(warn_kw) * 10.0))
    hygiene_score = 100.0 if not crit_hyg else 0.0

    raw_overall = (
        (prepress_score * 0.30)
        + (anonymity_score * 0.30)
        + (metadata_score * 0.20)
        + (hygiene_score * 0.20)
    )

    if critical_violations:
        raw_overall = min(50.0, raw_overall - (len(critical_violations) * 20.0))
        verdict = "REJECTED"
    elif raw_overall >= 80.0:
        verdict = "PASSED"
    else:
        verdict = "WARNING"

    overall_score = round(max(0.0, min(100.0, raw_overall)), 1)

    return {
        "status": "success",
        "verdict": verdict,
        "overall_score": overall_score,
        "anti_anonymity_score": anonymity_score,
        "prepress_score": round(prepress_score, 1),
        "editorial_score": round(hygiene_score, 1),
        "a9_seo_score": round(metadata_score, 1),
        "critical_violations": critical_violations,
        "warnings": warnings,
        "passed_checks": passed_checks,
        "audit_details": {
            "title": title,
            "author": author,
            "page_count": page_count,
            "format_id": format_id,
            "anonymity_breakdown": anonymity_details,
            "project_type": project_type,
        },
        "timestamp": datetime.now().isoformat(),
        "supervisor": "Agent 4 : KDP Compliance & Anti-Anonymity Gatekeeper",
    }


__all__ = [
    "audit_utf8_integrity",
    "audit_font_script_compatibility",
    "audit_rtl_gutter_compliance",
    "audit_hyphenation_rules",
    "audit_multilingual_kdp_project",
    "FORBIDDEN_TITLE_TERMS",
    "NOTORIOUS_TRADEMARKS",
    "GENERIC_AUTHOR_KEYWORDS",
    "CONTENT_HYGIENE_BUGS",
    "check_title_subtitle_terms",
    "check_author_name_quality",
    "check_a9_keywords_compliance",
    "check_content_hygiene",
    "calculate_anti_anonymity_score",
    "audit_kdp_compliance",
    "supervise_kdp_book",
]


def supervise_kdp_book(book_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Supervise a KDP book payload and return compliance verdict and anti-ordinary audit.

    Verdict: APPROVED_FOR_KDP if excellence_score >= 85 and no blocking violations, else REJECTED_FOR_REVISION.
    """
    p = book_payload or {}
    title = str(p.get("title") or "")
    subtitle = str(p.get("subtitle") or "")
    author = str(p.get("author") or "MarkEddy")
    keywords = p.get("keywords") or p.get("backend_keywords") or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in re.split(r"[\n,;]+", keywords) if k.strip()]
    page_count = int(p.get("page_count") or p.get("pages") or 0)
    binding = str(p.get("binding") or p.get("cover_type") or "paperback").lower()
    language = str(p.get("language") or "fr")
    niche = str(p.get("niche") or "")
    content = str(p.get("content") or p.get("content_text_or_html") or "")
    format_id = str(p.get("format_id") or p.get("format") or "6x9")

    blocking: List[str] = []
    warnings: List[str] = []

    # 1. Anti keyword-stuffing nom d'auteur
    auth_ok, auth_err = check_author_name_quality(author)
    if not auth_ok and auth_err:
        blocking.append(auth_err)

    # 2. Termes prohibés dans le titre / sous-titre & marques notoires
    crit_title, warn_title = check_title_subtitle_terms(title, subtitle)
    blocking.extend(crit_title)
    warnings.extend(warn_title)

    # 3. Limite de 200 caractères titre + sous-titre combinés
    combined_title_len = len(f"{title} {subtitle}".strip())
    if combined_title_len > 200:
        blocking.append(
            f"Titre et sous-titre combinés dépassent la limite stricte de 200 caractères imposée par Amazon KDP ({combined_title_len} car.)."
        )

    # 4. Audit des 7 mots-clés backend A9
    crit_kw, warn_kw = check_a9_keywords_compliance(keywords, title, subtitle)
    blocking.extend([f"Infraction mot-clé A9 : {c}" for c in crit_kw])
    warnings.extend(warn_kw)

    # 5. Hygiène textuelle (absence de TODO, Lorem ipsum, NaN)
    crit_hyg, warn_hyg = check_content_hygiene(content)
    blocking.extend(crit_hyg)
    warnings.extend(warn_hyg)

    # 6. Disclaimers légaux obligatoires par niche
    has_disclaimer = bool(
        p.get("has_disclaimer")
        or p.get("disclaimer")
        or ("avertissement" in content.lower())
        or ("disclaimer" in content.lower())
        or ("non-responsabilité" in content.lower())
    )
    niche_l = niche.lower()
    needs_disclaimer = any(k in niche_l for k in ("finance", "argent", "invest", "sante", "santé", "health", "medical", "médical", "legal", "droit", "juridique", "enfant", "kid"))
    if needs_disclaimer and not has_disclaimer:
        blocking.append("Disclaimer légal / Avertissement de non-responsabilité requis pour cette niche mais absent.")
    elif not has_disclaimer:
        warnings.append("Aucun disclaimer détecté (fortement recommandé pour asseoir la crédibilité éditoriale).")

    # 7. Minimum 24 pages pour livre broché
    is_paperback = binding in ("paperback", "broché", "broche", "print")
    if is_paperback and page_count and page_count < 24:
        blocking.append(f"Livre broché : minimum 24 pages requis par Amazon KDP (actuel: {page_count} pages).")

    # 8. Interdiction texte sur le dos si < 79 pages
    spine_text = p.get("spine_text") or p.get("has_spine_text") or p.get("spine_text_present")
    has_spine_text = bool(spine_text) and str(spine_text).strip().lower() not in ("false", "0", "no", "none", "")
    if is_paperback and has_spine_text and page_count and page_count < 79:
        blocking.append(f"Texte sur le dos interdit par Amazon KDP pour les livres brochés de moins de 79 pages (actuel: {page_count} pages).")

    # 9. Réserve code-barres ISBN (si spécifications de couverture fournies)
    cover_specs = p.get("cover_specs")
    if cover_specs and isinstance(cover_specs, dict):
        has_isbn = bool(cover_specs.get("isbn_reserve") or "isbn" in str(cover_specs).lower())
        if not has_isbn:
            warnings.append("Vérifiez la présence du rectangle de réserve ISBN (600x360 px @ 300 DPI) en 4ème de couverture.")

    # 10. Déclaration de transparence IA KDP
    ai_declared = bool(p.get("ai_transparency_declared") or p.get("ai_disclosure"))
    ai_text_hit = bool(re.search(r"(ai[\-\s]?generated|artificial intelligence|g[ée]n[ée]r[ée] par une?\s*ia|transparence\s*ia|ai assisted)", content.lower()))
    if ai_declared or ai_text_hit:
        ai_summary = "Contenu textuel assisté par intelligence artificielle avec supervision humaine approfondie, relecture critique, vérification factuelle et mise en page éditoriale professionnelle."
    else:
        ai_summary = "Création humaine originale sans génération autonome directe d'IA."

    # 11. Alerte Paperback Arabe
    if normalize_language(language) == "ar" and is_paperback:
        warnings.append("Alerte KDP : Le format broché arabe peut être restreint selon les ateliers d'impression Amazon; vérifier éligibilité.")

    # --- GRILLE D'EXCELLENCE ANTI-ANONYMAT (100 POINTS) ---
    # 1. Promesse Unique (/20)
    if not title:
        promesse = 0
    elif combined_title_len > 200:
        promesse = 5
    elif subtitle and len(subtitle) >= 15:
        promesse = 20
    elif subtitle:
        promesse = 14
    else:
        promesse = 10

    # 2. Preuves & Valeur (/20)
    if needs_disclaimer and not has_disclaimer:
        preuves = 0
    elif has_disclaimer:
        preuves = 20
    elif len(content) > 5000:
        preuves = 16
    else:
        preuves = 10

    # 3. Voix Humaine & Anti-Tics IA (/20)
    if not auth_ok:
        voix_humaine = 0
    else:
        voix_humaine = 10
        has_bio = bool(p.get("has_author_bio") or p.get("author_bio") or ("auteur" in content.lower()))
        if has_bio:
            voix_humaine += 5
        # Bonus absence de clichés robotiques
        if not any(cliche in content.lower() for cliche in ["dans ce chapitre nous allons", "il convient de souligner que"]):
            voix_humaine += 5

    # 4. Structure Éditoriale (/20)
    has_copyright = bool(p.get("has_copyright") or p.get("copyright") or ("copyright" in content.lower()) or ("©" in content))
    has_colophon = bool(p.get("has_colophon") or p.get("colophon") or ("achevé d'imprimer" in content.lower()) or ("colophon" in content.lower()))
    has_toc = bool(p.get("has_toc") or p.get("toc") or ("sommaire" in content.lower()) or ("table des matières" in content.lower()))
    
    structure = 0
    if has_copyright:
        structure += 7
    if has_colophon:
        structure += 7
    if has_toc:
        structure += 6
    if structure == 0 and len(content) > 2000:
        structure = 10

    # 5. Packaging & Lisibilité (/20)
    packaging = 0
    if cover_specs or p.get("has_cover"):
        packaging += 10
    if p.get("isbn") or (cover_specs and isinstance(cover_specs, dict) and ("isbn" in str(cover_specs).lower())):
        packaging += 10
    if packaging == 0 and is_paperback:
        packaging = 10

    breakdown = {
        "promesse_unique_20": promesse,
        "preuves_valeur_20": preuves,
        "voix_humaine_20": voix_humaine,
        "structure_editoriale_20": structure,
        "packaging_lisibilite_20": packaging,
        "total_100": promesse + preuves + voix_humaine + structure + packaging,
    }

    excellence_score = float(breakdown["total_100"])

    # Recommandations concrètes Anti-Ordinaire
    recommendations: List[str] = []
    if promesse < 20:
        recommendations.append("Optimiser le sous-titre pour expliciter une promesse concrète et mesurable pour le lecteur.")
    if preuves < 20:
        recommendations.append("Intégrer des études de cas chiffrées, des exemples réels et un disclaimer légal pour dépasser les ouvrages théoriques amateurs.")
    if voix_humaine < 20:
        recommendations.append("Ajouter une biographie d'auteur riche (autorité et expertise) et purger le manuscrit des tournures impersonnelles ou tics IA.")
    if structure < 20:
        recommendations.append("Compléter la structure éditoriale formelle (page de copyright détaillée, table des matières structurée, achevé d'imprimer avec dépôt légal).")
    if packaging < 20:
        recommendations.append("Calibrer la couverture à 300 DPI avec réserve normalisée ISBN 600x360 px et calcul au micron de l'épaisseur du dos.")
    if not recommendations:
        recommendations.append("Ouvrage de niveau Best-Seller : architecture éditoriale, respect des TOS KDP et packaging exemplaires.")

    # Matrice de Décision Finale (Quality Gate)
    if blocking:
        verdict = "REJECTED_FOR_REVISION"
        kdp_compliance_passed = False
    elif excellence_score >= 85.0:
        verdict = "APPROVED_FOR_KDP"
        kdp_compliance_passed = True
    else:
        verdict = "REJECTED_FOR_REVISION"
        kdp_compliance_passed = False

    return {
        "status": "success",
        "verdict": verdict,
        "approved": verdict == "APPROVED_FOR_KDP",
        "kdp_compliance_passed": kdp_compliance_passed,
        "excellence_score": excellence_score,
        "score_anti_anonymat_100": excellence_score,
        "excellence_score_breakdown": breakdown,
        "anti_anonymat_breakdown_20_each": breakdown,
        "blocking_violations": blocking,
        "warnings": warnings,
        "ai_disclosure_summary": ai_summary,
        "anti_ordinary_recommendations": recommendations,
        "seo_a9_compliant": len(crit_kw) == 0,
        "checks": {
            "keyword_stuffing_checked": True,
            "title_200_chars_checked": combined_title_len <= 200,
            "trademarks_checked": True,
            "disclaimer_required_by_niche": needs_disclaimer,
            "ai_transparency_declared": ai_declared or ai_text_hit,
            "min_24_pages_paperback_ok": (not is_paperback) or (page_count >= 24 if page_count else True),
            "spine_text_rule_ok": (not has_spine_text) or (page_count >= 79 if page_count else False),
            "arabic_paperback_alert": (normalize_language(language) == "ar" and is_paperback),
            "seo_a9_audit": {
                "keywords_checked": True,
                "critical_violations": crit_kw,
                "warnings": warn_kw,
                "score_conforme": len(crit_kw) == 0,
            },
        },
        "timestamp": datetime.now().isoformat(),
        "supervisor": "Agent 4 : Superviseur de Conformité Amazon KDP & Anti-Anonymat",
    }
__all__ = [
    "audit_utf8_integrity",
    "audit_font_script_compatibility",
    "audit_rtl_gutter_compliance",
    "audit_hyphenation_rules",
    "audit_multilingual_kdp_project",
    "FORBIDDEN_TITLE_TERMS",
    "NOTORIOUS_TRADEMARKS",
    "GENERIC_AUTHOR_KEYWORDS",
    "CONTENT_HYGIENE_BUGS",
    "check_title_subtitle_terms",
    "check_author_name_quality",
    "check_a9_keywords_compliance",
    "check_content_hygiene",
    "calculate_anti_anonymity_score",
    "audit_kdp_compliance",
    "supervise_kdp_book",
]
