# -*- coding: utf-8 -*-
"""
kdp_extensions/brief_enhancer.py — Moteur d'enrichissement et d'angles éditoriaux KDP.

Fournit :
1. "Angle Aléatoire" : Génère instantanément un angle différenciant, percutant et concret
   selon la niche et le type d'ouvrage (Non-Fiction, Coloriage, Puzzles), disponible dans
   les 5 langues KDP (FR, EN, ES, DE, AR).
2. "Enrichir les détails" : Transforme un brouillon ou brief brut en un cahier des charges
   éditorial structuré (Cible précise, Promesse unique, Ton humain, Composantes par chapitre,
   Règles anti-fluff KDP).
3. Résilience totale hors-ligne : Repli déterministe haute fidélité sans erreur si Gemini
   ou le réseau est indisponible.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from kdp_extensions.i18n_config import normalize_language

# ==============================================================================
# BIBLIOTHÈQUE D'ANGLES ÉDITORIAUX PERCUTANTS PAR GENRE ET LANGUE
# ==============================================================================

ANGLES_NON_FICTION: Dict[str, List[Dict[str, str]]] = {
    "fr": [
        {
            "suggested_angle": "Méthode terrain en 30 jours sans jargon",
            "target_audience": "Débutants et actifs de 25-45 ans pressés",
            "tone": "Direct, empathique et ultra-pragmatique",
            "brief": (
                "🎯 Public Cible : Débutants et actifs de 25-45 ans cherchant une transformation concrète.\n"
                "💡 Promesse Unique : Maîtriser les fondamentaux et passer à l'action en 30 jours sans jargon théorique.\n"
                "🎙️ Ton & Voix : Direct, chaleureux, bienveillant mais sans complaisance. Bannir tout ton académique.\n"
                "📋 Exigences par Chapitre : Démarrer par un contre-pied cognitif ou une étude de cas chiffrée réelle. "
                "Inclure un piège fréquent évité et terminer obligatoirement par un encadré 'Action Immédiate 24h' en 3 étapes.\n"
                "🚫 Règle Anti-Fluff : Proscription absolue des formules de remplissage ('Dans ce chapitre nous allons...'). "
                "Privilégier la densité d'information, des ratios chiffrés et des modèles prêts à l'emploi."
            ),
        },
        {
            "suggested_angle": "Autopsie des 7 erreurs fatales et contre-attaques prouvées",
            "target_audience": "Pratiquants intermédiaires déçus par les méthodes standard",
            "tone": "Analytique, percutant et sans filtre",
            "brief": (
                "🎯 Public Cible : Profils intermédiaires ayant déjà testé des solutions classiques sans résultats durables.\n"
                "💡 Promesse Unique : Comprendre pourquoi 90% des débutants échouent et adopter les contre-attaques validées sur le terrain.\n"
                "🎙️ Ton & Voix : Factuel, incisif et déculpabilisant. S'appuyer sur la réalité plutôt que des promesses magiques.\n"
                "📋 Exigences par Chapitre : Analyser chaque erreur fatale avec ses coûts cachés. Fournir un tableau comparatif "
                "'Méthode naïve vs Contre-attaque d'élite' et un protocole de redressement immédiat.\n"
                "🚫 Règle Anti-Fluff : Aucune généralité tolérée. Des chiffres d'impact réels et des retours d'expérience authentiques."
            ),
        },
        {
            "suggested_angle": "Système minimaliste & automatisation (15 minutes par semaine)",
            "target_audience": "Professionnels et parents débordés avec charge mentale élevée",
            "tone": "Épuré, synthétique et orienté productivité 80/20",
            "brief": (
                "🎯 Public Cible : Professionnels et parents actifs avec un temps restreint et une forte charge mentale.\n"
                "💡 Promesse Unique : Mettre en place une routine minimaliste efficace en 15 minutes par semaine grâce au levier 80/20.\n"
                "🎙️ Ton & Voix : Clair, apaisant et ultra-structuré. Chaque mot doit mériter sa place.\n"
                "📋 Exigences par Chapitre : Présenter des règles de décision binaire (Oui/Non), des schémas de flux décisionnels "
                "et des checklists visuelles prêtes à photocopier.\n"
                "🚫 Règle Anti-Fluff : Pas de digressions philosophiques. Des protocoles condensés immédiatement applicables."
            ),
        },
        {
            "suggested_angle": "Psychologie comportementale & neuro-habitudes durables",
            "target_audience": "Lecteurs réflexifs cherchant à comprendre leurs blocages inconscients",
            "tone": "Scientifique, pédagogique et captivant",
            "brief": (
                "🎯 Public Cible : Lecteurs désireux de vaincre la procrastination et les sabotages inconscients.\n"
                "💡 Promesse Unique : Déjouer les pièges des biais cognitifs et ancrer des habitudes durables sans dépendre de la seule volonté.\n"
                "🎙️ Ton & Voix : Éclairé, scientifique mais accessible, illustré d'analogies du quotidien marquantes.\n"
                "📋 Exigences par Chapitre : Décomposer la boucle neurologique de l'habitude (déclencheur, routine, récompense). "
                "Proposer des micro-engagements à friction quasi-nulle.\n"
                "🚫 Règle Anti-Fluff : Zéro citation creuse de développement personnel. Des fondements appuyés sur les sciences comportementales."
            ),
        },
    ],
    "en": [
        {
            "suggested_angle": "30-Day Pragmatic Field Playbook (Zero-Fluff)",
            "target_audience": "Busy beginners & young professionals aged 25-45",
            "tone": "Direct, empathetic, and action-driven",
            "brief": (
                "🎯 Target Audience: Action-oriented beginners and professionals seeking real transformation.\n"
                "💡 Unique Promise: Master practical fundamentals and implement immediate solutions within 30 days.\n"
                "🎙️ Tone & Voice: Clear, authentic, no academic jargon. Treat the reader like a smart peer.\n"
                "📋 Chapter Essentials: Open with a surprising fact or counter-intuitive case study. "
                "Include a real-world numerical example, a beginner trap breakdown, and a 3-step '24h Action Protocol'.\n"
                "🚫 Anti-Fluff Rule: Strict ban on AI filler phrases ('In this chapter...'). Deliver high data density and battle-tested frameworks."
            ),
        },
        {
            "suggested_angle": "The 7 Fatal Mistakes Autopsy & Proven Turnaround Framework",
            "target_audience": "Intermediate practitioners stuck with poor results",
            "tone": "Analytical, sharp, and evidence-backed",
            "brief": (
                "🎯 Target Audience: Frustrated intermediate learners who tried standard advice and hit a wall.\n"
                "💡 Unique Promise: Diagnose why 90% fail and deploy field-tested countermeasures that actually move the needle.\n"
                "🎙️ Tone & Voice: Objective, candid, empowering through clarity.\n"
                "📋 Chapter Essentials: Deconstruct one fatal flaw per chapter with financial/time cost. "
                "Provide side-by-side comparison tables ('Naive Approach vs Elite Framework') and recovery checklists.\n"
                "🚫 Anti-Fluff Rule: Zero generic cheerleading. Focus on metrics, decision trees, and verifiable outcomes."
            ),
        },
    ],
    "es": [
        {
            "suggested_angle": "Método de campo en 30 días sin rodeos ni jerga",
            "target_audience": "Principiantes y profesionales ocupados de 25 a 45 años",
            "tone": "Directo, empático y ultrapráctico",
            "brief": (
                "🎯 Público Objetivo: Principiantes decididos que buscan resultados medibles sin teoría innecesaria.\n"
                "💡 Promesa Única: Dominar las claves operativas y aplicar soluciones en 30 días.\n"
                "🎙️ Tono y Voz: Claro, cercano y riguroso. Sin rodeos académicos ni frases hechas.\n"
                "📋 Requisitos por Capítulo: Abrir con un caso real con cifras concretas, señalar el error típico a evitar "
                "y cerrar con un plan de acción de 24 horas en 3 pasos.\n"
                "🚫 Regla Anti-Relleno: Cero clichés de autoayuda. Máxima densidad de valor práctico."
            ),
        },
    ],
    "de": [
        {
            "suggested_angle": "30-Tage-Praxisleitfaden ohne Fachchinesisch",
            "target_audience": "Einsteiger und Berufstätige (25-45 Jahre)",
            "tone": "Präzise, strukturiert und ergebnisorientiert",
            "brief": (
                "🎯 Zielgruppe: Berufstätige und Einsteiger mit begrenzter Zeit und hohem Anspruch.\n"
                "💡 Einzigartiges Versprechen: Klare Schritt-für-Schritt-Umsetzung in 30 Tagen mit messbaren Resultaten.\n"
                "🎙️ Tonfall: Professionell, direkt und ermutigend. Keine leeren Phrasen.\n"
                "📋 Kapitel-Vorgaben: Konkrete Zahlenbeispiele, Analyse typischer Fallstricke und ein verbindlicher 24-Stunden-Aktionsplan.\n"
                "🚫 Anti-Fluff-Prinzip: Kein KI-Fülltext. Höchste Informationsdichte und sofort anwendbare Vorlagen."
            ),
        },
    ],
    "ar": [
        {
            "suggested_angle": "دليل عملي وتطبيقي في 30 يوماً بدون حشو نظري",
            "target_audience": "المبتدئون والمهنيون الطموحون من عمر 25 إلى 45 عاماً",
            "tone": "مباشر، عملي، دقيق ومحفز للإنجاز الفوري",
            "brief": (
                "🎯 الجمهور المستهدف: المبتدئون الباحثون عن نتائج حقيقية وخطوات واضحة بدون تعقيد.\n"
                "💡 الوعد الفريد: السيطرة على الأساسيات وتطبيق حلول عملية خلال 30 يوماً بخطوات مجربة.\n"
                "🎙️ النبرة والأسلوب: واقعي، محفز ومحترم لوقت القارئ. الابتعاد التام عن المصطلحات الأكاديمية الجافة.\n"
                "📋 محتويات كل فصل: البدء بدراسة حالة رقمية واقعية، توضيح فخ شائع وتجنبه، والختام بخطة عمل 'تنفيذ خلال 24 ساعة'.\n"
                "🚫 قاعدة منع الحشو: حظر العبارات الإنشائية المكررة. التركيز التام على القيمة الميدانية القابلة للتطبيق."
            ),
        },
    ],
}

ANGLES_COLORIAGE: Dict[str, List[Dict[str, str]]] = {
    "fr": [
        {
            "suggested_angle": "Art-Thérapie & Sérénité : Contours d'ancrage épais anti-débordement",
            "target_audience": "Adultes stressés & débutants en quête de relaxation profonde",
            "tone": "Apaisant, immersif et bienveillant",
            "brief": (
                "🎨 Format & Style : Planches haute définition 300 DPI, noir pur #000000 sur fond blanc pur #FFFFFF.\n"
                "📐 Caractéristiques Graphiques : Contours nets et d'épaisseur moyenne à forte (2.5 à 4 pt) pour faciliter le coloriage sans déborder.\n"
                "🧘 Objectif Émotionnel : Favoriser l'état de 'flow' et réduire l'anxiété quotidienne en 20 minutes de coloriage par jour.\n"
                "📄 Conception Prépresse : Impression recto uniquement avec dos de page neutre anti-bavure."
            ),
        },
        {
            "suggested_angle": "Monde Botanique & Faune Majestueuse : Compositions harmonieuses",
            "target_audience": "Amateurs de nature, dessin floral et mandalas organiques",
            "tone": "Élégant, poétique et précis",
            "brief": (
                "🎨 Format & Style : 50 planches botaniques d'orfèvre équilibrant détails fins et grandes zones relaxantes.\n"
                "📐 Caractéristiques Graphiques : Motifs floraux, feuillages stylisés et animaux totems aux courbes douces.\n"
                "📄 Conception Prépresse : Marges de sécurité KDP strictes (0.5 po minimum) pour éviter toute coupure à la reliure."
            ),
        },
    ],
    "en": [
        {
            "suggested_angle": "Mindful Stress-Relief: Bold Line-Art for Deep Relaxation",
            "target_audience": "Stressed adults & beginners looking for creative calm",
            "tone": "Calming, elegant, and mindful",
            "brief": (
                "🎨 Style & Specs: Crisp 300 DPI vector line-art in pure black #000000 on pure white #FFFFFF.\n"
                "📐 Line Quality: Medium-to-bold clean contours preventing bleed-through and coloring frustration.\n"
                "📄 Prepress Safety: Single-sided prints with dark protective backing to preserve marker art."
            ),
        },
    ],
}

ANGLES_PUZZLES: Dict[str, List[Dict[str, str]]] = {
    "fr": [
        {
            "suggested_angle": "Gymnastique Cérébrale & Logique : Progression en 3 niveaux avec solutions complètes",
            "target_audience": "Adultes, seniors et passionnés d'énigmes cherchant à stimuler leur vivacité d'esprit",
            "tone": "Stimulant, ludique et gratifiant",
            "brief": (
                "🧩 Structure du Cahier : 8 types de jeux variés (Mots mêlés, Mots mélangés, Échelles de mots, Devinettes, Labyrinthes, etc.).\n"
                "📈 Progression : 3 paliers progressifs (Échauffement, Défi Logique, Maître des Mots).\n"
                "🔍 Ergonomie & Lisibilité : Typographie soignée sans empattement en corps généreux pour limiter la fatigue oculaire.\n"
                "✅ Solutionnaire Intégré : Solutions détaillées et aérées regroupées en fin d'ouvrage."
            ),
        },
    ],
    "en": [
        {
            "suggested_angle": "Brain Fitness & Deduction Challenge: 3-Tier Progressive Workbook",
            "target_audience": "Adults, seniors & puzzle enthusiasts seeking cognitive stimulation",
            "tone": "Engaging, rewarding, and clear",
            "brief": (
                "🧩 Book Structure: 8 diversified puzzle types with progressive difficulty tiers.\n"
                "🔍 Readability: Clean high-contrast typography with generous sizing for stress-free solving.\n"
                "✅ Answer Key: Clear, organized back-matter solutions section."
            ),
        },
    ],
}


# ==============================================================================
# MOTEUR PRINCIPAL D'ENRICHISSEMENT & DE GÉNÉRATION D'ANGLES
# ==============================================================================

def normalize_book_type(raw_type: Optional[str]) -> str:
    """Normalise la typologie du livre vers les 3 piliers : non-fiction, coloriage, puzzle."""
    t = (raw_type or "").strip().lower()
    if any(k in t for k in ("coloriage", "coloring")):
        return "coloriage"
    if any(k in t for k in ("puzzle", "jeux", "jeu", "enigme")):
        return "puzzle"
    return "non-fiction"


def enhance_kdp_brief(
    niche: str = "Finances Personnelles",
    book_type: str = "non-fiction",
    target_audience: str = "Adultes Débutants",
    current_brief: str = "",
    mode: str = "random",
    language: str = "fr"
) -> Dict[str, Any]:
    """
    Génère un angle aléatoire ou enrichit un brief éditorial existant.
    
    Modes:
      - 'random' : sélectionne un angle percutant adapté à la niche, au format et à la cible.
      - 'enhance' : transforme le texte saisi en un brief structuré de prestige.
    
    Garantit 100% de résilience sans erreur même sans réseau.
    """
    lang = normalize_language(language)
    btype = normalize_book_type(book_type)
    mode_clean = (mode or "random").strip().lower()
    niche_clean = (niche or "Finances Personnelles & Stratégie").strip()
    target_aud = (target_audience or "Adultes Débutants").strip()

    aud_lower = target_aud.lower()
    large_print_recommended = any(
        k in aud_lower for k in ("senior", "60+", "large print", "grands caractères", "grand caractère", "malvoyant")
    )

    if mode_clean == "random":
        return _generate_random_angle(niche_clean, btype, lang, target_aud, large_print_recommended)
    else:
        return _enrich_current_brief(niche_clean, btype, current_brief, lang, target_aud, large_print_recommended)


def _generate_random_angle(
    niche: str,
    btype: str,
    lang: str,
    target_audience: str = "Adultes Débutants",
    large_print_recommended: bool = False
) -> Dict[str, Any]:
    """Sélectionne et adapte un angle aléatoire concret pour la niche, la cible et le type de livre."""
    if btype == "coloriage":
        catalog = ANGLES_COLORIAGE.get(lang) or ANGLES_COLORIAGE.get("fr") or ANGLES_COLORIAGE["fr"]
    elif btype == "puzzle":
        catalog = ANGLES_PUZZLES.get(lang) or ANGLES_PUZZLES.get("fr") or ANGLES_PUZZLES["fr"]
    else:
        catalog = ANGLES_NON_FICTION.get(lang) or ANGLES_NON_FICTION.get("fr") or ANGLES_NON_FICTION["fr"]

    chosen = random.choice(catalog)
    brief_text = chosen["brief"]

    # Personnalisation légère de la niche dans le texte si pertinent
    if btype == "non-fiction" and niche.lower() not in brief_text.lower():
        prefix = f"📌 Thématique Cible : {niche}\n"
        brief_text = prefix + brief_text

    # Intégration de la cible spécifique si précisée
    effective_target = target_audience if target_audience and target_audience != "Adultes Débutants" else chosen.get("target_audience", target_audience)

    # Recommandations spécifiques Large Print pour seniors
    if large_print_recommended:
        brief_text += (
            "\n👓 Recommandation Grands Caractères (Large Print KDP) : "
            "Corps de texte 14-16 pt, interlignage 1.5, fort contraste noir pur, "
            "marges généreuses et ergonomie visuelle sans fatigue."
        )

    # Recommandations spécifiques enfants si pertinent
    aud_lower = target_audience.lower()
    if any(k in aud_lower for k in ("enfant", "maternelle", "primaire", "3-5", "3–5", "6-8", "6–8", "9-12", "9–12", "collège", "ado", "kid", "child")):
        brief_text += (
            f"\n👶 Adaptation Pédagogique ({target_audience}) : "
            "Consignes courtes et imagées, repères visuels clairs, progression graduée "
            "et valorisation bienveillante de chaque étape franchie."
        )

    return {
        "status": "success",
        "mode": "random",
        "brief": brief_text,
        "suggested_angle": chosen.get("suggested_angle", "Angle d'Élite KDP"),
        "target_audience": effective_target,
        "tone": chosen.get("tone", "Direct, pragmatique et humain"),
        "large_print_recommended": large_print_recommended,
        "book_type": btype,
        "language": lang,
        "niche": niche
    }


def _enrich_current_brief(
    niche: str,
    btype: str,
    current_brief: str,
    lang: str,
    target_audience: str = "Adultes Débutants",
    large_print_recommended: bool = False
) -> Dict[str, Any]:
    """
    Enrichit un brief utilisateur brut en un cahier des charges éditorial complet.
    Tente Gemini si configuré, avec repli immédiat et infaillible sur le moteur déterministe.
    """
    raw_brief = (current_brief or "").strip()
    
    # 1. Tentative d'appel IA via Gemini si disponible
    ai_enhanced = _try_gemini_enhance(niche, btype, raw_brief, lang, target_audience)
    if ai_enhanced:
        brief_final = ai_enhanced["brief"]
        if large_print_recommended and "grands caractères" not in brief_final.lower() and "large print" not in brief_final.lower():
            brief_final += "\n👓 Spécification Grands Caractères (Large Print KDP) : Typographie 14-16 pt, fort contraste et mise en page aérée."

        return {
            "status": "success",
            "mode": "enhance",
            "source": "ai_gemini",
            "brief": brief_final,
            "suggested_angle": ai_enhanced.get("suggested_angle", "Angle Personnalisé IA"),
            "target_audience": target_audience or ai_enhanced.get("target_audience", "Audience Cible Spécifiée"),
            "tone": ai_enhanced.get("tone", "Voix Humaine & Zéro-Fluff"),
            "large_print_recommended": large_print_recommended,
            "book_type": btype,
            "language": lang,
            "niche": niche
        }

    # 2. Repli déterministe de haute qualité (structuré, zéro erreur)
    return _deterministic_enhance(niche, btype, raw_brief, lang, target_audience, large_print_recommended)


def _deterministic_enhance(
    niche: str,
    btype: str,
    raw_brief: str,
    lang: str,
    target_audience: str = "Adultes Débutants",
    large_print_recommended: bool = False
) -> Dict[str, Any]:
    """Construit un brief éditorial structuré et dense de niveau professionnel sans IA."""
    base_text = raw_brief if len(raw_brief) >= 15 else f"Ouvrage de référence pratique sur '{niche}'"
    default_target = target_audience if target_audience else f"Lecteurs et praticiens dans la thématique '{niche}'"
    
    if lang == "en":
        target = f"Readers and practitioners in the '{niche}' space looking for actionable mastery"
        angle = f"Action-Driven Field Blueprint for {niche}"
        tone = "Direct, engaging, no-nonsense, and highly practical"
        structured_brief = (
            f"🎯 Target Audience: {target}.\n"
            f"💡 Core Promise & Transformation: Turn confusion into clarity through hands-on steps derived from: '{base_text}'.\n"
            f"🎙️ Tone & Voice: {tone}. Cut out filler and academic lectures.\n"
            f"📋 Chapter Architecture: Each chapter must feature 1 real-world case study with figures, 1 common pitfall to avoid, "
            f"and an immediate 3-step '24h Action Protocol'.\n"
            f"🚫 KDP Anti-Fluff Standards: No AI clichés ('In today's fast-paced world...'). "
            f"High information density, tangible takeaways, and immediate field value."
        )
    elif lang == "es":
        target = f"Lectores interesados en '{niche}' que buscan resultados rápidos y prácticos"
        angle = f"Guía práctica y estructurada de {niche}"
        tone = "Cercano, pragmático y orientado a la acción inmediata"
        structured_brief = (
            f"🎯 Público Objetivo: {target}.\n"
            f"💡 Promesa Central: Transformar la teoría en acciones medibles a partir de: '{base_text}'.\n"
            f"🎙️ Tono y Estilo: {tone}. Lenguaje claro y sin rodeos.\n"
            f"📋 Estructura Obligatoria: 1 caso práctico con datos reales por capítulo, 1 error común evitado y 1 plan de acción en 24 horas.\n"
            f"🚫 Normas Anti-Relleno KDP: Prohibidas las frases introductorias genéricas. Máximo rigor y utilidad directa."
        )
    elif lang == "de":
        target = f"Pragmatische Leser und Einsteiger im Bereich '{niche}'"
        angle = f"Strukturierter Praxis-Leitfaden für {niche}"
        tone = "Präzise, zielgerichtet und ohne überflüssige Theorie"
        structured_brief = (
            f"🎯 Zielgruppe: {target}.\n"
            f"💡 Kernversprechen: Schritt-für-Schritt-Umsetzung basierend auf: '{base_text}'.\n"
            f"🎙️ Tonalität: {tone}.\n"
            f"📋 Kapitelaufbau: Mindestens ein konkretes Zahlenbeispiel, ein Warnhinweis vor typischen Fehlern und ein 24h-Aktionsplan.\n"
            f"🚫 Anti-Fluff-Prinzip: Keine generischen Floskeln. Höchste Informationsdichte."
        )
    elif lang == "ar":
        target = f"القراء والمهتمون بمجال '{niche}' الباحثون عن تطبيق عملي سريع"
        angle = f"الدليل التطبيقي الشامل في {niche}"
        tone = "مباشر، عملي، دقيق وواضح تماماً"
        structured_brief = (
            f"🎯 الجمهور المستهدف: {target}.\n"
            f"💡 الوعد الأساسي والتحول: تحويل المعرفة إلى خطوات تطبيقية ملموسة انطلاقاً من: '{base_text}'.\n"
            f"🎙️ النبرة والأسلوب: {tone}. البعد التام عن التكرار والمقدمات الإنشائية الطويلة.\n"
            f"📋 مكونات كل فصل: دراسة حالة واقعية بالأرقام، فخ شائع يجب تجنبه، وخطة تطبيق فوري خلال 24 ساعة.\n"
            f"🚫 معايير الجودة KDP: منع حشو الذكاء الاصطناعي. كثافة معلوماتية عالية وقيمة مباشرة للقارئ."
        )
    else:  # Français (par défaut)
        target = f"Lecteurs et débutants motivés dans la thématique '{niche}'"
        angle = f"Guide d'action pragmatique & transformation concrète sur {niche}"
        tone = "Direct, bienveillant, humain et ultra-pragmatique"
        structured_brief = (
            f"🎯 Public Cible Précis : {target}.\n"
            f"💡 Promesse Unique & Transformation : Passer de la confusion à la maîtrise concrète à partir de : '{base_text}'.\n"
            f"🎙️ Ton & Voix d'Auteur : {tone}. Bannir toute condescendance et tout jargon universitaire.\n"
            f"📋 Composantes Obligatoires par Chapitre : 1 étude de cas chiffrée réelle, 1 erreur critique évitée "
            f"et 1 protocole d'action immédiate (24h) en 3 étapes.\n"
            f"🚫 Normes Anti-Fluff Amazon KDP : Interdiction formelle des formules de remplissage IA. "
            f"Densité d'information maximale, ratios chiffrés et modèles directement applicables."
        )

    if large_print_recommended:
        structured_brief += (
            "\n👓 Recommandation Grands Caractères (Large Print KDP) : "
            "Corps de texte 14-16 pt, interlignage 1.5, fort contraste noir pur, "
            "marges généreuses et ergonomie visuelle adaptée aux seniors."
        )

    aud_lower = target_audience.lower()
    if any(k in aud_lower for k in ("enfant", "maternelle", "primaire", "3-5", "3–5", "6-8", "6–8", "9-12", "9–12", "collège", "ado", "kid", "child")):
        structured_brief += (
            f"\n👶 Adaptation Pédagogique ({target_audience}) : "
            "Consignes courtes et imagées, repères visuels clairs, progression graduée "
            "et valorisation bienveillante de chaque étape franchie."
        )

    return {
        "status": "success",
        "mode": "enhance",
        "source": "deterministic_fallback",
        "brief": structured_brief,
        "suggested_angle": angle,
        "target_audience": target_audience or target,
        "tone": tone,
        "large_print_recommended": large_print_recommended,
        "book_type": btype,
        "language": lang,
        "niche": niche
    }


def _try_gemini_enhance(
    niche: str,
    btype: str,
    raw_brief: str,
    lang: str,
    target_audience: str = "Adultes Débutants"
) -> Optional[Dict[str, str]]:
    """Tente un enrichissement IA via Gemini avec un délai d'attente court. Retourne None si indisponible."""
    try:
        from call_ai import generer_texte_gemini
        import json

        system_prompt = (
            "Tu es un directeur éditorial d'élite pour Amazon KDP. "
            "Ta mission est de structurer le brief d'un livre en un cahier des charges d'écriture d'autorité. "
            "Réponds UNIQUEMENT en JSON avec les clés : 'brief' (texte complet structuré), "
            "'suggested_angle' (accroche en 4-8 mots), 'target_audience' (profil précis), 'tone' (ton d'écriture)."
        )
        user_prompt = (
            f"Niche: {niche}\n"
            f"Type de livre: {btype}\n"
            f"Cible / Audience visée: {target_audience}\n"
            f"Langue: {lang}\n"
            f"Brouillon ou idée de l'auteur: {raw_brief or 'Méthode pratique et accessible'}\n\n"
            "Génère un brief éditorial chirurgical avec 5 sections (Public cible, Promesse unique, Ton & Voix, "
            "Composantes obligatoires par chapitre, Normes anti-fluff KDP). Reste direct, percutant et dense."
        )

        res_text = generer_texte_gemini(
            system_prompt=system_prompt,
            prompt=user_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        if not res_text:
            return None

        # Nettoyage Markdown JSON éventuel
        clean_json = res_text.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.split("\n", 1)[-1]
            if clean_json.endswith("```"):
                clean_json = clean_json.rsplit("```", 1)[0]

        data = json.loads(clean_json.strip())
        if isinstance(data, dict) and "brief" in data:
            return {
                "brief": str(data["brief"]),
                "suggested_angle": str(data.get("suggested_angle", "Angle d'Élite")),
                "target_audience": str(data.get("target_audience", target_audience or "Lecteurs ciblés")),
                "tone": str(data.get("tone", "Direct et pragmatique")),
            }
    except Exception:
        # En cas d'erreur réseau, quota, timeout ou JSON invalide -> repli déterministe immédiat
        pass
    return None
