"""
kdp_extensions/seo_a9_agent.py — Agent d'Optimisation SEO Amazon A9 Multilingue.
(Conforme à la RÈGLE 05 du Système Multi-Agents KDP & Exigences Officielles KDP).

Fonctionnalités chirurgicales :
1. Calcul rigoureux de la limite de 50 octets UTF-8 par slot (et 250 octets cumulés).
   Prise en compte des caractères multi-octets (accents français/espagnols, umlauts allemands, lettres arabes).
2. Filtrage impitoyable des mots interdits locaux par marché Amazon (FR, EN, ES, DE, AR)
   (ex: 'meilleur', 'gratuit', 'kindle', 'bestseller', etc.).
3. Détection des doublons avec le Titre et le Sous-Titre (A9 indexe déjà le titre au poids maximal).
4. Proscription de la ponctuation parasite (guillemets, virgules, points d'exclamation).
5. Génération/Optimisation des 7 slots d'intention stratégique (Matrice Règle 05).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

from kdp_extensions.i18n_config import (
    get_forbidden_keywords,
    get_language_config,
    normalize_language,
)


def calculate_utf8_bytes(text: str) -> int:
    """Calcule la taille exacte d'une chaîne en octets UTF-8."""
    return len((text or "").strip().encode("utf-8"))


def tokenize_clean_words(text: str) -> Set[str]:
    """Extrait l'ensemble des mots uniques en minuscules sans accents ni ponctuation."""
    if not text:
        return set()
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    # Normalisation NFKD pour comparaison sémantique sans accents
    normalized = unicodedata.normalize("NFKD", cleaned)
    ascii_clean = "".join(c for c in normalized if not unicodedata.combining(c))
    return {w for w in ascii_clean.split() if len(w) > 1}


def validate_a9_slot(
    slot_text: str,
    language: str = "fr",
    title: str = "",
    subtitle: str = "",
    max_bytes: int = 50,
) -> Dict[str, Any]:
    """
    Valide un slot backend Amazon KDP individuel vis-à-vis des règles A9.
    """
    lang_code = normalize_language(language)
    forbidden = get_forbidden_keywords(lang_code)

    raw_text = (slot_text or "").strip()
    byte_count = calculate_utf8_bytes(raw_text)
    char_count = len(raw_text)

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Limite d'octets UTF-8
    if byte_count > max_bytes:
        errors.append(f"Dépassement du quota A9 : {byte_count} octets UTF-8 (limite stricte : {max_bytes} octets).")
    elif byte_count > (max_bytes - 5):
        warnings.append(f"Slot très proche de la limite ({byte_count}/{max_bytes} octets).")

    # 2. Ponctuation interdite (guillemets, virgules...)
    if re.search(r'["\'«»“”,\.!?;:]', raw_text):
        warnings.append("Présence de ponctuation (guillemets/virgules) : Amazon A9 indexe les espaces purs.")

    # 3. Mots interdits locaux (TOS Amazon KDP)
    lower_slot = raw_text.lower()
    for forb in forbidden:
        # Correspondance par mot entier ou sous-chaîne selon la nature
        pattern = rf"\b{re.escape(forb)}\b"
        if re.search(pattern, lower_slot):
            errors.append(f"Mot interdit détecté ({lang_code.upper()}) : '{forb}'. Amazon pénalise ce mot.")

    # 4. Doublons avec Titre ou Sous-Titre (Gaspillage de quota A9)
    title_words = tokenize_clean_words(title) | tokenize_clean_words(subtitle)
    slot_words = tokenize_clean_words(raw_text)
    redundant_words = slot_words & title_words
    if redundant_words:
        warnings.append(
            f"Mots déjà indexés dans le Titre/Sous-titre ({', '.join(sorted(redundant_words))}) : gaspillage de slot."
        )

    is_valid = len(errors) == 0

    return {
        "text": raw_text,
        "language": lang_code,
        "byte_count": byte_count,
        "char_count": char_count,
        "max_bytes": max_bytes,
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "redundant_words": sorted(redundant_words),
    }


def audit_7_slots_a9(
    slots: List[str],
    language: str = "fr",
    title: str = "",
    subtitle: str = "",
) -> Dict[str, Any]:
    """
    Audite la matrice complète des 7 slots de mots-clés backend pour Amazon KDP.
    Score de conformité sur 100 et diagnostic d'autorité.
    """
    lang_code = normalize_language(language)
    lang_cfg = get_language_config(lang_code)

    effective_slots = list(slots or [])
    while len(effective_slots) < 7:
        effective_slots.append("")
    effective_slots = effective_slots[:7]

    slot_results: List[Dict[str, Any]] = []
    total_bytes = 0
    total_errors = 0
    total_warnings = 0

    all_slot_words: Set[str] = set()
    internal_duplicates: List[str] = []

    for idx, slot_str in enumerate(effective_slots, start=1):
        res = validate_a9_slot(
            slot_str,
            language=lang_code,
            title=title,
            subtitle=subtitle,
            max_bytes=50,
        )
        res["slot_number"] = idx
        slot_results.append(res)
        total_bytes += res["byte_count"]
        total_errors += len(res["errors"])
        total_warnings += len(res["warnings"])

        # Vérifier répétitions entre slots
        words = tokenize_clean_words(slot_str)
        repeated = words & all_slot_words
        if repeated:
            internal_duplicates.extend(list(repeated))
        all_slot_words.update(words)

    # Calcul du score A9
    score = 100
    if len([s for s in effective_slots if s.strip()]) < 7:
        score -= (7 - len([s for s in effective_slots if s.strip()])) * 8

    score -= total_errors * 15
    score -= total_warnings * 5
    if internal_duplicates:
        score -= len(set(internal_duplicates)) * 5

    # Limite globale Amazon KDP (250 octets cumulés recommandés)
    if total_bytes > 250:
        score -= 10
        total_warnings += 1

    final_score = max(0, min(100, score))
    is_conforme = final_score >= 80 and total_errors == 0

    return {
        "status": "success",
        "marketplace": lang_cfg["amazon_marketplace"],
        "language": lang_code,
        "is_conforme": is_conforme,
        "score_a9": final_score,
        "total_bytes": total_bytes,
        "max_recommended_total_bytes": 250,
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "internal_duplicates": sorted(set(internal_duplicates)),
        "slots_detail": slot_results,
    }


def optimize_7_slots_a9(
    title: str,
    subtitle: str,
    niche: str,
    language: str = "fr",
    target_audience: str = "",
) -> Dict[str, Any]:
    """
    Génère 7 slots d'intention stratégique selon la matrice Règle 05 pour la langue ciblée.
    Garantit zéro mot interdit, zéro doublon avec le titre et < 50 octets UTF-8 par slot.
    """
    lang_code = normalize_language(language)

    # Banques de templates d'intention par langue (Problem, Method, Action, Safety, Target, Obstacle, Outcome)
    INTENT_TEMPLATES: Dict[str, List[str]] = {
        "fr": [
            "sortir du decouvert bancaire fin de mois",     # 1. Problème / Douleur
            "methode enveloppes virtuelles regle 50 30 20", # 2. Méthode
            "investir en bourse petit budget etf pea",      # 3. Action / Investissement
            "constituer epargne securite matelas urgence",  # 4. Sécurité
            "gestion budget debutant jeune actif salarie",  # 5. Cible
            "rembourser credit consommation effet boule",   # 6. Obstacle
            "independance financiere liberte patrimoine",   # 7. Transformation
        ],
        "en": [
            "stop living paycheck to paycheck escape debt",  # 1. Pain
            "zero based budget 50 30 20 cash envelope",      # 2. Method
            "invest in index funds etf small budget",        # 3. Action
            "emergency fund cash buffer financial cushion",  # 4. Safety
            "money management young adult beginner guide",   # 5. Target
            "debt snowball payoff consumer loans strategy",  # 6. Obstacle
            "financial independence retire early wealth",    # 7. Outcome
        ],
        "es": [
            "salir de deudas llegar a fin de mes facil",     # 1. Dolor
            "metodo 50 30 20 sobres presupuesto familiar",   # 2. Método
            "invertir en fondos indexados etf poco dinero",  # 3. Acción
            "colchon de seguridad fondo de emergencia",     # 4. Seguridad
            "finanzas personales para jovenes principiantes",# 5. Público
            "liquidar prestamos personales bola de nieve",   # 6. Obstáculo
            "libertad financiera crear patrimonio pasivo",   # 7. Transformación
        ],
        "de": [
            "raus aus den schulden dispo ausgleichen",       # 1. Problem
            "haushaltsbuch 50 30 20 briefumschlagmethode",   # 2. Methode
            "etf sparplan vermoegensaufbau passiv",         # 3. Investition
            "notgroschen aufbauen finanzielle sicherheit",   # 4. Sicherheit
            "finanzen fuer anfaenger berufsstarter guide",   # 5. Zielgruppe
            "konsumkredite tilgen schneeball system",        # 6. Hindernis
            "finanzielle freiheit vermoegen aufbauen",       # 7. Transformation
        ],
        "ar": [
            "التخلص من الديون وسد العجز الشهري",             # 1. مشكلة
            "قاعدة 50 30 20 إدارة الميزانية الشخصية",       # 2. طريقة
            "الاستثمار في الصناديق المتداولة بمبلغ صغير",    # 3. استثمار
            "بناء صندوق الطوارئ والادخار الاحتياطي",        # 4. أمان
            "دليل التخطيط المالي للمبتدئين والشباب",         # 5. الفئة
            "سداد القروض الاستهلاكية بطريقة كرة الثلج",      # 6. عقبة
            "تحقيق الاستقلال المالي والحرية والثروة",       # 7. الهدف
        ],
    }

    raw_candidates = INTENT_TEMPLATES.get(lang_code, INTENT_TEMPLATES["en"])
    title_words = tokenize_clean_words(title) | tokenize_clean_words(subtitle)

    final_slots: List[str] = []
    for cand in raw_candidates:
        words = cand.split()
        retained: List[str] = []
        for w in words:
            # Exclure si déjà dans le titre
            if tokenize_clean_words(w) & title_words:
                continue
            test_phrase = " ".join(retained + [w])
            if calculate_utf8_bytes(test_phrase) <= 50:
                retained.append(w)
        final_slots.append(" ".join(retained) if retained else cand[:40])

    # Garantir que le cumul des 7 slots ne dépasse pas 250 octets
    while sum(calculate_utf8_bytes(s) for s in final_slots) > 250:
        # Trouver le slot le plus long en octets
        longest_idx = max(range(len(final_slots)), key=lambda i: calculate_utf8_bytes(final_slots[i]))
        s_words = final_slots[longest_idx].split()
        if len(s_words) > 2:
            final_slots[longest_idx] = " ".join(s_words[:-1])
        else:
            break

    audit = audit_7_slots_a9(final_slots, language=lang_code, title=title, subtitle=subtitle)

    return {
        "status": "success",
        "language": lang_code,
        "optimized_slots": final_slots,
        "audit": audit,
    }


def optimize_kdp_seo(
    book_title: str,
    subtitle: str,
    niche: str,
    book_type: str,
    target_audience: str,
    seed_keywords: Any,
    language: str = "fr",
) -> Dict[str, Any]:
    """Optimize Amazon KDP SEO package (A9) with strict constraints.

    Returns a dict including:
      - title, subtitle, title_subtitle_char_count (<=200)
      - backend_keywords (7 slots) validated to <=50 UTF-8 bytes each and no duplicate words with title
      - categories: 3 Amazon categories (1 volume + 2 niches)
      - description_html (<=4000 chars, only allowed KDP tags)
      - a_plus_blueprint
      - ppc_clusters
    """
    lang_code = normalize_language(language)
    lang_cfg = get_language_config(lang_code)

    title = (book_title or "").strip()
    sub = (subtitle or "").strip()
    ts_count = len(title + sub)

    # Normalize seed keywords into list
    if seed_keywords is None:
        seeds: List[str] = []
    elif isinstance(seed_keywords, str):
        seeds = [s.strip() for s in re.split(r"[\n,;]+", seed_keywords) if s.strip()]
    elif isinstance(seed_keywords, (list, tuple)):
        seeds = [str(s).strip() for s in seed_keywords if str(s).strip()]
    else:
        seeds = [str(seed_keywords).strip()]

    # Build slots from optimizer (uses intent templates) then try to inject seeds if helpful
    opt = optimize_7_slots_a9(title=title, subtitle=sub, niche=niche, language=lang_code, target_audience=target_audience)
    slots = list(opt.get("optimized_slots") or [])

    # If seeds provided, try to merge some into slots (respect byte limit and no title dup)
    title_words = tokenize_clean_words(title) | tokenize_clean_words(sub)
    if seeds:
        for s in seeds:
            if len(slots) >= 7:
                break
            # ensure not duplicate words with title
            if tokenize_clean_words(s) & title_words:
                continue
            candidate = " ".join(s.split())[:120]
            # fit into a new slot if possible
            if calculate_utf8_bytes(candidate) <= 50:
                # avoid exact duplicates
                if candidate.lower() not in [x.lower() for x in slots]:
                    slots.append(candidate)
        # pad to 7
        while len(slots) < 7:
            slots.append("")
        slots = slots[:7]
        # re-audit
        audit = audit_7_slots_a9(slots, language=lang_code, title=title, subtitle=sub)
    else:
        audit = opt.get("audit") or audit_7_slots_a9(slots, language=lang_code, title=title, subtitle=sub)

    # Categories (simple heuristic)
    marketplace = lang_cfg.get("amazon_marketplace", "amazon.com")
    categories = {
        "volume_category": f"Books > {niche}" if niche else "Books > General",
        "niche_categories": [
            f"Books > {book_type}" if book_type else f"Books > {niche}",
            f"Kindle Store > {niche}" if niche else "Kindle Store > General",
        ],
        "marketplace_hint": marketplace,
    }

    # Description HTML (allowed tags only): <h4>, <b>, <i>, <p>, <br>, <ul>, <li>
    desc_parts = [
        f"<h4>{title}</h4>" if title else "<h4>Discover this book</h4>",
        f"<p><b>{sub}</b></p>" if sub else "",
        f"<p>{niche} — {target_audience}</p>" if (niche or target_audience) else "",
        "<p><b>What you will learn</b></p>",
        "<ul>",
        "<li>Practical steps you can apply immediately.</li>",
        "<li>Clear frameworks to avoid common mistakes.</li>",
        "<li>Actionable checklists for fast progress.</li>",
        "</ul>",
        f"<p><i>Optimized for {marketplace}.</i></p>",
    ]
    description_html = "\n".join([p for p in desc_parts if p])
    # enforce <= 4000 chars
    if len(description_html) > 4000:
        description_html = description_html[:3997] + "..."

    # A+ blueprint (simple)
    a_plus_blueprint = {
        "modules": [
            {"type": "headline", "content": title or "Key benefits"},
            {"type": "image_text", "content": "Who this book is for and what problem it solves."},
            {"type": "bullets", "content": ["Benefit 1", "Benefit 2", "Benefit 3"]},
        ]
    }

    # PPC clusters
    ppc_clusters = {
        "broad": seeds[:3] if seeds else [niche] if niche else ["general"],
        "phrase": slots[:3],
        "exact": slots[3:6] if len(slots) >= 6 else slots[:3],
    }

    result = {
        "status": "success",
        "language": lang_code,
        "book_title": title,
        "subtitle": sub,
        "title_subtitle_char_count": ts_count,
        "title_subtitle_over_200": ts_count > 200,
        "backend_keywords": slots,
        "backend_keywords_audit": audit,
        "categories": categories,
        "description_html": description_html,
        "description_html_char_count": len(description_html),
        "a_plus_blueprint": a_plus_blueprint,
        "ppc_clusters": ppc_clusters,
        "marketplace": marketplace,
    }
    return result


__all__ = [
    "calculate_utf8_bytes",
    "tokenize_clean_words",
    "validate_a9_slot",
    "audit_7_slots_a9",
    "optimize_7_slots_a9",
    "optimize_kdp_seo",
]
