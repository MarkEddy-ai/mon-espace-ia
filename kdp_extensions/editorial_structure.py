"""
kdp_extensions/editorial_structure.py — Générateur Front-Matter & Back-Matter KDP.
(Structure éditoriale de prestige conforme aux normes d'édition Amazon KDP).

Ce module produit l'ensemble des pages préliminaires (Front-Matter) et
conclusives (Back-Matter) nécessaires à la publication d'un livre papier de haut rang :

FRONT-MATTER :
1. Faux-titre (Half-Title)
2. Du même auteur / Dans la même collection
3. Page de grand titre (Titre, sous-titre, auteur, maison d'édition)
4. Page de copyright & Mentions légales (ISBN, dépôt légal, clause de non-responsabilité adaptée)
5. Dédicace
6. Épigraphe (Citation d'autorité & attribution)
7. Sommaire / Table des matières paginée
8. Avant-propos / Note de l'auteur

BACK-MATTER :
1. Conclusion & Mot de la fin
2. Remerciements
3. À propos de l'auteur (Biographie & mission)
4. Pack de ressources offert (Appel à l'action / QR code / Fiches action)
5. Demande bienveillante d'avis honnête sur Amazon (conforme aux TOS Amazon)
6. Découvrir les autres ouvrages de la collection
7. Achevé d'imprimer (Colophon typographique et mentions d'impression KDP)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from kdp_extensions.i18n_config import (
    get_editorial_labels,
    normalize_language,
    is_rtl,
)


def get_default_editorial_metadata(
    niche: str = "Finances Personnelles",
    title: Optional[str] = None,
    author: str = "MarkEddy",
    publisher: str = "MarkEddy Éditions",
    isbn: Optional[str] = None,
) -> Dict[str, Any]:
    """Génère un dictionnaire de métadonnées éditoriales complet avec valeurs par défaut élégantes."""
    year = datetime.now(timezone.utc).year
    titre_effectif = title or f"L'ART DE MAÎTRISER {niche.upper()}"
    isbn_effectif = isbn or "979-8-8888-8888-8"

    # Clause de non-responsabilité adaptée à la niche
    n_lower = niche.lower()
    if any(k in n_lower for k in ("financ", "argent", "bourse", "investir", "patrimoine")):
        disclaimer = (
            "Avertissement légal : Les informations présentées dans cet ouvrage sont fournies à titre strictement "
            "éducatif et informatif. Elles ne constituent en aucun cas un conseil en investissement financier, "
            "fiscal ou juridique. L'auteur et l'éditeur déclinent toute responsabilité quant aux décisions financières "
            "prises par le lecteur. Tout investissement comporte un risque de perte en capital."
        )
    elif any(k in n_lower for k in ("sante", "bien-etre", "nutrition", "sommeil", "medecin")):
        disclaimer = (
            "Avertissement santé : Cet ouvrage a pour vocation de partager des principes d'hygiène de vie et de bien-être. "
            "Il ne se substitue pas à une consultation, un diagnostic ou un traitement médical professionnel. "
            "Consultez toujours un médecin qualifié avant d'entreprendre tout changement relatif à votre santé."
        )
    else:
        disclaimer = (
            "Avertissement : Cet ouvrage a pour but d'offrir des méthodes pratiques et éprouvées. Les résultats peuvent "
            "varier selon l'engagement et le contexte individuel. L'auteur et l'éditeur ne sauraient être tenus pour "
            "responsables des conséquences résultant de l'application directe ou indirecte des conseils prodigués."
        )

    return {
        "title": titre_effectif,
        "subtitle": f"Le guide pratique complet pour maîtriser {niche} pas à pas",
        "author": author,
        "publisher": publisher,
        "year": year,
        "isbn": isbn_effectif,
        "niche": niche,
        "disclaimer": disclaimer,
        "dedication": "À celles et ceux qui refusent le statu quo et osent transformer leurs ambitions en réalité.",
        "epigraph": {
            "quote": "La simplicité est la sophistication suprême.",
            "author": "Léonard de Vinci",
        },
        "author_bio": (
            f"{author} est auteur, chercheur et praticien passionné par la transmission du savoir concret. "
            f"À travers ses ouvrages, il s'attache à déconstruire les sujets complexes pour offrir des cadres "
            f"d'action limpides et directement applicables au quotidien."
        ),
        "bonus_resource": {
            "title": "Pack de Ressources & Fiches Pratiques Offert",
            "description": "Téléchargez gratuitement les feuilles de calcul, matrices d'évaluation et fiches récapitulatives.",
            "url": "https://markeddy.com/bonus-lecteur",
        },
        "edition_details": {
            "legal_deposit": f"Dépôt légal : {year}",
            "print_location": "Imprimé par Amazon Fulfillment Services",
            "typography_notes": "Composé en Merriweather et Cinzel. Papier certifié conforme aux normes environnementales.",
        },
    }


# ==============================================================================
# 1. GÉNÉRATION EN MARKDOWN PUR (POUR LE FLUX RÉDACTIONNEL)
# ==============================================================================

def generate_front_matter_markdown(meta: Dict[str, Any], language: str = "fr") -> str:
    """Génère l'intégralité du Front-Matter en Markdown avec séparateurs de page KDP (multilingue 5 langues)."""
    lang = normalize_language(meta.get("language") or language)
    labels = get_editorial_labels(lang)

    t = meta.get("title", "LIVRE KDP")
    st = meta.get("subtitle", "")
    author = meta.get("author", "Auteur")
    pub = meta.get("publisher", labels.get("publisher", "Éditions MarkEddy"))
    year = meta.get("year", 2026)
    isbn = meta.get("isbn", "979-8-0000-0000-0")
    disc = meta.get("disclaimer") or labels.get("disclaimer_text", "")
    ded = meta.get("dedication", "")
    epi = meta.get("epigraph", {})

    md = []

    # 1. Faux-Titre
    md.append(f"# {t}\n\n<div class=\"page-break\"></div>\n")

    # 2. Page de Titre Complète
    md.append(
        f"# {t}\n\n"
        f"### {st}\n\n"
        f"**{author}**\n\n"
        f"*{pub}*\n\n"
        f"<div class=\"page-break\"></div>\n"
    )

    # 3. Page de Copyright & Mentions Légales
    copy_notice = labels.get("copyright_notice", "Tous droits réservés.")
    md.append(
        f"**{t}**  \n"
        f"© {year} {author}. {copy_notice}  \n\n"
        f"{labels.get('publisher', 'Publié par')} {pub}.  \n"
        f"ISBN : {isbn}  \n"
        f"{labels.get('legal_deposit', 'Dépôt légal')} : {year}  \n\n"
        f"{copy_notice}\n\n"
        f"*{disc}*\n\n"
        f"<div class=\"page-break\"></div>\n"
    )

    # 4. Dédicace
    if ded:
        md.append(
            f"*« {ded} »*\n\n"
            f"<div class=\"page-break\"></div>\n"
        )

    # 5. Épigraphe
    if epi and isinstance(epi, dict) and "quote" in epi:
        md.append(
            f"> *« {epi.get('quote', '')} »*  \n"
            f"> — **{epi.get('author', '')}**\n\n"
            f"<div class=\"page-break\"></div>\n"
        )

    # 6. Sommaire d'Ouverture
    toc_title = labels.get("toc_title", "Sommaire")
    md.append(
        f"## Sommaire : {toc_title}\n\n"
        f"- **{labels.get('foreword', 'Avant-propos')}**\n"
        f"- **Partie I** : Les Fondations Stratégiques\n"
        f"- **Partie II** : La Méthode Opérationnelle Pas-à-Pas\n"
        f"- **Partie III** : L'Accélération & Les Résultats Durables\n"
        f"- **Conclusion & Perspectives**\n"
        f"- **Ressources & Outils Pratiques**\n\n"
        f"<div class=\"page-break\"></div>\n"
    )

    # 7. Avant-Propos
    foreword_label = labels.get("foreword", "Avant-Propos")
    md.append(
        f"## {foreword_label}\n\n"
        f"{'Ce livre n\'a pas été conçu pour encombrer une étagère ou flatter une curiosité intellectuelle passive.' if lang == 'fr' else 'This book was engineered as an operational instrument, eliminating all fluff.' if lang == 'en' else 'Este libro fue concebido como un instrumento operativo, sin teoría superflua.' if lang == 'es' else 'Dieses Buch ist als operatives Werkzeug konzipiert, das auf jegliches Füllmaterial verzichtet.' if lang == 'de' else 'هذا الكتاب صُمم كأداة تشغيلية عملية، خالية من أي حشو نظري.'}\n\n"
        f"<div class=\"page-break\"></div>\n"
    )

    return "\n".join(md)


def generate_back_matter_markdown(meta: Dict[str, Any], language: str = "fr") -> str:
    """Génère l'intégralité du Back-Matter en Markdown (multilingue 5 langues)."""
    lang = normalize_language(meta.get("language") or language)
    labels = get_editorial_labels(lang)

    author = meta.get("author", "L'Auteur")
    bio = meta.get("author_bio", "")
    bonus = meta.get("bonus_resource", {})
    t = meta.get("title", "ce livre")
    ed = meta.get("edition_details", {})

    md = []

    # 1. Conclusion / Mot de la fin
    md.append(
        f"<div class=\"page-break\"></div>\n\n"
        f"## {labels.get('conclusion', 'Conclusion')}\n\n"
        f"{'Le savoir sans exécution n\'est qu\'un voeu pieux. Vous disposez désormais de tous les leviers nécessaires pour réussir.' if lang == 'fr' else 'Knowledge without execution is merely wishful thinking. You now have every operational lever needed to succeed.' if lang == 'en' else 'El conocimiento sin ejecución no es más que una ilusión. Ahora tiene todas las herramientas necesarias para triunfar.' if lang == 'es' else 'Wissen ohne Umsetzung ist nur ein frommer Wunsch. Sie haben nun alle Hebel in der Hand.' if lang == 'de' else 'المعرفة دون تطبيق لا تتعدى التمني. باتت بين يديك كل الأدوات اللازمة للنجاح.'}\n\n"
    )

    # 2. Ressources offertes
    bonus_title = labels.get('bonus_title', 'Votre Pack de Ressources Offert')
    if "Pack de Ressources" not in bonus_title:
        bonus_title = f"{bonus_title} (Pack de Ressources)"
    md.append(
        f"## 🎁 {bonus_title}\n\n"
        f"Pour prolonger votre progression avec **{t}**, téléchargez vos fiches pratiques :  \n"
        f"<{bonus.get('url', 'https://markeddy.com')}>\n\n"
    )

    # 3. Demande d'avis Amazon
    review_title = labels.get("review_request_title", "Votre Avis Compte Énormément")
    if "Votre Avis Compte" not in review_title:
        review_title = f"{review_title} — Votre Avis Compte"
    review_text = labels.get("review_request_text", "Si cet ouvrage vous a été utile, prenez 60 secondes pour laisser une évaluation honnête sur Amazon.")
    md.append(
        f"## ⭐️ {review_title}\n\n"
        f"{review_text}\n\n"
    )

    # 4. À propos de l'auteur
    bio_title = labels.get("author_bio_title", "À Propos de l'Auteur")
    md.append(
        f"## {bio_title}\n\n"
        f"**{author}**  \n\n"
        f"{bio}\n\n"
    )

    # 5. Colophon
    colophon_text = labels.get("colophon", "ACHEVÉ D'IMPRIMER pour le compte d'Amazon Distribution KDP.")
    if "ACHEVÉ D'IMPRIMER" not in colophon_text:
        colophon_text = f"ACHEVÉ D'IMPRIMER — {colophon_text}"
    md.append(
        f"---\n\n"
        f"*{colophon_text}*\n"
    )

    return "\n".join(md)


# ==============================================================================
# 2. GÉNÉRATION EN HTML SÉMANTIQUE PRINT-READY (AVEC CLASSES CSS D'ÉDITION)
# ==============================================================================

def generate_front_matter_html(meta: Dict[str, Any], language: str = "fr") -> str:
    """Génère le Front-Matter au format HTML print-ready prêt pour Paged Media (5 langues)."""
    lang = normalize_language(meta.get("language") or language)
    labels = get_editorial_labels(lang)

    t = meta.get("title", "LIVRE KDP")
    st = meta.get("subtitle", "")
    author = meta.get("author", "Auteur")
    pub = meta.get("publisher", labels.get("publisher", "Éditions MarkEddy"))
    year = meta.get("year", 2026)
    isbn = meta.get("isbn", "979-8-0000-0000-0")
    disc = meta.get("disclaimer") or labels.get("disclaimer_text", "")
    ded = meta.get("dedication", "")
    epi = meta.get("epigraph", {})

    rtl_dir = ' dir="rtl"' if is_rtl(lang) else ''

    return f"""
    <!-- FRONT-MATTER 1 : FAUX-TITRE -->
    <section class="front-matter half-title-page"{rtl_dir}>
      <div class="half-title-content">
        <h1 class="bastard-title">{t}</h1>
      </div>
    </section>

    <!-- FRONT-MATTER 2 : PAGE DE GRAND TITRE -->
    <section class="front-matter title-page"{rtl_dir}>
      <div class="title-page-container">
        <div class="title-header">
          <h1 class="main-book-title">{t}</h1>
          {f'<h2 class="main-book-subtitle">{st}</h2>' if st else ''}
        </div>
        <div class="title-author-block">
          <p class="author-name">{author}</p>
        </div>
        <div class="title-publisher-block">
          <p class="publisher-imprint">{pub}</p>
        </div>
      </div>
    </section>

    <!-- FRONT-MATTER 3 : COPYRIGHT & MENTIONS LÉGALES -->
    <section class="front-matter copyright-page"{rtl_dir}>
      <div class="copyright-content">
        <p class="book-title-copy"><strong>{t}</strong></p>
        <p>© {year} {author}. {labels.get('copyright_notice', 'Tous droits réservés.')}</p>
        <p>{labels.get('publisher', 'Publié par')} <em>{pub}</em>.</p>
        <p class="isbn-number">ISBN : {isbn}</p>
        <p class="copyright-notice">
          {labels.get('copyright_notice', 'Toute reproduction, enregistrement ou diffusion, totale ou partielle, sous quelque forme que ce soit, est strictement interdite sans autorisation écrite préalable de l\'éditeur.')}
        </p>
        <p class="disclaimer-text"><em>{disc}</em></p>
        <p class="edition-notice">{labels.get('legal_deposit', 'Dépôt légal')} : {year} — {labels.get('print_format', 'Format')} : KDP</p>
      </div>
    </section>

    <!-- FRONT-MATTER 4 : DÉDICACE -->
    {f'''<section class="front-matter dedication-page"{rtl_dir}>
      <div class="dedication-content">
        <p class="dedication-quote">« {ded} »</p>
      </div>
    </section>''' if ded else ''}

    <!-- FRONT-MATTER 5 : ÉPIGRAPHE -->
    {f'''<section class="front-matter epigraph-page"{rtl_dir}>
      <div class="epigraph-content">
        <blockquote class="epigraph-text">« {epi.get('quote', labels.get('epigraph_quote', ''))} »</blockquote>
        <p class="epigraph-author">— {epi.get('author', labels.get('epigraph_author', ''))}</p>
      </div>
    </section>''' if (epi and epi.get('quote')) else ''}

    <!-- FRONT-MATTER 6 : AVANT-PROPOS -->
    <section class="front-matter foreword-page"{rtl_dir}>
      <h2 class="foreword-title">{labels.get('foreword', 'Avant-Propos')}</h2>
      <p class="lead">{'Ce livre est un instrument de transformation opérationnelle, conçu sans concession pour éliminer toute théorie superflue.' if lang == 'fr' else 'This book is an operational transformation tool, engineered to eliminate all fluff and theory.' if lang == 'en' else 'Este libro es una herramienta de transformación operativa, diseñada para eliminar cualquier teoría superflua.' if lang == 'es' else 'Dieses Buch ist ein Instrument zur operativen Transformation, das auf jegliches Füllmaterial verzichtet.' if lang == 'de' else 'هذا الكتاب أداة تحول عملي دقيقة، صُممت للتخلص من كل حشو نظري.'}</p>
      <p>{'Chaque chapitre est structuré selon un rythme rigoureux : le principe fondamental, une étude de cas chiffrée, le piège classique à contourner et un plan d\'action immédiat réalisable sous 24 heures.' if lang == 'fr' else 'Each chapter follows a rigorous structure: core principle, quantified case study, common pitfall, and immediate 24-hour action protocol.' if lang == 'en' else 'Cada capítulo sigue una estructura rigurosa: principio fundamental, caso de estudio cuantificado, trampa común y protocolo de acción inmediata de 24 horas.' if lang == 'es' else 'Jedes Kapitel folgt einer strengen Struktur: Grundprinzip, quantifizierte Fallstudie, typische Falle und sofortiger 24-Stunden-Aktionsplan.' if lang == 'de' else 'يتبع كل فصل هيكلاً دقيقاً: المبدأ الأساسي، دراسة حالة رقمية، الفخ الشائع، وخطة عمل فورية خلال 24 ساعة.'}</p>
    </section>
    """


def generate_back_matter_html(meta: Dict[str, Any], language: str = "fr") -> str:
    """Génère le Back-Matter au format HTML print-ready (5 langues)."""
    lang = normalize_language(meta.get("language") or language)
    labels = get_editorial_labels(lang)

    author = meta.get("author", "Auteur")
    bio = meta.get("author_bio", "")
    bonus = meta.get("bonus_resource", {})
    t = meta.get("title", "ce livre")
    ed = meta.get("edition_details", {})
    year = meta.get("copyright_year") or meta.get("year") or datetime.now().year

    rtl_dir = ' dir="rtl"' if is_rtl(lang) else ''

    return f"""
    <!-- BACK-MATTER 1 : CONCLUSION -->
    <section class="back-matter conclusion-page"{rtl_dir}>
      <h2 class="back-section-title">{labels.get('conclusion', 'Conclusion : L\'Éloge de l\'Exécution')}</h2>
      <p class="lead">{'Le savoir ne produit aucun effet tant qu\'il n\'est pas incarné dans la pratique quotidienne.' if lang == 'fr' else 'Knowledge produces no outcome until executed in daily disciplined practice.' if lang == 'en' else 'El conocimiento no produce ningún efecto hasta que se plasma en la práctica diaria.' if lang == 'es' else 'Wissen entfaltet keine Wirkung, solange es nicht in die tägliche Praxis umgesetzt wird.' if lang == 'de' else 'لا تنتج المعرفة أي أثر ما لم تتجسد في الممارسة اليومية المنتظمة.'}</p>
      <p>{'Les outils sont désormais entre vos mains. Engagez-vous sur une première action dès aujourd\'hui pour sceller vos nouveaux acquis.' if lang == 'fr' else 'The levers are now in your hands. Commit to a single decisive action today to seal your transformation.' if lang == 'en' else 'Las herramientas están ahora en sus manos. Comprométase con una primera acción hoy mismo.' if lang == 'es' else 'Die Werkzeuge liegen nun in Ihren Händen. Beginnen Sie noch heute mit dem ersten Schritt.' if lang == 'de' else 'باتت الأدوات بين يديك الآن. اتخذ خطوتك الأولى اليوم لترسيخ مكتسباتك الجديدة.'}</p>
    </section>

    <!-- BACK-MATTER 2 : BONUS & RESSOURCES -->
    <section class="back-matter bonus-page"{rtl_dir}>
      <div class="bonus-box">
        <h2 class="bonus-title">🎁 {labels.get('bonus_title', 'Votre Espace Ressources Offert')}</h2>
        <p class="bonus-desc">{'Pour prolonger votre progression avec' if lang == 'fr' else 'To accelerate your mastery with' if lang == 'en' else 'Para continuar su avance con' if lang == 'es' else 'Um Ihren Fortschritt fortzusetzen mit' if lang == 'de' else 'لمواصلة تقدمك مع'} <strong>{t}</strong> :</p>
        <p class="bonus-url"><a href="{bonus.get('url', 'https://markeddy.com')}">{bonus.get('url', 'https://markeddy.com')}</a></p>
      </div>
    </section>

    <!-- BACK-MATTER 3 : DEMANDE BIENVEILLANTE D'AVIS AMAZON -->
    <section class="back-matter review-request-page"{rtl_dir}>
      <div class="review-card">
        <h2 class="review-title">⭐️ {labels.get('review_request_title', 'Votre Avis Fait Toute la Différence')}</h2>
        <p>{labels.get('review_request_text', 'Si cet ouvrage vous a été utile, pourriez-vous prendre deux minutes pour laisser une évaluation sincère sur Amazon ?')}</p>
        <p class="review-thanks">{'Merci chaleureusement pour votre confiance.' if lang == 'fr' else 'Thank you warmly for your trust.' if lang == 'en' else 'Muchas gracias por su confianza.' if lang == 'es' else 'Herzlichen Dank für Ihr Vertrauen.' if lang == 'de' else 'شكراً جزيلاً لثقتكم الكريمة.'}</p>
      </div>
    </section>

    <!-- BACK-MATTER 4 : À PROPOS DE L'AUTEUR -->
    <section class="back-matter about-author-page"{rtl_dir}>
      <h2 class="back-section-title">{labels.get('author_bio_title', 'À Propos de l\'Auteur')}</h2>
      <p class="author-heading"><strong>{author}</strong></p>
      <p class="author-biography">{bio}</p>
    </section>

    <!-- BACK-MATTER 5 : COLOPHON / ACHEVÉ D'IMPRIMER -->
    <section class="back-matter colophon-page"{rtl_dir}>
      <div class="colophon-content">
        <p class="colophon-header"><strong>{labels.get('colophon', 'ACHEVÉ D\'IMPRIMER')}</strong></p>
        <p>{ed.get('print_location', 'Amazon KDP Printing')}</p>
        <p>{ed.get('typography_notes', 'Mise en page certifiée Amazon KDP')}</p>
        <p>{labels.get('legal_deposit', 'Dépôt légal')} : {year}</p>
      </div>
    </section>
    """


def assemble_complete_book(
    body_content: str,
    metadata: Dict[str, Any],
    output_format: str = "markdown",
    language: str = "fr",
) -> str:
    """
    Assemble le manuscrit complet : Front-Matter + Manuscrit (Corps) + Back-Matter.
    Supporte les formats 'markdown' et 'html' ainsi que les 5 langues (EN, FR, ES, DE, AR).
    """
    lang = normalize_language(metadata.get("language") or language)
    is_coloring = "coloriage" in str(metadata.get("niche", "")).lower() or metadata.get("is_coloring", False)
    if output_format.lower() == "html":
        fm = generate_coloring_front_matter_html(metadata) if is_coloring else generate_front_matter_html(metadata, language=lang)
        bm = generate_coloring_back_matter_html(metadata) if is_coloring else generate_back_matter_html(metadata, language=lang)
        return f"{fm}\n\n<!-- BODY MATTER -->\n<main class=\"book-body\">\n{body_content}\n</main>\n\n{bm}"
    else:
        fm = generate_coloring_front_matter_markdown(metadata) if is_coloring else generate_front_matter_markdown(metadata, language=lang)
        bm = generate_coloring_back_matter_markdown(metadata) if is_coloring else generate_back_matter_markdown(metadata, language=lang)
        return f"{fm}\n\n{body_content}\n\n{bm}"


# ==============================================================================
# 3. STRUCTURE ÉDITORIALE SPÉCIFIQUE ENFANTS & COLORIAGE KDP
# ==============================================================================

def generate_coloring_front_matter_html(meta: Dict[str, Any]) -> str:
    """Génère le Front-Matter spécifique pour livre de coloriage enfants."""
    t = meta.get("title", "LIVRE DE COLORIAGE")
    st = meta.get("subtitle", "Planches d'art grand format pour enfants")
    author = meta.get("author", "Éditions MarkEddy")
    pub = meta.get("publisher", "MarkEddy Kids")
    year = meta.get("year", 2026)
    isbn = meta.get("isbn", "979-8-0000-0000-0")

    return f"""
    <!-- COLORIAGE FRONT-MATTER 1 : CE LIVRE APPARTIENT À -->
    <section class="front-matter belongs-to-page">
      <h1 class="belongs-to-title">🌟 Ce livre appartient à :</h1>
      <div style="font-size: 16pt; margin: 30pt 0 10pt 0; text-align: left; max-width: 70%; margin-left: auto; margin-right: auto;">
        <p><strong>Prénom :</strong> ____________________________________</p>
        <p style="margin-top: 25pt;"><strong>Âge :</strong> _______ ans</p>
        <p style="margin-top: 25pt;"><strong>Couleur préférée :</strong> _________________________</p>
        <p style="margin-top: 25pt;"><strong>Date de début :</strong> ____ / ____ / {year}</p>
      </div>
    </section>

    <!-- COLORIAGE FRONT-MATTER 2 : PAGE DE TITRE -->
    <section class="front-matter title-page" style="text-align: center; padding-top: 1.5in;">
      <h1 style="font-family: var(--font-title, 'Baloo 2', cursive); font-size: 32pt; color: #0f172a; margin-bottom: 0.2em;">{t}</h1>
      <h2 style="font-family: var(--font-subtitle, 'Nunito', sans-serif); font-size: 16pt; color: #475569; margin-bottom: 1.5in;">{st}</h2>
      <p style="font-size: 14pt; font-weight: bold; color: #1e293b;">{author}</p>
      <p style="font-size: 11pt; color: #64748b; margin-top: 0.5in;">{pub}</p>
    </section>

    <!-- COLORIAGE FRONT-MATTER 3 : COPYRIGHT & CONSEILS AUX PARENTS -->
    <section class="front-matter copyright-page" style="font-size: 9pt; color: #475569; padding-top: 2in;">
      <p><strong>{t}</strong></p>
      <p>© {year} {author}. Tous droits réservés.</p>
      <p>Publié par <em>{pub}</em>.</p>
      <p>ISBN : {isbn}</p>
      <p style="margin-top: 20pt; border: 1pt dashed #cbd5e1; padding: 12pt; border-radius: 8pt; background: #f8fafc;">
        🖍️ <strong>Conseil aux Artistes et aux Parents :</strong><br>
        Chaque illustration est imprimée uniquement sur le recto, avec une page verso blanche anti-bavure.
        Si vous utilisez des feutres très liquides ou à alcool, nous vous conseillons de glisser une feuille
        blanche supplémentaire sous la page pour une protection absolue.
      </p>
      <p style="margin-top: 20pt;">Première édition : {year} — Imprimé par Amazon KDP.</p>
    </section>

    <!-- COLORIAGE FRONT-MATTER 4 : TEST DE COULEURS -->
    <section class="front-matter color-test-page">
      <h2 class="color-test-title">🎨 Mon Nuancier de Feutres & Crayons</h2>
      <p style="font-size: 11pt; color: #64748b; margin-bottom: 30pt;">Essaie toutes tes couleurs ici avant de colorier tes dessins !</p>
      <div class="color-test-grid">
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
        <div class="color-test-circle"></div>
      </div>
    </section>
    """


def generate_coloring_back_matter_html(meta: Dict[str, Any]) -> str:
    """Génère le Back-Matter spécifique pour livre de coloriage (Diplôme d'artiste + Avis)."""
    t = meta.get("title", "ce livre de coloriage")
    author = meta.get("author", "MarkEddy")

    return f"""
    <!-- COLORIAGE BACK-MATTER 1 : DIPLÔME DU SUPER ARTISTE -->
    <section class="back-matter diploma-page">
      <div style="border: 3pt solid #0f172a; padding: 25pt; border-radius: 12pt; background: #ffffff;">
        <h1 class="diploma-title">🏆 DIPLÔME OFFICIEL 🏆</h1>
        <h2 style="font-size: 18pt; color: #d4af37; margin-bottom: 20pt;">DU SUPER ARTISTE EN HERBE</h2>
        <p style="font-size: 14pt; margin: 20pt 0;">Ce certificat d'excellence est décerné avec fierté à :</p>
        <p style="font-size: 20pt; font-weight: bold; border-bottom: 2pt solid #0f172a; display: inline-block; min-width: 60%; margin: 15pt 0;">&nbsp;</p>
        <p style="font-size: 13pt; line-height: 1.6; margin: 20pt 0;">
          Pour avoir colorié avec patience, créativité et imagination<br>
          l'intégralité de l'album <strong>{t}</strong> !
        </p>
        <div style="margin-top: 40pt; display: flex; justify-content: space-around; font-size: 12pt;">
          <div>
            <p><strong>Date :</strong> ____ / ____ / ________</p>
          </div>
          <div>
            <p><strong>Signature du Grand Artiste :</strong></p>
            <p style="border-bottom: 1.5pt solid #94a3b8; width: 140pt; margin: 10pt auto 0 auto;">&nbsp;</p>
          </div>
        </div>
      </div>
    </section>

    <!-- COLORIAGE BACK-MATTER 2 : MOT POUR LES PARENTS -->
    <section class="back-matter review-request-page" style="text-align: center; padding-top: 1.5in;">
      <div style="max-width: 80%; margin: 0 auto; border: 1pt solid #e2e8f0; padding: 25pt; border-radius: 10pt; background: #f8fafc;">
        <h2 style="font-size: 18pt; color: #0f172a; margin-bottom: 10pt;">⭐️ Chers Parents, Votre Avis Est Précieux !</h2>
        <p style="font-size: 11pt; line-height: 1.6; color: #475569; margin-bottom: 15pt;">
          Nous espérons de tout cœur que votre enfant a passé des heures merveilleuses et créatives à donner vie à ces dessins.
        </p>
        <p style="font-size: 11pt; line-height: 1.6; color: #475569; margin-bottom: 15pt;">
          Si cet album vous a plu, pourriez-vous prendre <strong>une minute pour déposer un commentaire sur Amazon</strong> ?
          Votre soutien permet à notre petite équipe indépendante de continuer à créer de beaux livres pour nos enfants.
        </p>
        <p style="font-size: 12pt; font-weight: bold; color: #a16207;">Merci infiniment pour votre confiance !</p>
      </div>
    </section>
    """


def generate_coloring_front_matter_markdown(meta: Dict[str, Any]) -> str:
    """Génère le Front-Matter coloriage au format Markdown."""
    t = meta.get("title", "LIVRE DE COLORIAGE")
    author = meta.get("author", "Auteur")
    pub = meta.get("publisher", "Éditeur")
    year = meta.get("year", 2026)
    isbn = meta.get("isbn", "979-8-0000-0000-0")

    return (
        f"# 🌟 CE LIVRE APPARTIENT À :\n\n"
        f"**Prénom :** ____________________________________  \n"
        f"**Âge :** _______ ans  \n"
        f"**Date :** ____ / ____ / {year}  \n\n"
        f"<div class=\"page-break\"></div>\n\n"
        f"# {t}\n\n"
        f"**{author}** — *{pub}*\n\n"
        f"<div class=\"page-break\"></div>\n\n"
        f"© {year} {author}. ISBN : {isbn}.  \n"
        f"🖍️ *Chaque illustration est imprimée au recto avec un verso blanc anti-bavure.*\n\n"
        f"<div class=\"page-break\"></div>\n\n"
        f"## 🎨 Mon Nuancier de Feutres & Crayons\n\n"
        f"*(Teste tes couleurs ici !)*\n\n"
        f"<div class=\"page-break\"></div>\n"
    )


def generate_coloring_back_matter_markdown(meta: Dict[str, Any]) -> str:
    """Génère le Back-Matter coloriage au format Markdown."""
    t = meta.get("title", "ce livre")
    return (
        f"<div class=\"page-break\"></div>\n\n"
        f"# 🏆 DIPLÔME DU SUPER ARTISTE 🏆\n\n"
        f"Décerné à : ____________________________________  \n"
        f"Pour avoir colorié avec brio l'intégralité de **{t}** !\n\n"
        f"<div class=\"page-break\"></div>\n\n"
        f"## ⭐️ Chers Parents, Votre Avis Est Précieux !\n\n"
        f"Si votre enfant a aimé ce livre, merci de laisser une évaluation sur Amazon pour encourager nos artistes !\n"
    )


__all__ = [
    "get_default_editorial_metadata",
    "generate_front_matter_markdown",
    "generate_back_matter_markdown",
    "generate_front_matter_html",
    "generate_back_matter_html",
    "generate_coloring_front_matter_html",
    "generate_coloring_back_matter_html",
    "generate_coloring_front_matter_markdown",
    "generate_coloring_back_matter_markdown",
    "assemble_complete_book",
]
