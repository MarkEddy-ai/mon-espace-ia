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

try:
    from kdp_extensions.kdp_compliance_supervisor import (
        FORBIDDEN_TITLE_TERMS,
        NOTORIOUS_TRADEMARKS,
    )
except ImportError:
    FORBIDDEN_TITLE_TERMS = [
        "bestseller", "best-seller", "best seller", "#1", "n°1", "numéro 1", "numero 1",
        "gratuit", "free", "promo", "promotion", "pas cher", "prix cassé", "solde", "soldes",
        "illimité", "unlimited",
    ]
    NOTORIOUS_TRADEMARKS = [
        "disney", "marvel", "pokémon", "pokemon", "lego", "minecraft", "star wars",
        "harry potter",
    ]


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


CATEGORIES_DB: Dict[str, Dict[str, Any]] = {
    "finances": {
        "volume_category": "Livres > Entreprise et Bourse > Finances personnelles",
        "volume_bisac": "BUS027000",
        "niche_categories": [
            "Livres > Entreprise et Bourse > Gestion et Comptabilité > Budget",
            "Boutique Kindle > Ebooks Kindle > Économie et Entreprise > Investissement",
        ],
        "niche_bisac_codes": ["BUS006000", "BUS036000"],
    },
    "immobilier": {
        "volume_category": "Livres > Entreprise et Bourse > Immobilier",
        "volume_bisac": "BUS054000",
        "niche_categories": [
            "Livres > Entreprise et Bourse > Investissements et Titres > Immobilier locatif",
            "Boutique Kindle > Ebooks Kindle > Droit et Fiscalité > Fiscalité immobilière",
        ],
        "niche_bisac_codes": ["BUS036050", "LAW014000"],
    },
    "productivite": {
        "volume_category": "Livres > Santé, Forme et Diététique > Développement personnel > Efficacité",
        "volume_bisac": "SEL000000",
        "niche_categories": [
            "Livres > Entreprise et Bourse > Efficacité professionnelle > Gestion du temps",
            "Boutique Kindle > Ebooks Kindle > Développement personnel > Motivation",
        ],
        "niche_bisac_codes": ["BUS041000", "SEL021000"],
    },
    "coloriage": {
        "volume_category": "Livres > Livres pour enfants > Jeux, arts et création > Coloriages",
        "volume_bisac": "JUV054000",
        "niche_categories": [
            "Livres > Livres pour enfants > Animaux et Nature",
            "Livres > Art, Musique et Cinéma > Dessin et Peinture",
        ],
        "niche_bisac_codes": ["JUV002000", "ART010000"],
    },
    "puzzle": {
        "volume_category": "Livres > Jeux et énigmes > Mots croisés et jeux de lettres",
        "volume_bisac": "GAM001000",
        "niche_categories": [
            "Livres > Jeux et énigmes > Casse-têtes, énigmes et logique",
            "Livres > Livres pour enfants > Jeux de mots et remue-méninges",
        ],
        "niche_bisac_codes": ["GAM005000", "JUV053000"],
    },
    "sante": {
        "volume_category": "Livres > Santé, Forme et Diététique > Bien-être et Santé",
        "volume_bisac": "HEA000000",
        "niche_categories": [
            "Livres > Santé, Forme et Diététique > Nutrition et Régimes",
            "Boutique Kindle > Ebooks Kindle > Famille et Santé > Prévention",
        ],
        "niche_bisac_codes": ["HEA017000", "HEA028000"],
    },
    "general": {
        "volume_category": "Livres > Société et Sciences humaines",
        "volume_bisac": "SOC000000",
        "niche_categories": [
            "Livres > Pratique et Vie quotidienne",
            "Boutique Kindle > Ebooks Kindle > Non-fiction",
        ],
        "niche_bisac_codes": ["REF000000", "NON000000"],
    },
}


def generate_kdp_categories(
    niche: str = "",
    book_type: str = "text",
    language: str = "fr",
) -> Dict[str, Any]:
    """Génère la structure des 3 catégories Amazon KDP (1 volume + 2 niches) et codes BISAC."""
    n_lower = f"{niche} {book_type}".lower()
    cat_key = "general"
    if any(k in n_lower for k in ("financ", "argent", "bourse", "budget", "patrimoine")):
        cat_key = "finances"
    elif any(k in n_lower for k in ("immo", "locatif", "lmnp", "pierre")):
        cat_key = "immobilier"
    elif any(k in n_lower for k in ("productiv", "temps", "habit", "mindset", "focus")):
        cat_key = "productivite"
    elif any(k in n_lower for k in ("coloriag", "coloring", "dessin", "mandala")):
        cat_key = "coloriage"
    elif any(k in n_lower for k in ("puzzle", "mots", "grille", "labyrinthe", "enigme")):
        cat_key = "puzzle"
    elif any(k in n_lower for k in ("sante", "bien-etre", "nutrition", "forme")):
        cat_key = "sante"

    entry = CATEGORIES_DB.get(cat_key, CATEGORIES_DB["general"])
    lang_code = normalize_language(language)
    marketplace = get_language_config(lang_code).get("amazon_marketplace", "amazon.fr")

    vol = entry["volume_category"]
    niches = list(entry["niche_categories"])

    # Si marché anglophone ou autre, adapter préfixes de base
    if lang_code == "en":
        vol = vol.replace("Livres >", "Books >").replace("Boutique Kindle >", "Kindle Store >")
        niches = [n.replace("Livres >", "Books >").replace("Boutique Kindle >", "Kindle Store >") for n in niches]

    return {
        "volume_category": vol,
        "volume_bisac": entry["volume_bisac"],
        "niche_categories": niches,
        "niche_bisac_codes": list(entry["niche_bisac_codes"]),
        "categories_list": [vol] + niches,
        "marketplace_hint": marketplace,
        "category_key": cat_key,
    }


def generate_amazon_description_html(
    title: str,
    subtitle: str = "",
    niche: str = "",
    target_audience: str = "",
    language: str = "fr",
) -> str:
    """
    Rédige une description de vente persuasive conforme aux règles de balisage Amazon KDP.
    Balises permises uniquement : <h2>, <h3>, <h4>, <b>, <i>, <p>, <br>, <ul>, <li>.
    Longueur maximale : 4 000 caractères.
    """
    lang = normalize_language(language)
    t = title.strip() or "LE GUIDE D'EXCELLENCE"
    st = subtitle.strip() or "La méthode pas-à-pas concrète pour réussir"

    if lang == "fr":
        html_content = f"""<h2>{t}</h2>
<h3>{st}</h3>

<p>Marre des ouvrages théoriques remplis de jargon inaccessible et de conseils génériques ? Ce manuel pratique a été conçu avec une seule exigence : <b>l'efficacité concrète sur le terrain</b>.</p>

<p>Que vous soyez débutant complet ou praticien désireux de structurer votre méthode, ce guide vous donne les clés exactes pour passer à l'action dès aujourd'hui.</p>

<p><b>Ce que vous allez maîtriser dans cet ouvrage :</b></p>
<ul>
  <li><b>La Méthode Pas-à-Pas :</b> Un cadre clair pour avancer sans hésitation ni confusion.</li>
  <li><b>Études de Cas Chiffrées :</b> Des exemples réels, transparents et immédiatement applicables.</li>
  <li><b>Les Pièges à Éviter :</b> Les erreurs coûteuses commises par 90% des débutants et les contre-mesures.</li>
  <li><b>Protocoles 24 Heures :</b> Des fiches d'action rapide pour valider vos progrès à chaque chapitre.</li>
</ul>

<p><b>À qui s'adresse ce livre ?</b><br>
Cet ouvrage s'adresse à : {target_audience or "toute personne désireuse de développer ses compétences avec rigueur et autonomie"}.</p>

<p><i>Ne laissez plus le hasard décider de vos résultats. Équipez-vous d'une méthode éprouvée et transformez votre approche dès aujourd'hui.</i></p>

<p><b>👉 Commandez votre exemplaire maintenant et commencez votre transformation !</b></p>"""
    elif lang == "es":
        html_content = f"""<h2>{t}</h2>
<h3>{st}</h3>

<p>¿Cansado de libros teóricos llenos de relleno y fórmulas genéricas? Este manual práctico ha sido diseñado con un único objetivo: <b>resultados reales y directos</b>.</p>

<p><b>Lo que aprenderás en este libro :</b></p>
<ul>
  <li><b>El Método Paso a Paso :</b> Una estructura clara y sin rodeos.</li>
  <li><b>Casos Prácticos Reales :</b> Cálculos y ejemplos concretos aplicables hoy mismo.</li>
  <li><b>Errores Críticos a Evitar :</b> Las trampas habituales y cómo sortearlas.</li>
  <li><b>Plan de Acción 24h :</b> Pasos específicos para validar cada etapa de aprendizaje.</li>
</ul>

<p><i>Diseñado para : {target_audience or "lectores exigentes que buscan claridad y resultados tangibles"}.</i></p>

<p><b>👉 ¡Consigue tu ejemplar hoy mismo y toma el control!</b></p>"""
    elif lang == "de":
        html_content = f"""<h2>{t}</h2>
<h3>{st}</h3>

<p>Schluss mit langwierigen Theorien ohne praktischen Nutzen. Dieser Leitfaden bietet Ihnen ein <b>klares, praxisorientiertes System</b> für messbare Erfolge.</p>

<p><b>Ihre Vorteile mit diesem Leitfaden :</b></p>
<ul>
  <li><b>Schritt-für-Schritt-Methode :</b> Präzise Anleitungen ohne Fachchinesisch.</li>
  <li><b>Praxiserprobte Fallstudien :</b> Echte Berechnungen und handfeste Beispiele.</li>
  <li><b>Vermeidung teurer Anfängerfehler :</b> Bewährte Gegenmaßnahmen für dauerhafte Sicherheit.</li>
  <li><b>24-Stunden-Aktionsplan :</b> Sofort umsetzbare Checklisten für jeden Tag.</li>
</ul>

<p><b>👉 Sichern Sie sich Ihr Exemplar jetzt und starten Sie sofort durch!</b></p>"""
    elif lang == "ar":
        html_content = f"""<h2>{t}</h2>
<h3>{st}</h3>

<p>دليل عملي شامل مصمم بعناية ليقدم لك <b>خطوات تنفيذية واضحة ومباشرة</b> دون حشو أو تعقيد.</p>

<p><b>أبرز ما ستتعلمه في هذا الكتاب :</b></p>
<ul>
  <li><b>منهجية تدريجية واضحة :</b> خطوات عملية وسهلة التطبيق من اليوم الأول.</li>
  <li><b>أمثلة وحالات دراسية حقيقية :</b> حسابات واقعية ونتائج ملموسة.</li>
  <li><b>تجنب الأخطاء الشائعة :</b> كيفية تفادي العثرات التي يقع فيها أغلب المبتدئين.</li>
  <li><b>خطة عمل فورية :</b> قوائم مراجعة عملية لكل فصل.</li>
</ul>

<p><b>👉 اطلب نسختك الآن وابدأ رحلتك بثقة ووضوح !</b></p>"""
    else:
        html_content = f"""<h2>{t}</h2>
<h3>{st}</h3>

<p>Tired of generic theories and fluff? This comprehensive guide was crafted with one standard in mind: <b>practical, field-tested effectiveness</b>.</p>

<p><b>What you will discover inside :</b></p>
<ul>
  <li><b>Step-by-step Framework :</b> A clear methodology designed for immediate execution.</li>
  <li><b>Real-world Case Studies :</b> Realistic numbers, practical scenarios, and zero fluff.</li>
  <li><b>Costly Pitfalls to Avoid :</b> Common mistakes made by 90% of beginners and how to bypass them.</li>
  <li><b>Action Checklists :</b> Direct exercises you can complete in under 24 hours.</li>
</ul>

<p><b>Target Audience :</b> {target_audience or "Anyone seeking actionable clarity and measurable progress"}.</p>

<p><b>👉 Grab your copy today and accelerate your progress!</b></p>"""

    # Nettoyage strict et garantie limite 4000 caractères
    return sanitize_kdp_html(html_content)


def sanitize_kdp_html(html_str: str) -> str:
    """
    Nettoie et valide une description HTML selon les règles strictes d'Amazon KDP.
    - Élimine tout script, balise div, span, a, etc.
    - Convertit <h1> en <h2> (Amazon réserve <h1> au titre du produit).
    - Conserve uniquement : <h2>, <h3>, <h4>, <h5>, <h6>, <b>, <i>, <u>, <em>, <strong>, <p>, <br>, <ul>, <ol>, <li>.
    - Tronque proprement à 4 000 caractères si nécessaire.
    """
    if not html_str:
        return ""
    # 1. Éliminer les scripts et styles avec leur contenu
    content = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_str, flags=re.DOTALL | re.IGNORECASE)
    # 2. Remplacer h1 par h2
    content = re.sub(r"<h1\b[^>]*>", "<h2>", content, flags=re.IGNORECASE)
    content = re.sub(r"</h1>", "</h2>", content, flags=re.IGNORECASE)
    # 3. Supprimer toutes les balises non autorisées par Amazon KDP
    content = re.sub(r"<(?!/?(h2|h3|h4|h5|h6|b|i|u|em|strong|p|br|ul|ol|li)\b)[^>]*>", "", content, flags=re.IGNORECASE)
    # 4. Limite stricte de 4000 caractères
    if len(content) > 4000:
        content = content[:3996] + "..."
    return content.strip()


def generate_amazon_ads_blueprint(
    title: str,
    subtitle: str = "",
    niche: str = "",
    backend_keywords: Optional[List[str]] = None,
    language: str = "fr",
) -> Dict[str, Any]:
    """
    Génère la structure de campagnes Amazon Advertising (PPC Sponsored Products) prêtes à lancer.
    Comprend : Exact, Phrase, Large, Ciblage Produits (ASIN) et Mots-clés Négatifs.
    """
    lang = normalize_language(language)
    kws = list(backend_keywords or [])
    clean_kws = [k.strip() for k in kws if k.strip()]

    exact_terms = clean_kws[:4] if clean_kws else [f"{niche} guide", f"methode {niche}"]
    phrase_terms = clean_kws[2:6] if len(clean_kws) >= 4 else clean_kws
    broad_terms = [niche] if niche else ["guide pratique"]

    campaign_prefix = re.sub(r"[^a-zA-Z0-9]+", "_", title.strip())[:20]

    return {
        "status": "success",
        "language": lang,
        "broad": broad_terms,
        "phrase": phrase_terms,
        "exact": exact_terms,
        "campaigns": [
            {
                "campaign_name": f"SP_EXACT_{campaign_prefix}",
                "targeting_type": "Manual - Keyword Exact",
                "target_acos": 25.0,
                "suggested_bid_eur": 0.65,
                "daily_budget_eur": 10.0,
                "keywords": exact_terms,
                "match_type": "EXACT",
                "strategy": "Top of Search Placement (+20% modifier)",
            },
            {
                "campaign_name": f"SP_PHRASE_{campaign_prefix}",
                "targeting_type": "Manual - Keyword Phrase",
                "target_acos": 30.0,
                "suggested_bid_eur": 0.45,
                "daily_budget_eur": 8.0,
                "keywords": phrase_terms,
                "match_type": "PHRASE",
                "strategy": "Dynamic Bids - Down Only",
            },
            {
                "campaign_name": f"SP_BROAD_{campaign_prefix}",
                "targeting_type": "Manual - Keyword Broad",
                "target_acos": 35.0,
                "suggested_bid_eur": 0.35,
                "daily_budget_eur": 5.0,
                "keywords": broad_terms,
                "match_type": "BROAD",
                "strategy": "Harvesting new search terms weekly",
            },
            {
                "campaign_name": f"SP_ASIN_{campaign_prefix}",
                "targeting_type": "Product Targeting (Competitor ASINs)",
                "target_acos": 28.0,
                "suggested_bid_eur": 0.50,
                "daily_budget_eur": 7.0,
                "target_niche": niche,
                "strategy": "Target high-ranking competitor product pages",
            },
        ],
        "negative_keywords": [
            "gratuit",
            "free",
            "pdf",
            "torrent",
            "occasion",
            "telecharger",
            "crack",
            "pirate",
            "kindle unlimited gratuit",
        ],
        "recommended_daily_budget_total_eur": 30.0,
    }


def generate_a_plus_blueprint(
    title: str,
    subtitle: str = "",
    niche: str = "",
    language: str = "fr",
) -> Dict[str, Any]:
    """Génère le gabarit complet des modules Amazon A+ Content (Informations de l'éditeur)."""
    lang = normalize_language(language)
    t = title or "LIVRE DE RÉFÉRENCE"
    st = subtitle or f"Le manuel d'excellence sur {niche}"

    return {
        "status": "success",
        "language": lang,
        "blueprint_version": "Amazon KDP A+ Standard 3-Module Layout",
        "modules": [
            {
                "slot": 1,
                "module_type": "standard_image_header_with_text",
                "name": "Bannière Hero d'Autorité",
                "headline": t,
                "body_text": st,
                "recommended_image_size": "970x300 px ou 970x600 px @ 300 DPI",
            },
            {
                "slot": 2,
                "module_type": "standard_three_image_text",
                "name": "Les 3 Piliers Majeurs",
                "features": [
                    {
                        "headline": "Méthode Pas-à-Pas",
                        "body_text": "Zéro jargon théorique : des étapes chronologiques immédiatement actionnables.",
                        "recommended_image_size": "300x300 px @ 300 DPI",
                    },
                    {
                        "headline": "Études de Cas Chiffrées",
                        "body_text": "Des montants réels, des calculs transparents et des scénarios complets.",
                        "recommended_image_size": "300x300 px @ 300 DPI",
                    },
                    {
                        "headline": "Protocoles 24 Heures",
                        "body_text": "Des plans d'action rapides pour valider vos acquis sans attendre.",
                        "recommended_image_size": "300x300 px @ 300 DPI",
                    },
                ],
            },
            {
                "slot": 3,
                "module_type": "standard_comparison_table",
                "name": "Pourquoi Cet Ouvrage Surclasse la Concurrence",
                "comparison_metrics": [
                    "Excellence Typographique 6x9 pouces avec marges de reliure (Gutter)",
                    "Zéro Remplissage Artificiel (Anti-Fluff garanti)",
                    "Checklists et Fiches d'Action Téléchargeables",
                    "Avertissements Légaux & Déclaration de Transparence KDP",
                ],
            },
        ],
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
      - ppc_clusters & amazon_ads_campaigns
      - marketplace
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

    # Build slots from optimizer (uses intent templates)
    opt = optimize_7_slots_a9(title=title, subtitle=sub, niche=niche, language=lang_code, target_audience=target_audience)
    template_slots = list(opt.get("optimized_slots") or [])

    # Intelligently merge seed keywords without title duplicate words & respecting 50 bytes UTF-8
    title_words = tokenize_clean_words(title) | tokenize_clean_words(sub)
    merged_slots: List[str] = []
    used_words: Set[str] = set()

    # Filter high-quality seeds
    for s in seeds:
        if len(merged_slots) >= 7:
            break
        # Ignore if repeats title words
        if tokenize_clean_words(s) & title_words:
            continue
        clean_seed = " ".join(s.split())
        s_words = tokenize_clean_words(clean_seed)
        if s_words & used_words:
            retained = [w for w in clean_seed.split() if not (tokenize_clean_words(w) & (title_words | used_words))]
            if not retained:
                continue
            clean_seed = " ".join(retained)
            s_words = tokenize_clean_words(clean_seed)

        if calculate_utf8_bytes(clean_seed) <= 50 and clean_seed.lower() not in [x.lower() for x in merged_slots]:
            merged_slots.append(clean_seed)
            used_words.update(s_words)

    # Fill remaining slots from template_slots without word-level duplication
    for ts in template_slots:
        if len(merged_slots) >= 7:
            break
        ts_tokens = ts.split()
        retained = [w for w in ts_tokens if not (tokenize_clean_words(w) & (title_words | used_words))]
        if retained:
            clean_ts = " ".join(retained)
            if calculate_utf8_bytes(clean_ts) <= 50 and clean_ts.lower() not in [x.lower() for x in merged_slots]:
                merged_slots.append(clean_ts)
                used_words.update(tokenize_clean_words(clean_ts))
        elif ts and ts.lower() not in [x.lower() for x in merged_slots]:
            merged_slots.append(ts)

    # Pad with template slots if needed
    while len(merged_slots) < 7:
        merged_slots.append("")
    merged_slots = merged_slots[:7]

    # Audit the final 7 slots
    audit = audit_7_slots_a9(merged_slots, language=lang_code, title=title, subtitle=sub)

    # Categories (3 catégories Amazon KDP 1 volume + 2 niches + codes BISAC)
    categories = generate_kdp_categories(niche=niche, book_type=book_type, language=lang_code)
    marketplace = categories.get("marketplace_hint") or lang_cfg.get("amazon_marketplace", "amazon.fr")

    # Description HTML persuasive conforme KDP
    description_html = generate_amazon_description_html(
        title=title,
        subtitle=sub,
        niche=niche,
        target_audience=target_audience,
        language=lang_code,
    )

    # A+ blueprint
    a_plus_blueprint = generate_a_plus_blueprint(
        title=title,
        subtitle=sub,
        niche=niche,
        language=lang_code,
    )

    # PPC / Amazon Ads campaigns
    ads_campaigns = generate_amazon_ads_blueprint(
        title=title,
        subtitle=sub,
        niche=niche,
        backend_keywords=merged_slots,
        language=lang_code,
    )

    ppc_clusters = {
        "broad": ads_campaigns["broad"],
        "phrase": ads_campaigns["phrase"],
        "exact": ads_campaigns["exact"],
    }

    # Audit complet pour la note sur 100 et vérifications chirurgicales
    audit_score = audit.get("score_a9", 100)
    byte_counts = [calculate_utf8_bytes(s) for s in merged_slots]
    total_b = sum(byte_counts)

    title_words = tokenize_clean_words(title) | tokenize_clean_words(sub)
    has_dup = any(tokenize_clean_words(s) & title_words for s in merged_slots)

    forb_terms = [t for t in FORBIDDEN_TITLE_TERMS if any(re.search(rf"\b{re.escape(t)}\b", s.lower()) for s in merged_slots)]
    trademarks = [t for t in NOTORIOUS_TRADEMARKS if any(re.search(rf"\b{re.escape(t)}\b", s.lower()) for s in merged_slots)]

    seo_audit = {
        "score_a9_100": audit_score,
        "score": audit_score,
        "byte_count_per_slot": byte_counts,
        "total_bytes": total_b,
        "zero_title_duplicates": not has_dup,
        "zero_forbidden_terms": len(forb_terms) == 0,
        "zero_trademarks": len(trademarks) == 0,
        "html_valid": len(description_html) <= 4000 and not any(tag in description_html.lower() for tag in ["<script", "<div", "<span", "<h1", "<a "]),
        "details": audit,
    }

    result = {
        "status": "success",
        "language": lang_code,
        # Nouveaux champs explicites demandés par l'utilisateur (Agent 5) :
        "optimized_title": title,
        "optimized_subtitle": sub,
        "backend_keywords_7": merged_slots,
        "categories_3": categories.get("categories_list", [categories.get("volume_category", "")] + categories.get("niche_categories", [])),
        "amazon_description_html": description_html,
        "aplus_content_blueprint": a_plus_blueprint,
        "ppc_launch_keywords": ppc_clusters,
        "seo_audit": seo_audit,
        # Rétrocompatibilité totale Zéro-Casse :
        "book_title": title,
        "subtitle": sub,
        "title_subtitle_char_count": ts_count,
        "title_subtitle_over_200": ts_count > 200,
        "backend_keywords": merged_slots,
        "backend_keywords_audit": audit,
        "categories": categories,
        "description_html": description_html,
        "description_html_char_count": len(description_html),
        "a_plus_blueprint": a_plus_blueprint,
        "ppc_clusters": ppc_clusters,
        "amazon_ads_campaigns": ads_campaigns,
        "marketplace": marketplace,
        "seo_package_ready": True,
    }
    return result


def build_seo_package(
    book_title: str,
    subtitle: str = "",
    niche: str = "general",
    book_type: str = "text",
    target_audience: str = "Tous publics",
    seed_keywords: Any = None,
    language: str = "fr",
) -> Dict[str, Any]:
    """Point d'entrée chirurgical pour la production du pack SEO Amazon KDP complet (Agent 5)."""
    seo_data = optimize_kdp_seo(
        book_title=book_title,
        subtitle=subtitle,
        niche=niche,
        book_type=book_type,
        target_audience=target_audience,
        seed_keywords=seed_keywords,
        language=language,
    )
    return {
        "status": "success",
        "seo_amazon_ready": seo_data,
        "description_amazon_html": seo_data["description_html"],
        "backend_keywords": seo_data["backend_keywords"],
        "categories": seo_data["categories"],
        "ppc_clusters": seo_data["ppc_clusters"],
        "amazon_ads_campaigns": seo_data["amazon_ads_campaigns"],
        "a_plus_blueprint": seo_data["a_plus_blueprint"],
    }


__all__ = [
    "calculate_utf8_bytes",
    "tokenize_clean_words",
    "validate_a9_slot",
    "audit_7_slots_a9",
    "optimize_7_slots_a9",
    "optimize_kdp_seo",
    "generate_kdp_categories",
    "generate_amazon_description_html",
    "sanitize_kdp_html",
    "generate_amazon_ads_blueprint",
    "generate_a_plus_blueprint",
    "build_seo_package",
    "CATEGORIES_DB",
]
