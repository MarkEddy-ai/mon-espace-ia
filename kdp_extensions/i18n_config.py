# -*- coding: utf-8 -*-
"""
kdp_extensions/i18n_config.py — Registre central d'internationalisation KDP (5 langues).

Ce module centralise les règles éditoriales, typographiques, prépresse et SEO
pour les 5 langues majeures d'Amazon KDP :
1. Français (FR) — Marché Amazon.fr / Amazon.ca
2. Anglais (EN) — Marché Amazon.com / Amazon.co.uk
3. Espagnol (ES) — Marché Amazon.es / Amazon.com.mx
4. Allemand (DE) — Marché Amazon.de
5. Arabe (AR) — Marché Amazon.sa / Amazon.ae (avec gestion RTL & alerte KDP Paperback)

Fournit :
- Métadonnées complètes par langue (direction, marché, monnaie, césures)
- Recommandations de Google Fonts adaptées
- Banques de mots et alphabets pour générateurs de puzzles et activités
- Libellés éditoriaux natifs pour le Front-Matter et Back-Matter
- Dictionnaire de mots interdits par les TOS Amazon KDP selon le marché
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

SUPPORTED_LANGUAGES: Tuple[str, ...] = ("en", "fr", "es", "de", "ar")

LANGUAGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "fr": {
        "code": "fr",
        "name": "French",
        "native_name": "Français",
        "direction": "ltr",
        "is_rtl": False,
        "default_font_pairing": "LUXURY_HERITAGE",
        "google_fonts": ["EB Garamond", "Cinzel", "Cinzel Decorative"],
        "hyphenation_lang": "fr",
        "amazon_marketplace": "amazon.fr",
        "marketplaces_supported": ["amazon.fr", "amazon.ca", "amazon.com", "amazon.be"],
        "currency": "€",
        "currency_code": "EUR",
        "word_banks": {
            "animaux": [
                "LION", "TIGRE", "ELEPHANT", "GIRAFE", "ZEBRE", "RENARD",
                "LAPIN", "OURS", "DAUPHIN", "AIGLE", "TORTUE", "HIBOU",
                "CHAMEAU", "PERROQUET", "ECUREUIL", "PANDA"
            ],
            "espace": [
                "ETOILE", "PLANETE", "FUSEE", "LUNE", "SOLEIL", "COMETE",
                "GALAXIE", "ORBITE", "ASTRE", "MARS", "SATURNE", "COSMOS",
                "METEORE", "ASTRONAUTE", "TELESCOPE", "NEBULEUSE"
            ],
            "ocean": [
                "BALEINE", "CORAIL", "REQUIN", "POULPE", "PHARE", "ANCRE",
                "VOILIER", "VAGUE", "CRABE", "MEDUSE", "PORT", "ILE",
                "COQUILLAGE", "HIPPOCAMPE", "SARDINE", "ROCHER"
            ],
            "voyage": [
                "VALISE", "CARTE", "BOUSSOLE", "SENTIER", "SOMMET", "VOYAGE",
                "HORIZON", "PASSEPORT", "EXCURSION", "CAMPING", "RIVIERE", "FORET"
            ],
            "general": [
                "AVENTURE", "ESPRIT", "LOGIQUE", "VICTOIRE", "MYSTERE", "ENIGME",
                "ASTUCE", "DEFI", "COURAGE", "CHEMIN", "ETAPE", "TALENT",
                "MEMOIRE", "REUSSITE", "DECOUVERTE", "SAVOIR"
            ]
        },
        "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        "forbidden_keywords": [
            "meilleur", "meilleurs", "bestseller", "best-seller", "gratuit", "free", "promo",
            "promotion", "pas cher", "n°1", "numéro 1", "solde", "vente"
        ],
        "editorial_labels": {
            "half_title": "Faux-Titre",
            "title_page": "Page de Titre",
            "by_author": "Par",
            "publisher": "Éditions MarkEddy & Cie",
            "imprint_sub": "Collection Haute Finance & Souveraineté Personnelle • Paris — Genève",
            "copyright_title": "Mentions Légales & Propriété Intellectuelle",
            "copyright_notice": "Tous droits de traduction, d'adaptation et de reproduction réservés pour tous pays.",
            "disclaimer_title": "Avertissement de Non-Responsabilité Financière & Fiscale",
            "disclaimer_text": (
                "Cet ouvrage est publié à des fins strictement éducatives et méthodologiques. "
                "Ni l'auteur ni l'éditeur ne sont agréés en qualité de Conseillers en Investissements "
                "Financiers (CIF). Tout investissement comporte un risque inhérent de perte en capital."
            ),
            "legal_deposit": "Dépôt légal",
            "print_format": "Format d'édition : 6 × 9 pouces (15,24 × 22,86 cm) • Papier 90 g/m²",
            "dedication_title": "Dédicace",
            "epigraph_author": "Warren Buffett",
            "epigraph_quote": "Quelqu'un est assis à l'ombre aujourd'hui parce que quelqu'un d'autre a planté un arbre il y a très longtemps.",
            "toc_title": "Table des Matières Exécutive",
            "chapter_label": "PILIER",
            "action_protocol": "PROTOCOLE D'ACTION IMMÉDIATE (24 HEURES)",
            "case_study": "Étude de Cas Chiffrée",
            "pitfall": "Le Piège Fréquent & Contre-Mesure",
            "author_bio_title": "À Propos de l'Auteur",
            "author_title_tag": "REPÈRES D'AUTORITÉ",
            "review_request_title": "Votre Avis Est Le Carburant De L'Indépendance",
            "review_request_text": "Si cet ouvrage vous a apporté de la valeur, prenez 60 secondes pour déposer une note et un avis sur Amazon.",
            "colophon": "Achevé d'imprimer pour le compte d'Amazon Distribution KDP.",
            "puzzle_title": "MOTS MÊLÉS THÉMATIQUES",
            "puzzle_solutions": "SOLUTIONS DES GRILLES",
            "this_book_belongs_to": "Ce livre appartient à :",
            "color_test": "Nuancier & Test de Couleurs",
            "super_artist_diploma": "Diplôme Officiel du Super Artiste",
            "maze_start": "Entrée",
            "maze_exit": "Sortie",
            "answer_key": "Solutions & Corrigés",
            "puzzle_scramble": "Mots Mélangés",
            "puzzle_ladder": "Échelle de Mots",
            "puzzle_riddles": "Devinettes",
            "puzzle_cryptogram": "Code Secret",
            "puzzle_maze": "Labyrinthe",
            "puzzle_dots": "Points à Relier",
            "puzzle_logic": "Grille Logique"
        },
        "paperback_warning": None
    },

    "en": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "direction": "ltr",
        "is_rtl": False,
        "default_font_pairing": "CLASSIC_EDITORIAL",
        "google_fonts": ["Libre Baskerville", "Playfair Display", "Cinzel"],
        "hyphenation_lang": "en-us",
        "amazon_marketplace": "amazon.com",
        "marketplaces_supported": ["amazon.com", "amazon.co.uk", "amazon.ca", "amazon.com.au"],
        "currency": "$",
        "currency_code": "USD",
        "word_banks": {
            "animaux": [
                "LION", "TIGER", "ELEPHANT", "GIRAFFE", "ZEBRA", "FOX",
                "RABBIT", "BEAR", "DOLPHIN", "EAGLE", "TURTLE", "OWL",
                "CAMEL", "PARROT", "SQUIRREL", "PANDA"
            ],
            "espace": [
                "STAR", "PLANET", "ROCKET", "MOON", "SUN", "COMET",
                "GALAXY", "ORBIT", "MARS", "SATURN", "COSMOS", "METEOR",
                "ASTRONAUT", "TELESCOPE", "NEBULA", "GRAVITY"
            ],
            "ocean": [
                "WHALE", "CORAL", "SHARK", "OCTOPUS", "BEACON", "ANCHOR",
                "SAILBOAT", "WAVE", "CRAB", "JELLYFISH", "HARBOR", "ISLAND",
                "SEASHELL", "SEAHORSE", "DOLPHIN", "REEF"
            ],
            "voyage": [
                "SUITCASE", "MAP", "COMPASS", "TRAIL", "SUMMIT", "JOURNEY",
                "HORIZON", "PASSPORT", "HIKING", "CAMPING", "RIVER", "FOREST"
            ],
            "general": [
                "ADVENTURE", "WISDOM", "LOGIC", "VICTORY", "MYSTERY", "RIDDLE",
                "SKILL", "COURAGE", "PATH", "TALENT", "MEMORY", "DISCOVERY"
            ]
        },
        "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        "forbidden_keywords": [
            "bestseller", "best seller", "free", "cheap", "sale",
            "discount", "promo", "promotion", "number 1", "#1", "top rated"
        ],
        "editorial_labels": {
            "half_title": "Half-Title",
            "title_page": "Title Page",
            "by_author": "By",
            "publisher": "MarkEddy Publishing House",
            "imprint_sub": "High Finance & Personal Sovereignty Collection • New York — London",
            "copyright_title": "Legal Notice & Intellectual Property",
            "copyright_notice": "All rights reserved. No part of this publication may be reproduced without prior written permission.",
            "disclaimer_title": "Financial & Tax Disclaimer",
            "disclaimer_text": (
                "This publication is designed for educational and informational purposes only. "
                "Neither the author nor publisher is a licensed Financial Advisor (RIA/SEC). "
                "Investing involves significant risks, including potential loss of principal."
            ),
            "legal_deposit": "Copyright Registration",
            "print_format": "Edition Format: 6 × 9 inches (15.24 × 22.86 cm) • Acid-Free Paper 90 gsm",
            "dedication_title": "Dedication",
            "epigraph_author": "Warren Buffett",
            "epigraph_quote": "Someone is sitting in the shade today because someone planted a tree a long time ago.",
            "toc_title": "Executive Table of Contents",
            "chapter_label": "PILLAR",
            "action_protocol": "IMMEDIATE ACTION PROTOCOL (24 HOURS)",
            "case_study": "Detailed Case Study & Financial Model",
            "pitfall": "Common Pitfall & Counter-Strategy",
            "author_bio_title": "About the Author",
            "author_title_tag": "AUTHORITY BENCHMARK",
            "review_request_title": "Your Honest Review Fuels Independent Authors",
            "review_request_text": "If this guide delivered actionable clarity, please take 60 seconds to leave an honest review on Amazon.",
            "colophon": "Printed and bound by Amazon KDP Distribution.",
            "puzzle_title": "WORD SEARCH PUZZLES",
            "puzzle_solutions": "PUZZLE SOLUTIONS",
            "this_book_belongs_to": "This book belongs to:",
            "color_test": "Color Palette & Swatch Test",
            "super_artist_diploma": "Official Super Artist Certificate",
            "maze_start": "Start",
            "maze_exit": "Finish",
            "answer_key": "Answer Key & Solutions",
            "puzzle_scramble": "Word Scramble",
            "puzzle_ladder": "Word Ladder",
            "puzzle_riddles": "Riddles",
            "puzzle_cryptogram": "Secret Code",
            "puzzle_maze": "Maze",
            "puzzle_dots": "Connect the Dots",
            "puzzle_logic": "Logic Grid"
        },
        "paperback_warning": None
    },

    "es": {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "direction": "ltr",
        "is_rtl": False,
        "default_font_pairing": "MODERN_LITERARY",
        "google_fonts": ["Lora", "Playfair Display", "Merriweather"],
        "hyphenation_lang": "es",
        "amazon_marketplace": "amazon.es",
        "marketplaces_supported": ["amazon.es", "amazon.com.mx", "amazon.com"],
        "currency": "€",
        "currency_code": "EUR",
        "word_banks": {
            "animaux": [
                "LEON", "TIGRE", "ELEFANTE", "JIRAFA", "CEBRA", "ZORRO",
                "CONEJO", "OSO", "DELFIN", "AGUILA", "TORTUGA", "BUHO",
                "CAMELLO", "LORO", "ARDILLA", "PANDA"
            ],
            "espace": [
                "ESTRELLA", "PLANETA", "COHETE", "LUNA", "SOL", "COMETA",
                "GALAXIA", "ORBITA", "MARTE", "SATURNO", "COSMOS", "METEORO",
                "ASTRONAUTA", "TELESCOPIO", "NEBULOSA", "GRAVEDAD"
            ],
            "ocean": [
                "BALLENA", "CORAL", "TIBURON", "PULPO", "FARO", "ANCLA",
                "VELERO", "OLA", "CANGREJO", "MEDUSA", "PUERTO", "ISLA",
                "CONCHA", "CABALLITO", "ARRECIFE", "DELFIN"
            ],
            "voyage": [
                "MALETA", "MAPA", "BRUJULA", "SENDERO", "CUMBRE", "VIAJE",
                "HORIZONTE", "PASAPORTE", "EXCURSION", "CAMPING", "RIO", "BOSQUE"
            ],
            "general": [
                "AVENTURA", "SABIDURIA", "LOGICA", "VICTORIA", "MISTERIO",
                "ENIGMA", "DESTREZA", "VALOR", "CAMINO", "TALENTO", "MEMORIA"
            ]
        },
        "alphabet": list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"),
        "forbidden_keywords": [
            "bestseller", "superventas", "gratis", "barato", "oferta",
            "descuento", "promocion", "numero 1", "nº 1", "mejor vendido"
        ],
        "editorial_labels": {
            "half_title": "Portadilla",
            "title_page": "Portada Interior",
            "by_author": "Por",
            "publisher": "Ediciones MarkEddy & Cía",
            "imprint_sub": "Colección Alta Finanza y Soberanía Personal • Madrid — México",
            "copyright_title": "Aviso Legal & Propiedad Intelectual",
            "copyright_notice": "Todos los derechos reservados. Prohibida la reproducción total o parcial sin autorización.",
            "disclaimer_title": "Descargo de Responsabilidad Financiera y Fiscal",
            "disclaimer_text": (
                "Esta publicación tiene fines estrictamente formativos e informativos. "
                "Ni el autor ni la editorial actúan como Asesores Financieros Autorizados (CNMV). "
                "Toda inversión conlleva un riesgo inherente de pérdida del capital."
            ),
            "legal_deposit": "Depósito Legal",
            "print_format": "Formato: 6 × 9 pulgadas (15,24 × 22,86 cm) • Papel de 90 g/m² libre de ácido",
            "dedication_title": "Dedicatoria",
            "epigraph_author": "Warren Buffett",
            "epigraph_quote": "Alguien se sienta hoy a la sombra porque alguien plantó un árbol hace mucho tiempo.",
            "toc_title": "Índice de Contenidos Ejecutivo",
            "chapter_label": "PILAR",
            "action_protocol": "PROTOCOLO DE ACCIÓN INMEDIATA (24 HORAS)",
            "case_study": "Estudio de Caso Numérico y Modelado",
            "pitfall": "Error Frecuente & Estrategia Defensiva",
            "author_bio_title": "Sobre el Autor",
            "author_title_tag": "REFERENTES DE AUTORIDAD",
            "review_request_title": "Su Opinión Honesta Impulsa la Libertad Financiera",
            "review_request_text": "Si este libro le ha aportado valor, dedique 60 segundos a dejar una valoración sincera en Amazon.",
            "colophon": "Impreso bajo demanda por Amazon Distribution KDP.",
            "puzzle_title": "SOPA DE LETRAS TEMÁTICA",
            "puzzle_solutions": "SOLUCIONES DE LAS SOPAS",
            "this_book_belongs_to": "Este libro pertenece a:",
            "color_test": "Paleta de Colores & Test de Prueba",
            "super_artist_diploma": "Diploma Oficial del Súper Artista",
            "maze_start": "Entrada",
            "maze_exit": "Salida",
            "answer_key": "Soluciones y Respuestas",
            "puzzle_scramble": "Palabras Revueltas",
            "puzzle_ladder": "Escalera de Palabras",
            "puzzle_riddles": "Adivinanzas",
            "puzzle_cryptogram": "Código Secreto",
            "puzzle_maze": "Laberinto",
            "puzzle_dots": "Unir los Puntos",
            "puzzle_logic": "Cuadrícula Lógica"
        },
        "paperback_warning": None
    },

    "de": {
        "code": "de",
        "name": "German",
        "native_name": "Deutsch",
        "direction": "ltr",
        "is_rtl": False,
        "default_font_pairing": "GERMANIC_PRECISION",
        "google_fonts": ["EB Garamond", "Noto Serif", "Cinzel"],
        "hyphenation_lang": "de-1996",
        "amazon_marketplace": "amazon.de",
        "marketplaces_supported": ["amazon.de", "amazon.at"],
        "currency": "€",
        "currency_code": "EUR",
        "word_banks": {
            "animaux": [
                "LOEWE", "TIGER", "ELEFANT", "GIRAFFE", "ZEBRA", "FUCHS",
                "HASE", "BAER", "DELFIN", "ADLER", "SCHILDKROETE", "EULE",
                "KAMEL", "PAPAGEI", "EICHHOERNCHEN", "PANDA"
            ],
            "espace": [
                "STERN", "PLANET", "RAKETE", "MOND", "SONNE", "KOMET",
                "GALAXIE", "ORBIT", "MARS", "SATURN", "KOSMOS", "METEOR",
                "ASTRONAUT", "TELESKOP", "NEBEL", "SCHWERKRAFT"
            ],
            "ocean": [
                "WALFISCH", "KORALLE", "HAI", "KRAKE", "LEUCHTTURM", "ANKER",
                "SEGELBOOT", "WELLE", "KRABBE", "QUALLE", "HAFEN", "INSEL",
                "MUSCHEL", "SEEFERDCHEN", "RIFF", "MEER"
            ],
            "voyage": [
                "KOFFER", "KARTE", "KOMPASS", "PFAD", "GIPFEL", "REISE",
                "HORIZONT", "REISEPASS", "WANDERUNG", "CAMPING", "FLUSS", "WALD"
            ],
            "general": [
                "ABENTEUER", "WEISHEIT", "LOGIK", "SIEG", "GEHEIMNIS",
                "RAETSEL", "MUT", "WEG", "TALENT", "GEDAECHTNIS", "ERFOLG"
            ]
        },
        "alphabet": list("ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß"),
        "forbidden_keywords": [
            "bestseller", "best-seller", "kostenlos", "gratis", "billig",
            "angebot", "rabatt", "nr 1", "nummer 1", "spitzenreiter"
        ],
        "editorial_labels": {
            "half_title": "Schmutztitel",
            "title_page": "Haupttitel",
            "by_author": "Von",
            "publisher": "MarkEddy Verlag",
            "imprint_sub": "Sammlung Hohe Finanzen & Persönliche Souveränität • Frankfurt — Zürich",
            "copyright_title": "Impressum & Urheberrecht",
            "copyright_notice": "Alle Rechte vorbehalten. Nachdruck, Übersetzung und Vervielfältigung nur mit Genehmigung.",
            "disclaimer_title": "Haftungsausschluss (Finanzen & Steuern)",
            "disclaimer_text": (
                "Dieses Werk dient ausschließlich Informations- und Bildungszwecken. "
                "Weder Autor noch Verlag sind zugelassene Anlageberater (BaFin). "
                "Jede Kapitalanlage birgt das Risiko finanzieller Verluste."
            ),
            "legal_deposit": "Bibliografische Information",
            "print_format": "Buchformat: 6 × 9 Zoll (15,24 × 22,86 cm) • Säurefreies Werkdruckpapier 90 g/m²",
            "dedication_title": "Widmung",
            "epigraph_author": "Johann Wolfgang von Goethe",
            "epigraph_quote": "Es ist nicht genug zu wissen, man muss auch anwenden; es ist nicht genug zu wollen, man muss auch tun.",
            "toc_title": "Inhaltsverzeichnis",
            "chapter_label": "SÄULE",
            "action_protocol": "SOFORT-AKTIONSPLAN (24 STUNDEN)",
            "case_study": "Geprüfte Fallstudie & Finanzmodellierung",
            "pitfall": "Häufige Falle & Gegenmaßnahme",
            "author_bio_title": "Über den Autor",
            "author_title_tag": "AUTORITÄTSNACHWEIS",
            "review_request_title": "Ihre ehrliche Rezension stärkt unabhängiges Wissen",
            "review_request_text": "Wenn dieses Werk Ihnen geholfen hat, nehmen Sie sich bitte 60 Sekunden für eine Amazon-Rezension.",
            "colophon": "Gedruckt und gebunden im KDP-Verfahren durch Amazon Distribution.",
            "puzzle_title": "THEMATISCHE WORTSUCHE",
            "puzzle_solutions": "LÖSUNGEN DER WORTSUCHE",
            "this_book_belongs_to": "Dieses Buch gehört:",
            "color_test": "Farbpalette & Farbtest",
            "super_artist_diploma": "Offizielle Urkunde für den Super-Künstler",
            "maze_start": "Start",
            "maze_exit": "Ziel",
            "answer_key": "Lösungen & Antwortschlüssel",
            "puzzle_scramble": "Wortsalat & Buchstabensalat",
            "puzzle_ladder": "Wortleiter",
            "puzzle_riddles": "Rätsel",
            "puzzle_cryptogram": "Geheimcode",
            "puzzle_maze": "Labyrinth",
            "puzzle_dots": "Punkte Verbinden",
            "puzzle_logic": "Logik-Gitter"
        },
        "paperback_warning": None
    },

    "ar": {
        "code": "ar",
        "name": "Arabic",
        "native_name": "العربية",
        "direction": "rtl",
        "is_rtl": True,
        "default_font_pairing": "ARABIC_MAJESTIC",
        "google_fonts": ["Cairo", "Tajawal", "Amiri", "Noto Naskh Arabic"],
        "hyphenation_lang": "none",
        "amazon_marketplace": "amazon.sa",
        "marketplaces_supported": ["amazon.sa", "amazon.ae", "amazon.com"],
        "currency": "ر.س",
        "currency_code": "SAR",
        "word_banks": {
            "animaux": [
                "اسد", "نمر", "فيل", "زرافة", "حمار_وحشي", "ثعلب",
                "ارنب", "دب", "دلفين", "نسر", "سلحفاة", "بومة",
                "جمل", "ببغاء", "سنجاب", "باندا"
            ],
            "espace": [
                "نجم", "كوكب", "صاروخ", "قمر", "شمس", "مذنب",
                "مجرة", "مدار", "مريخ", "زحل", "كون", "شهاب",
                "رائد_فضاء", "تلسكوب", "سديم", "جاذبية"
            ],
            "ocean": [
                "حوت", "مرجان", "قرش", "اخطبوط", "منارة", "مرساة",
                "شراع", "موجة", "سلطعون", "قنديل", "ميناء", "جزيرة",
                "صدفة", "فرس_البحر", "شعب", "بحر"
            ],
            "voyage": [
                "حقيبة", "خريطة", "بوصلة", "مسار", "قمة", "رحلة",
                "افق", "جواز", "استكشاف", "تخييم", "نهر", "غابة"
            ],
            "general": [
                "مغامرة", "حكمة", "منطق", "انتصار", "سر", "لغز",
                "شجاعة", "طريق", "موهبة", "ذاكرة", "نجاح", "معرفة"
            ]
        },
        "alphabet": [
            "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش",
            "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي"
        ],
        "forbidden_keywords": [
            "الاكثر مبيعا", "الأكثر مبيعاً", "مجاني", "مجانا", "رخيص",
            "عرض", "تخفيض", "خصم", "رقم 1", "الاول", "الأول"
        ],
        "editorial_labels": {
            "half_title": "صفحة العنوان التمهيدي",
            "title_page": "صفحة العنوان الرئيسي",
            "by_author": "تأليف",
            "publisher": "دار مارك إيدي للنشر والتوزيع",
            "imprint_sub": "سلسلة الهندسة المالية والسيادة الشخصية • الرياض — دبي",
            "copyright_title": "إشعار حقوق النشر والملكية الفكرية",
            "copyright_notice": "جميع الحقوق محفوظة. لا يجوز نسخ أو توزيع أي جزء من هذا الكتاب دون إذن خطي مسبق.",
            "disclaimer_title": "إخلاء المسؤولية المالية والاستثمارية",
            "disclaimer_text": (
                "تم إعداد هذا الكتاب لأغراض تعليمية وإرشادية عامة فقط. "
                "لا يُعتبر المؤلف أو الناشر مستشاراً مالياً مرخصاً. "
                "تتضمن كافة الاستثمارات والأنشطة المالية مخاطر قد تؤدي إلى خسارة جزء أو كل رأس المال."
            ),
            "legal_deposit": "رقم الإيداع القانوني",
            "print_format": "المقاس: 6 × 9 بوصة (15.24 × 22.86 سم) • ورق فاخر خالي من الأحماض 90 جم/م²",
            "dedication_title": "الإهداء",
            "epigraph_author": "ابن خلدون",
            "epigraph_quote": "المال إذا لم يُدبر بالعلم أسرع في الزوال من السحاب في الصيف.",
            "toc_title": "جدول المحتويات التنفيذي",
            "chapter_label": "الركيزة",
            "action_protocol": "بروتوكول التنفيذ الفوري (خلال 24 ساعة)",
            "case_study": "دراسة حالة تطبيقية ونمذجة مالية",
            "pitfall": "المطب الشائع واستراتيجية الحماية",
            "author_bio_title": "نبذة عن المؤلف",
            "author_title_tag": "معايير الموثوقية",
            "review_request_title": "رأيكم الصادق هو وقود المؤلفين المستقلين",
            "review_request_text": "إذا حقق لك هذا الكتاب فائدة عملية، يُرجى قضاء 60 ثانية لترك تقييم موضوعي على متجر أمازون.",
            "colophon": "تمت الطباعة والتوزيع عبر نظام النشر الذاتي KDP على أمازون.",
            "puzzle_title": "شبكة البحث عن الكلمات",
            "puzzle_solutions": "حلول شبكات البحث",
            "this_book_belongs_to": "هذا الكتاب ملك لـ:",
            "color_test": "لوحة الألوان واختبار التدرجات",
            "super_artist_diploma": "شهادة الفنان المبدع الرسمية",
            "maze_start": "البداية",
            "maze_exit": "النهاية",
            "answer_key": "دليل الحلول والإجابات",
            "puzzle_scramble": "الكلمات المبعثرة",
            "puzzle_ladder": "سلم الكلمات",
            "puzzle_riddles": "ألغاز وفوازير",
            "puzzle_cryptogram": "الشفرة السرية",
            "puzzle_maze": "المتاهة",
            "puzzle_dots": "توصيل النقاط",
            "puzzle_logic": "شبكة المنطق"
        },
        "paperback_warning": (
            "⚠️ تنبيه KDP للغة العربية (Paperback Warning): تدعم منصة Amazon KDP الكتب الإلكترونية (Kindle eBook) "
            "باللغة العربية بشكل كامل. بالنسبة للكتب الورقية المطبوعة (Paperback)، تُطبق أمازون اشتراطات فنية خاصة "
            "وتدعم أسواقاً محددة (مثل Amazon.com). يُوصى بتضمين خطوط Amiri أو Cairo بشكل كامل في ملف PDF المطبوع "
            "والتأكد من إعداد اتجاه القراءة من اليمين إلى اليسار (RTL) وانعكاس هامش التجليد (Gutter)."
        )
    }
}


def normalize_language(lang: Optional[str]) -> str:
    """Normalise un code de langue en minuscules avec repli par défaut sur 'fr'."""
    if not lang or not isinstance(lang, str):
        return "fr"
    clean = lang.strip().lower()
    if clean in SUPPORTED_LANGUAGES:
        return clean

    ALIASES = {
        "arabic": "ar", "arabe": "ar", "العربية": "ar",
        "english": "en", "anglais": "en",
        "spanish": "es", "espagnol": "es", "español": "es",
        "german": "de", "allemand": "de", "deutsch": "de",
        "french": "fr", "français": "fr", "francais": "fr",
    }
    if clean in ALIASES:
        return ALIASES[clean]

    # Gestion des codes locaux (ex: 'fr-FR' -> 'fr', 'en-US' -> 'en')
    short_code = clean.split("-")[0].split("_")[0]
    return short_code if short_code in SUPPORTED_LANGUAGES else "fr"


def get_language_config(lang: Optional[str] = "fr") -> Dict[str, Any]:
    """Retourne la configuration complète de la langue demandée."""
    code = normalize_language(lang)
    return LANGUAGE_CONFIGS[code]


def get_supported_languages() -> List[Dict[str, Any]]:
    """Retourne la liste descriptive des 5 langues pour les sélecteurs UI et API."""
    return [
        {
            "code": cfg["code"],
            "name": cfg["name"],
            "native_name": cfg["native_name"],
            "direction": cfg["direction"],
            "is_rtl": cfg["is_rtl"],
            "amazon_marketplace": cfg["amazon_marketplace"],
            "currency": cfg["currency"],
            "default_font_pairing": cfg["default_font_pairing"],
            "paperback_warning": cfg["paperback_warning"],
        }
        for cfg in LANGUAGE_CONFIGS.values()
    ]


def is_rtl(lang: Optional[str] = "fr") -> bool:
    """Vérifie si la langue s'écrit de droite à gauche (RTL)."""
    return get_language_config(lang)["is_rtl"]


def get_editorial_labels(lang: Optional[str] = "fr") -> Dict[str, str]:
    """Retourne le dictionnaire des étiquettes éditoriales traduites."""
    return get_language_config(lang)["editorial_labels"]


def get_puzzle_word_banks(lang: Optional[str] = "fr") -> Dict[str, List[str]]:
    """Retourne les banques de mots pour puzzles dans la langue."""
    return get_language_config(lang)["word_banks"]


def get_alphabet(lang: Optional[str] = "fr") -> List[str]:
    """Retourne l'alphabet valide pour la langue."""
    return get_language_config(lang)["alphabet"]


def get_forbidden_keywords(lang: Optional[str] = "fr") -> List[str]:
    """Retourne la liste des mots-clés proscrits par les TOS KDP."""
    return get_language_config(lang)["forbidden_keywords"]


def get_paperback_warning(lang: Optional[str] = "fr") -> Optional[str]:
    """Retourne l'alerte éventuelle liée au format Paperback pour la langue."""
    return get_language_config(lang)["paperback_warning"]


def get_language_profile(lang: Optional[str] = "fr") -> Dict[str, Any]:
    """Return a normalized language profile for KDP pipeline consumers.

    Keys:
      - direction: "ltr" | "rtl"
      - amazon_marketplace: primary marketplace code (e.g. amazon.fr)
      - google_fonts: list of recommended Google Fonts (includes Cairo/Tajawal/Amiri for ar)
      - editorial_strings: full Front/Back Matter editorial labels
      - puzzle_alphabet: alphabet list for puzzles/activities
      - word_banks: localized word banks
      - forbidden_kdp_terms: forbidden keywords list (TOS)
    """
    cfg = get_language_config(lang)
    code = cfg["code"]

    # puzzle_alphabet explicit rules per requirement
    if code == "es":
        puzzle_alphabet = list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ")
    elif code == "de":
        # include Ä, Ö, Ü (keep ß as in config for completeness)
        puzzle_alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß")
    elif code == "ar":
        # 28 Arabic letters as defined in config
        puzzle_alphabet = list(cfg.get("alphabet") or [])
    else:
        puzzle_alphabet = list(cfg.get("alphabet") or [])

    return {
        "code": code,
        "name": cfg.get("name"),
        "native_name": cfg.get("native_name"),
        "name_native": cfg.get("native_name"),
        "direction": cfg.get("direction", "ltr"),
        "is_rtl": bool(cfg.get("is_rtl", False)),
        "amazon_marketplace": cfg.get("amazon_marketplace"),
        "marketplaces_supported": list(cfg.get("marketplaces_supported") or []),
        "google_fonts": list(cfg.get("google_fonts") or []),
        "editorial_strings": dict(cfg.get("editorial_labels") or {}),
        "puzzle_alphabet": puzzle_alphabet,
        "word_banks": dict(cfg.get("word_banks") or {}),
        "forbidden_kdp_terms": list(cfg.get("forbidden_keywords") or []),
        "hyphenation_lang": cfg.get("hyphenation_lang"),
        "currency": cfg.get("currency"),
        "currency_code": cfg.get("currency_code"),
        "paperback_warning": cfg.get("paperback_warning"),
    }
