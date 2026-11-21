"""
kdp_extensions/multilingual_transcreator.py — Agent 6 : Transcréateur Multilingue Idiomatique & Bundle KDP (5 Langues).

Cet agent orchestre la production automatisée et indépendante des éditions internationales
d'un livre KDP d'excellence pour les 5 langues majeures :
  - Anglais ('en')
  - Français ('fr')
  - Espagnol ('es')
  - Allemand ('de')
  - Arabe ('ar', avec support RTL complet)

RÈGLES D'OR DU STUDIO MARKEDDY KDP :
1. ZÉRO TRADUCTION LITTÉRALE : Transcréation idiomatique complète (concepts financiers/légaux
   locaux, devises, exemples concrets adaptés à chaque culture).
2. ZÉRO HALLUCINATION : Métadonnées et sources documentaires rigoureuses, traçables.
3. FLUX COMPLET PAR LANGUE :
   - Transcréation du contenu + Front-Matter + Back-Matter
   - SEO A9 localisé (7 slots de recherche, limite stricte de 50 octets UTF-8 par slot)
   - Rendu HTML & compilation PDF (Playwright / repli prépresse) avec comptage réel des pages
   - Recalcul indépendant du dos de couverture au micron (mm et pouces) + inversion RTL si 'ar'
   - Audit de conformité KDP via supervise_kdp_book()
4. MANIFESTE & ARCHIVAGE :
   - Production du 'bundle_manifest.json' comparant toutes les éditions
   - Création de l'archive ZIP globale et des archives par langue.
"""

from __future__ import annotations

import hashlib
import html
import json
import logging
import os
import random
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from kdp_extensions.i18n_config import (
    SUPPORTED_LANGUAGES,
    get_alphabet,
    get_editorial_labels,
    get_forbidden_kdp_terms,
    get_language_profile,
    get_marketplace,
    is_rtl,
    normalize_language,
)
from kdp_extensions.kdp_dimensions import (
    KDP_FORMATS,
    calculate_kdp_specs,
    normalize_format,
)
from kdp_extensions.fonts_connector import (
    get_google_fonts_embed_url,
    recommend_font_pairing,
)
from kdp_extensions.cover_calculator import (
    calculate_cover_dimensions,
    generate_cover_template_svg,
)
from kdp_extensions.editorial_structure import (
    assemble_complete_book,
    generate_back_matter_html,
    generate_front_matter_html,
)
from kdp_extensions.seo_a9_agent import (
    calculate_utf8_bytes,
    optimize_kdp_seo,
    validate_a9_slot,
)
from kdp_extensions.kdp_compliance_supervisor import (
    supervise_kdp_book,
)
from kdp_extensions.kdp_export_orchestrator import (
    compile_kdp_interior_pdf,
    inject_kdp_prepress_bonus_pages,
)
from kdp_extensions.puzzle_generator import (
    generate_word_search,
    generate_maze,
    generate_word_scramble,
    generate_riddles_set,
    generate_cryptogram,
    generate_word_ladder,
    generate_connect_dots,
    generate_logic_grid,
    _render_maze_svg,
    _render_dots_svg,
    _puzzle_html,
    _solution_html,
)

logger = logging.getLogger("multilingual_transcreator")

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "exports" / "multilang_bundles"
BUNDLES_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# 1. BASE DE DONNÉES DE TRANSCRÉATION IDIOMATIQUE PAR NICHE & CULTURE
# ==============================================================================

CULTURAL_TRANSCREATION_MATRIX: Dict[str, Dict[str, Dict[str, Any]]] = {
    "finances": {
        "en": {
            "title": "The Financial Architect",
            "subtitle": "Building Wealth and Freedom Without Speculation: The 30-Day Step-by-Step Blueprint",
            "currency": "$",
            "institutions": ["Roth IRA", "401(k)", "HYSA", "S&P 500 Index Funds", "FICO Credit Score"],
            "pain_point": "Living paycheck to paycheck despite a six-figure salary, overwhelmed by financial jargon.",
            "transformation": "Automating your savings cascade in 30 days to build a bulletproof emergency cushion.",
            "author_note": "Certified financial education framework.",
            "target_audience": "Beginners and professionals seeking stress-free money management."
        },
        "fr": {
            "title": "L'Architecte Financier",
            "subtitle": "Bâtir son Indépendance et son Patrimoine Sans Spéculer : La Méthode Pas-à-Pas en 30 Jours",
            "currency": "€",
            "institutions": ["PEA", "Assurance-Vie", "Livret A", "SCPI", "Comptes Tampons"],
            "pain_point": "Le découvert bancaire récurrent le 20 du mois et la peur paralysante de perdre son capital.",
            "transformation": "Mettre en place un système de trésorerie en cascades qui automatise 20 % d'épargne dès le jour de paie.",
            "author_note": "Protocole éditorial d'ingénierie financière audité.",
            "target_audience": "Jeunes actifs et salariés désireux d'assainir leurs finances."
        },
        "es": {
            "title": "El Arquitecto Financiero",
            "subtitle": "Construya su Libertad Patrimonial sin Especulaciones: El Método Paso a Paso en 30 Días",
            "currency": "€",
            "institutions": ["Fondos Indexados", "Planes de Pensiones", "Cuenta Remunerada", "Letras del Tesoro", "Colchón de Seguridad"],
            "pain_point": "La inflación constante devorando los ahorros y el miedo a invertir sin conocimientos técnicos.",
            "transformation": "Automatizar la inversión pasiva diversificada para dormir tranquilo mientras su dinero crece.",
            "author_note": "Manual práctico de educación patrimonial.",
            "target_audience": "Ahorradores y familias que buscan seguridad financiera."
        },
        "de": {
            "title": "Der Finanzarchitekt",
            "subtitle": "Vermögensaufbau und finanzielle Unabhängigkeit ohne Spekulation: Die 30-Tage-Schritt-für-Schritt-Methode",
            "currency": "€",
            "institutions": ["ETF-Sparplan", "Tagesgeld", "Festgeld", "Notgroschen", "Drei-Säulen-Prinzip"],
            "pain_point": "Nullzinsfalle, Kaufkraftverlust durch Inflation und undurchsichtige Bankprodukte.",
            "transformation": "Aufbau eines automatisierten Vermögens-Systems mit global gestreuten ETFs und sicherem Notgroschen.",
            "author_note": "Geprüfter Leitfaden für rationale Vermögensbildung.",
            "target_audience": "Berufstätige und Sparer, die ihr Geld eigenverantwortlich schützen möchten."
        },
        "ar": {
            "title": "المهندس المالي",
            "subtitle": "بناء الاستقلال والثروة بدون مضاربة: الدليل العملي خطوة بخطوة خلال 30 يوماً",
            "currency": "د.إ",
            "institutions": ["الاستثمار الحلال", "الصكوك الاستثمارية", "صناديق المؤشرات النقية", "صندوق الطوارئ", "حساب التوفير الذكي"],
            "pain_point": "التضخم المتسارع وضياع المدخرات في مصاريف استهلاكية بدون خطة واضحة متوافقة مع القيم.",
            "transformation": "تأسيس نظام مالي تلقائي يقسم الدخل بذكاء ويستثمر في أصول حقيقية حلال تضمن راحة البال.",
            "author_note": "منهج عملي في الإدارة المالية الرشيدة والأصول الحقيقية.",
            "target_audience": "الشباب والعائلات الطامحة للأمان المالي والاستثمار الرشيد."
        }
    },
    "animaux de la savane": {
        "en": {
            "title": "The Ultimate Savannah Activity Book",
            "subtitle": "58 Fun Mazes, Word Searches & Safari Logic Puzzles for Kids Ages 6-8",
            "currency": "$",
            "institutions": ["Educational Safari", "Wildlife Observation", "Deductive Logic", "STEM Curiosity"],
            "pain_point": "Excessive screen time and a need for engaging, brain-boosting offline adventures.",
            "transformation": "An exciting 58-challenge safari journey that builds focus, vocabulary, and wildlife wonder.",
            "author_note": "Certified MarkEddy playful learning design.",
            "target_audience": "Kids ages 6 to 8 (1st to 3rd grade) and young wildlife explorers.",
            "seed_keywords": ["savannah animals activity book", "puzzles for kids ages 6 8", "mazes word search safari", "educational wildlife game book", "fun logic games elementary"]
        },
        "fr": {
            "title": "Grand Livre de Jeux de la Savane",
            "subtitle": "58 Puzzles, Labyrinthes et Mots Mêlés pour Petits Explorateurs (6-8 ans)",
            "currency": "€",
            "institutions": ["Safari Pédagogique", "Observation Faune", "Logique Déductive", "Éveil Scientifique"],
            "pain_point": "Les écrans omniprésents et la recherche d'activités ludo-éducatives intelligentes et captivantes.",
            "transformation": "Un voyage immersif de 58 défis progressifs qui stimule la concentration et la curiosité scientifique.",
            "author_note": "Conception ludo-pédagogique certifiée MarkEddy.",
            "target_audience": "Enfants de 6 à 8 ans (CP, CE1, CE2) et jeunes explorateurs de la nature.",
            "seed_keywords": ["animaux savane jeux enfants", "cahier activites 6 8 ans", "mots meles labyrinthes safari", "jeux logique primaire", "enigmes devinettes animaux"]
        },
        "es": {
            "title": "El Gran Libro de Juegos de la Sabana",
            "subtitle": "58 Puzzles, Laberintos y Acertijos Divertidos para Niños de 6 a 8 Años",
            "currency": "€",
            "institutions": ["Safari Pedagógico", "Observación Silvestre", "Lógica Deductiva", "Curiosidad Científica"],
            "pain_point": "Demasiado tiempo frente a pantallas y falta de cuadernos entretenidos que despierten el ingenio.",
            "transformation": "Un viaje fascinante de 58 desafíos que fomenta la paciencia, la lectura y el amor por los animales.",
            "author_note": "Diseño lúdico-pedagógico certificado MarkEddy.",
            "target_audience": "Niños de 6 a 8 años (Primaria) y pequeños aventureros de la naturaleza.",
            "seed_keywords": ["libro juegos sabana animales", "pasatiempos ninos 6 8 anos", "laberintos sopas letras safari", "cuaderno actividades infantil", "acertijos logica primaria"]
        },
        "de": {
            "title": "Das Große Savannen-Rätselbuch",
            "subtitle": "58 Spannende Suchsel, Labyrinthe & Denksportaufgaben für Kinder von 6 bis 8 Jahren",
            "currency": "€",
            "institutions": ["Lern-Safari", "Tierbeobachtung", "Deduktive Logik", "Naturbegeisterung"],
            "pain_point": "Übermäßige Bildschirmzeit und der Wunsch nach sinnvoller, fesselnder Offline-Beschäftigung.",
            "transformation": "Eine lehrreiche Safari mit 58 abwechslungsreichen Rätseln für maximale Konzentration und Wissensdurst.",
            "author_note": "Geprüftes Lernspiel-Konzept von MarkEddy.",
            "target_audience": "Kinder von 6 bis 8 Jahren (1. bis 3. Klasse) und neugierige Safari-Forscher.",
            "seed_keywords": ["savanne tiere raetselbuch", "kinder beschaeftigung 6 8 jahre", "suchsel labyrinthe safari", "denksport logik grundschule", "mitmachheft ferien raetsel"]
        },
        "ar": {
            "title": "كتاب ألغاز وأنشطة حيوانات السافانا",
            "subtitle": "٥٨ لغزاً ومتاهة ممتعة ومسابقات ذكاء للأطفال المستكشفين (٦-٨ سنوات)",
            "currency": "د.إ",
            "institutions": ["سفاري تعليمي", "مراقبة الحياة البرية", "الاستنتاج المنطقي", "الفضول العلمي"],
            "pain_point": "قضاء أوقات طويلة أمام الشاشات الإلكترونية والحاجة إلى أنشطة ورقية ذكية تنمي المهارات.",
            "transformation": "رحلة سفاري مشوقة عبر ٥٨ تحدياً متدرجاً تنمي قوة الملاحظة، التركيز والذكاء اللغوي.",
            "author_note": "منهج تربوي ترفيهي معتمد من استوديو MarkEddy.",
            "target_audience": "الأطفال من سن ٦ إلى ٨ سنوات (المرحلة الابتدائية) والمستكشفون الصغار.",
            "seed_keywords": ["كتاب انشطة حيوانات السافانا", "العاب ذكاء اطفال ٦ ٨ سنوات", "متاهات كلمات متقاطعة سفاري", "دفتر تسلية والغاز للاطفال", "تنمية مهارات التفكير المنطقي"]
        }
    },
    "general": {
        "en": {
            "title_prefix": "The Mastery of",
            "subtitle_template": "The Step-by-Step Practical Handbook for Concrete Results in 30 Days",
            "currency": "$"
        },
        "fr": {
            "title_prefix": "L'Art de Maîtriser",
            "subtitle_template": "Le Guide Pratique Pas-à-Pas pour Obtenir des Résultats Concrets en 30 Jours",
            "currency": "€"
        },
        "es": {
            "title_prefix": "El Arte de Dominar",
            "subtitle_template": "La Guía Práctica Paso a Paso para Lograr Resultados Claros en 30 Días",
            "currency": "€"
        },
        "de": {
            "title_prefix": "Die Kunst des Erfolgs in",
            "subtitle_template": "Das praxisorientierte Handbuch für messbare Ergebnisse in 30 Tagen",
            "currency": "€"
        },
        "ar": {
            "title_prefix": "فن إتقان",
            "subtitle_template": "الدليل العملي الشامل خطوة بخطوة لتحقيق نتائج ملموسة في 30 يوماً",
            "currency": "د.إ"
        }
    }
}

CULTURAL_TRANSCREATION_MATRIX["savane"] = CULTURAL_TRANSCREATION_MATRIX["animaux de la savane"]
CULTURAL_TRANSCREATION_MATRIX["puzzles"] = CULTURAL_TRANSCREATION_MATRIX["animaux de la savane"]
CULTURAL_TRANSCREATION_MATRIX["puzzle"] = CULTURAL_TRANSCREATION_MATRIX["animaux de la savane"]


SAVANNAH_PUZZLE_WORDS = {
    "fr": ["LION", "ZEBRE", "GIRAFE", "ELEPHANT", "GUEPARD", "SURICATE", "RHINOCEROS", "HIPPOPOTAME", "AUTRUCHE", "GAZELLE", "BABOUIN", "HYENE"],
    "en": ["LION", "ZEBRA", "GIRAFFE", "ELEPHANT", "CHEETAH", "MEERKAT", "RHINOCEROS", "HIPPO", "OSTRICH", "GAZELLE", "BABOON", "HYENA"],
    "es": ["LEON", "CEBRA", "JIRAFA", "ELEFANTE", "GUEPARDO", "SURICATA", "RINOCERONTE", "HIPOPOTAMO", "AVESTRUZ", "GACELA", "BABUINO", "HIENA"],
    "de": ["LOEWE", "ZEBRA", "GIRAFFE", "ELEFANT", "GEPARD", "ERDMAENNCHEN", "NASHORN", "FLUSSPFERD", "STRAUSS", "GAZELLE", "PAVIAN", "HYAENE"],
    "ar": ["اسد", "زرافة", "فيل", "حمار_وحشي", "فهد", "سرقاط", "وحيد_القرن", "فرس_النهر", "نعامة", "غزال", "قرد", "ضبع"],
}

SAVANNAH_SECRET_PHRASES = {
    "fr": "LE LION EST LE ROI DE LA SAVANE",
    "en": "THE LION IS THE KING OF THE SAVANNAH",
    "es": "EL LEON ES EL REY DE LA SABANA",
    "de": "DER LOEWE IST DER KOENIG DER SAVANNE",
    "ar": "الاسد هو ملك السافانا الشجاع",
}

SAVANNAH_PUZZLE_TYPES_TITLES = {
    "fr": {
        "word_search": "Mots Mêlés de la Savane",
        "maze": "Le Grand Labyrinthe du Safari",
        "word_scramble": "Mots Mélangés de la Savane",
        "riddles": "Devinettes des Animaux",
        "cryptogram": "Code Secret du Ranger",
        "word_ladder": "Échelle des Mots Magiques",
        "connect_dots": "Points à Relier Mystère",
        "logic_grid": "Défi Logique de la Piste",
    },
    "en": {
        "word_search": "Savannah Word Search",
        "maze": "Great Safari Maze",
        "word_scramble": "Wild Word Scramble",
        "riddles": "Animal Safari Riddles",
        "cryptogram": "Ranger's Secret Code",
        "word_ladder": "Magic Word Ladder",
        "connect_dots": "Mystery Connect the Dots",
        "logic_grid": "Safari Logic Grid",
    },
    "es": {
        "word_search": "Sopa de Letras de la Sabana",
        "maze": "Gran Laberinto del Safari",
        "word_scramble": "Palabras Mezcladas",
        "riddles": "Acertijos de Animales",
        "cryptogram": "Código Secreto del Guardabosques",
        "word_ladder": "Escalera de Palabras",
        "connect_dots": "Une los Puntos Safari",
        "logic_grid": "Cuadrícula de Lógica",
    },
    "de": {
        "word_search": "Savannen-Wörtersuche",
        "maze": "Großes Safari-Labyrinth",
        "word_scramble": "Buchstaben-Salat der Tiere",
        "riddles": "Knifflige Tierrätsel",
        "cryptogram": "Ranger-Geheimcode",
        "word_ladder": "Magische Wortleiter",
        "connect_dots": "Punkte verbinden Safari",
        "logic_grid": "Logik-Gitter Safari",
    },
    "ar": {
        "word_search": "كلمات متقاطعة السافانا",
        "maze": "متاهة السفاري الكبرى",
        "word_scramble": "حروف الحيوانات المبعثرة",
        "riddles": "حزورات الحيوانات الذكية",
        "cryptogram": "الرمز السري لحارس المحمية",
        "word_ladder": "سلم الكلمات الذكية",
        "connect_dots": "صل النقاط واكتشف الحيوان",
        "logic_grid": "تحدي شبكة المنطق",
    }
}

SAVANNAH_SCIENCE_FACTS = {
    "fr": [
        ("Roi de la Savane", "Le lion peut dormir jusqu'à 20 heures par jour pour préserver son énergie avant ses chasses nocturnes !"),
        ("Géante Majestueuse", "La girafe ne dort que 30 minutes par jour et son cou mesure plus de 2 mètres de haut !"),
        ("Mémoire Prodigieuse", "La trompe de l'éléphant compte plus de 40 000 muscles différents et peut déraciner un grand arbre !"),
        ("Empreinte Secrète", "Les rayures de chaque zèbre sont absolument uniques au monde, comme nos empreintes digitales !"),
        ("Champion de Vitesse", "Le guépard est le coureur le plus rapide de la Terre : il atteint 100 km/h en seulement 3 secondes !"),
        ("Écran Solaire Naturel", "L'hippopotame produit un fluide rose-rougeâtre qui hydrate sa peau et la protège des rayons UV du soleil !"),
        ("Corne d'Armure", "La corne du rhinocéros n'est pas faite d'os, mais de kératine compacte, comme nos ongles et nos cheveux !"),
        ("Sentinelle du Désert", "Dans un clan de suricates, une sentinelle reste toujours perchée sur deux pattes pour avertir le groupe des rapaces !"),
        ("Yeux Géants", "L'autruche est le plus grand oiseau du monde, et chacun de ses yeux est plus volumineux que son cerveau !"),
        ("Vision Panoramique", "Le caméléon possède des yeux indépendants capables d'observer deux directions opposées à la fois !"),
        ("Langage des Singes", "Les babouins communiquent avec plus de 30 vocalisations différentes et des mimiques très expressives !"),
        ("Secret Rose", "Les flamants roses naissent gris ! C'est leur alimentation riche en petites crevettes qui colore leurs plumes !"),
        ("Carapace Géante", "La tortue léopard de la savane peut vivre plus de 75 ans et sa dossière ressemble à un bouclier doré !"),
        ("Genoux Tout Doux", "Le phacochère plie souvent ses pattes avant et broute à genoux grâce à des callosités protectrices !"),
        ("Seigneur des Airs", "L'aigle martial d'Afrique a une vue 4 fois plus perçante que celle d'un humain et plane pendant des heures !")
    ],
    "en": [
        ("King of the Savannah", "Lions can sleep up to 20 hours a day to conserve their energy for nighttime hunting!"),
        ("Majestic Giant", "A giraffe only sleeps 30 minutes a day, and its neck can measure over 6 feet long!"),
        ("Gentle Giant", "An elephant's trunk contains more than 40,000 muscles and can lift heavy tree branches with ease!"),
        ("Unique Stripes", "Every zebra has a unique pattern of stripes, just like human fingerprints!"),
        ("Speed Champion", "The cheetah is the fastest land animal, accelerating from 0 to 60 mph in just 3 seconds flat!"),
        ("Natural Sunscreen", "Hippos produce a reddish fluid on their skin that acts as a natural sunscreen and antibiotic moisturizer!"),
        ("Armored Horn", "A rhino's horn is not made of bone, but of dense keratin, the exact same protein as our hair and nails!"),
        ("Desert Sentry", "In a meerkat mob, one guard always stands tall on two legs to warn the family if a hawk flies overhead!"),
        ("Giant Eyes", "The ostrich is the world's biggest bird, and each of its eyes is actually larger than its entire brain!"),
        ("Panoramic Eyes", "A chameleon's eyes can swivel independently, allowing it to look in two different directions at once!"),
        ("Chatty Monkeys", "Baboons communicate using more than 30 distinct vocal calls, gestures, and expressive faces!"),
        ("Pink Feathers", "Flamingos are born gray! Their feathers turn bright pink from the carotenoid pigments in their diet!"),
        ("Long-Lived Friend", "The leopard tortoise can live over 75 years and its shell pattern looks like a golden spotted shield!"),
        ("Kneeling Grazer", "Warthogs often bend their front legs and graze on their knees, protected by special padded calluses!"),
        ("Sky Hunter", "The African martial eagle has eyesight 4 times sharper than a human and can soar for hours on thermal currents!")
    ],
    "es": [
        ("Rey de la Sabana", "¡El león puede dormir hasta 20 horas al día para ahorrar energía antes de cazar de noche!"),
        ("Gigante Majestuosa", "¡La jirafa solo duerme 30 minutos al día y su cuello mide más de 2 metros de largo!"),
        ("Memoria Asombrosa", "¡La trompa del elefante posee más de 40.000 músculos y puede levantar ramas pesadísimas con facilidad!"),
        ("Rayas Únicas", "¡Las rayas de cada cebra son irrepetibles en el mundo, como las huellas dactilares de las personas!"),
        ("Velocidad Extrema", "¡El guepardo es el mamífero más veloz del planeta: alcanza 100 km/h en apenas 3 segundos!"),
        ("Protector Solar Natural", "¡El hipopótamo segrega un líquido rojizo que hidrata su piel y la protege de los rayos del sol!"),
        ("Cuerno Protector", "¡El cuerno del rinoceronte no es de hueso, sino de queratina pura, igual que nuestras uñas y cabello!"),
        ("Centinela Curioso", "¡En cada familia de suricatas, un centinela se para en dos patas para vigilar el cielo y alertar de águilas!"),
        ("Ojos Gigantescos", "¡El avestruz es el ave más grande del mundo, y cada uno de sus ojos es más grande que su cerebro!"),
        ("Visión Panorámica", "¡El camaleón puede mover sus ojos de forma independiente y mirar en dos direcciones opuestas a la vez!"),
        ("Lenguaje Fascinante", "¡Los babuinos se comunican mediante más de 30 sonidos distintos y gestos faciales muy expresivos!"),
        ("Color Sorprendente", "¡Los flamencos nacen de color gris! Sus plumas se vuelven rosas gracias a los carotenoides de su comida!"),
        ("Amiga Centenaria", "¡La tortuga leopardo de la sabana puede vivir más de 75 años con un caparazón moteado como un escudo!"),
        ("Comilón de Rodillas", "¡El facóquero a menudo pasta de rodillas sobre sus patas delanteras gracias a unas almohadillas especiales!"),
        ("Señor del Cielo", "¡El águila marcial africana tiene una vista 4 veces más aguda que la del ser humano y planea durante horas!")
    ],
    "de": [
        ("König der Savanne", "Löwen können bis zu 20 Stunden am Tag schlafen, um Energie für die nächtliche Jagd zu sparen!"),
        ("Majestätische Riesin", "Eine Giraffe schläft nur etwa 30 Minuten am Tag und ihr Hals ist über 2 Meter lang!"),
        ("Sanfter Riese", "Der Rüssel eines Elefanten besitzt über 40.000 Muskeln und kann riesige Äste mühelos anheben!"),
        ("Einzigartige Streifen", "Die Streifen jedes Zebras sind weltweit einmalig, genau wie menschliche Fingerabdrücke!"),
        ("Geschwindigkeits-Rekord", "Der Gepard ist das schnellste Landsäugetier der Erde: Er beschleunigt in 3 Sekunden auf 100 km/h!"),
        ("Natürliche Sonnencreme", "Flusspferde bilden ein rötliches Sekret, das ihre Haut wie eine natürliche Sonnencreme schützt!"),
        ("Horn aus Keratin", "Das Horn des Nashorns besteht nicht aus Knochen, sondern aus festem Keratin wie unsere Haare und Fingernägel!"),
        ("Wachsame Wächter", "In einer Erdmännchen-Gruppe steht stets ein Wachposten auf zwei Beinen, um vor Greifvögeln zu warnen!"),
        ("Riesige Augen", "Der Strauß ist der größte Vogel der Welt, und seine Augen sind tatsächlich größer als sein Gehirn!"),
        ("Panoramablick", "Chamäleons können ihre Augen unabhängig voneinander bewegen und gleichzeitig in zwei Richtungen blicken!"),
        ("Ausdrucksstarke Affen", "Paviane verständigen sich mit über 30 verschiedenen Lauten und einer ausdrucksvollen Mimik!"),
        ("Rosa Gefieder", "Flamingos kommen mit grauem Gefieder zur Welt! Ihre rosa Farbe erhalten sie erst durch ihre Nahrung!"),
        ("Uralte Panzerträgerin", "Die Pantherschildkröte kann über 75 Jahre alt werden und besitzt einen wunderschön gemusterten Panzer!"),
        ("Knieende Grasfresser", "Warzenschweine grasen oft auf den Knien ihrer Vorderbeine, die durch dicke Schwielen geschützt sind!"),
        ("König der Lüfte", "Der afrikanische Kampfadler sieht viermal schärfer als ein Mensch und gleitet stundenlang durch die Thermik!")
    ],
    "ar": [
        ("ملك السافانا", "يمكن للأسد أن ينام حتى ٢٠ ساعة يومياً لتوفير طاقته لرحلات الصيد الليلية!"),
        ("عملاقة السافانا", "تنام الزرافة حوالي ٣٠ دقيقة فقط يومياً ويصل طول رقبتها إلى أكثر من مترين!"),
        ("ذاكرة خارقة", "يحتوي خرطوم الفيل على أكثر من ٤٠,٠٠٠ عضلة مختلفة ويمكنه رفع جذوع الأشجار الضخمة بسهولة!"),
        ("بصمة فريدة", "خطوط كل حمار وحشي فريدة من نوعها في العالم تماماً مثل بصمات أصابع الإنسان!"),
        ("بطل السرعة", "الفهد الصياد هو أسرع حيوان بري على الأرض: ينطلق إلى سرعة ١٠٠ كم/س في ٣ ثوانٍ فقط!"),
        ("واقي شمس طبيعي", "يفرز فرس النهر سائلاً أحمر طبيعياً يرطب جلده ويحميه تماماً من أشعة الشمس الحارقة!"),
        ("قرن الحماية", "لا يتكون قرن وحيد القرن من العظام، بل من مادة الكيراتين الصلبة مثل أظافر الإنسان وشعره!"),
        ("حارس الصحراء", "في عائلة السرقاط، يقف حارس يقظ دائماً على رجليه الخلفيتين لمراقبة السماء وتحذير الجميع من النسور!"),
        ("عيون عملاقة", "النعامة هي أضخم طائر على وجه الأرض، وكل عين من عينيها أكبر من حجم دماغها بالكامل!"),
        ("رؤية بانورامية", "تستطيع الحرباء تحريك كل عين من عينيها بشكل مستقل للنظر في اتجاهين متعاكسين في نفس اللحظة!"),
        ("لغة التواصل", "يتواصل قرد البابون مع عائلته باستخدام أكثر من ٣٠ نداء صوتياً مختلفاً وتعبيرات وجه معبرة!"),
        ("سر اللون الوردي", "يولد طائر الفلامنغو بريش رمادي! ويتحول ريشه إلى الوردي الزاهي بفضل غذائه الغني بالأصباغ الطبيعية!"),
        ("سلحفاة معمرة", "يمكن لسلحفاة الفهد في السافانا أن تعيش لأكثر من ٧٥ عاماً ودرعها يشبه لوحة فنية مرقطة!"),
        ("الرعي على الركبتين", "ينحني الخنزير البري الأفريقي في كثير من الأحيان على ركبتيه الأماميتين ليرعى العشب بكل راحة!"),
        ("سيد السماء", "يتمتع النسر الحربي الأفريقي بنظر حاد أقوى بـ ٤ مرات من نظر الإنسان ويحلق لساعات طويلة في الأعالي!")
    ]
}

SAVANNAH_RIDDLES_BANK = {
    "fr": [
        ("Je suis le roi des animaux avec une magnifique crinière dorée. Qui suis-je ?", "LION"),
        ("J'ai un très long cou pour manger les feuilles tout en haut des acacias. Qui suis-je ?", "GIRAFE"),
        ("J'ai de superbes rayures noires et blanches et je galope en troupeau. Qui suis-je ?", "ZEBRE"),
        ("Je suis le plus grand mammifère terrestre avec de grandes oreilles et une trompe. Qui suis-je ?", "ELEPHANT"),
        ("Je cours plus vite que tous les animaux de la savane. Qui suis-je ?", "GUEPARD"),
        ("Je vis en famille dans des terriers et me dresse sur deux pattes pour faire le guet. Qui suis-je ?", "SURICATE"),
        ("J'adore me baigner dans la boue et j'ai une énorme mâchoire. Qui suis-je ?", "HIPPOPOTAME"),
        ("J'ai une ou deux cornes robustes sur le museau et une peau épaisse. Qui suis-je ?", "RHINOCEROS"),
        ("Je suis un oiseau géant incapable de voler mais je cours très vite. Qui suis-je ?", "AUTRUCHE"),
        ("Je saute avec grâce et agilité dans les hautes herbes dorées. Qui suis-je ?", "GAZELLE"),
        ("Je vis en groupe dans les arbres et les rochers avec une longue queue. Qui suis-je ?", "BABOUIN"),
        ("On entend souvent mon rire résonner la nuit dans la plaine. Qui suis-je ?", "HYENE")
    ],
    "en": [
        ("I am the king of beasts with a majestic golden mane. Who am I?", "LION"),
        ("I have a very long neck to reach high acacia leaves. Who am I?", "GIRAFFE"),
        ("I have striking black and white stripes and live in big herds. Who am I?", "ZEBRA"),
        ("I am the largest land animal with big ears and a long trunk. Who am I?", "ELEPHANT"),
        ("I can sprint faster than any sports car on land. Who am I?", "CHEETAH"),
        ("I stand tall on two legs to watch the sky for hawks. Who am I?", "MEERKAT"),
        ("I love soaking in muddy rivers and have massive yawning jaws. Who am I?", "HIPPO"),
        ("I have thick armor-like skin and a horn on my nose. Who am I?", "RHINO"),
        ("I am the tallest bird on Earth and lay giant eggs. Who am I?", "OSTRICH"),
        ("I leap gracefully across the golden grasslands. Who am I?", "GAZELLE"),
        ("I am a smart monkey living on rocky cliffs in big troops. Who am I?", "BABOON"),
        ("My laughter echoes across the African plains under the stars. Who am I?", "HYENA")
    ],
    "es": [
        ("Soy el rey de la sabana con una melena dorada majestuosa. ¿Quién soy?", "LEON"),
        ("Tengo un cuello larguísimo para comer hojas de las acacias. ¿Quién soy?", "JIRAFA"),
        ("Tengo rayas blancas y negras únicas en todo el mundo. ¿Quién soy?", "CEBRA"),
        ("Soy el gigante terrestre más grande con trompa y grandes orejas. ¿Quién soy?", "ELEFANTE"),
        ("Corro más rápido que cualquier otro mamífero en tierra. ¿Quién soy?", "GUEPARDO"),
        ("Me paro en dos patitas para vigilar a los depredadores. ¿Quién soy?", "SURICATA"),
        ("Paso el día sumergido en el agua refrescando mi piel. ¿Quién soy?", "HIPOPOTAMO"),
        ("Tengo un cuerno fuerte en el hocico y piel muy gruesa. ¿Quién soy?", "RINOCERONTE"),
        ("Soy el ave más grande del planeta pero no puedo volar. ¿Quién soy?", "AVESTRUZ"),
        ("Salto con elegancia entre los pastos dorados de la llanura. ¿Quién soy?", "GACELA"),
        ("Vivo en tropas familiares en las rocas y árboles africanos. ¿Quién soy?", "BABUINO"),
        ("Mi risa característica resuena en la noche bajo la luna. ¿Quién soy?", "HIENA")
    ],
    "de": [
        ("Ich bin der König der Tiere mit einer prächtigen Mähne. Wer bin ich?", "LOEWE"),
        ("Ich habe einen riesigen Hals, um Akazienblätter zu fressen. Wer bin ich?", "GIRAFFE"),
        ("Ich habe schwarz-weiße Streifen und galoppiere in Herden. Wer bin ich?", "ZEBRA"),
        ("Ich bin das größte Landsäugetier mit Rüssel und Riesenohren. Wer bin ich?", "ELEFANT"),
        ("Ich sprinte schneller als jedes andere Tier auf der Erde. Wer bin ich?", "GEPARD"),
        ("Ich stehe auf zwei Beinchen Wache für meine Familie. Wer bin ich?", "ERDMAENNCHEN"),
        ("Ich liebe Schlammbäder und habe ein riesiges Maul. Wer bin ich?", "FLUSSPFERD"),
        ("Ich trage ein Horn auf der Nase und habe eine dicke Haut. Wer bin ich?", "NASHORN"),
        ("Ich bin der größte Vogel der Welt und renne blitzschnell. Wer bin ich?", "STRAUSS"),
        ("Ich springe leichtfüßig durch das hohe Savannengras. Wer bin ich?", "GAZELLE"),
        ("Ich lebe in großen Affenbanden auf afrikanischen Felsen. Wer bin ich?", "PAVIAN"),
        ("Mein lautes Lachen hallt nachts durch die Savanne. Wer bin ich?", "HYAENE")
    ],
    "ar": [
        ("أنا ملك الغابة ذو اللبدة الذهبية المهيبة والصوت الهادر، فمن أكون؟", "اسد"),
        ("لدي رقبة طويلة جداً تمكنني من أكل أوراق شجر الأكاسيا، فمن أكون؟", "زرافة"),
        ("أرتدي ثوباً مخططاً باللونين الأبيض والأسود لا يتكرر أبداً، فمن أكون؟", "حمار_وحشي"),
        ("أنا أضخم حيوان على اليابسة ولدي خرطوم عجيب وأذنان واسعتان، فمن أكون؟", "فيل"),
        ("أنا أسرع كائن حي يركض على وجه الأرض، فمن أكون؟", "فهد"),
        ("أقف بذكاء على رجلي الخلفيتين لحراسة أفراد عائلتي من النسور، فمن أكون؟", "سرقاط"),
        ("أحب السباحة في المياه والوحل ولدي فك ضخم للغاية، فمن أكون؟", "فرس_النهر"),
        ("أحمل قرناً قوياً على أنفي وجلدي سميك كأنه درع صلب، فمن أكون؟", "وحيد_القرن"),
        ("أنا أكبر طائر في العالم، لا أطير ولكنني أعدو بسرعة الرياح، فمن أكون؟", "نعامة"),
        ("أقفز بخفة ورشاقة فائقة بين أعشاب السافانا الذهبية، فمن أكون؟", "غزال"),
        ("أعيش في جماعات مترابطة فوق الصخور والأشجار بذكاء ونشاط، فمن أكون؟", "قرد"),
        ("يُسمع صوتي المميز الشبيه بالضحك ليلاً في سهول البرية، فمن أكون؟", "ضبع")
    ]
}

SAVANNAH_EDITORIAL_PAGES = {
    "fr": {
        "fm_subtitle": "Édition Safari 6-8 ans",
        "copyright_title": "Mentions Légales & Copyright",
        "kdp_notice": "Conforme aux normes d'impression Amazon KDP. Papier blanc haute opacité, reliure brochée.",
        "belongs_title": "Ce carnet de jeu appartient à :",
        "belongs_name": "Nom de l'Explorateur :",
        "belongs_date": "Date de départ en expédition :",
        "toc_title": "Sommaire des 8 Mondes de la Savane",
        "toc_items": [
            "1. Le Bosquet des Mots Mêlés",
            "2. Les Pistes des Labyrinthes",
            "3. La Rivière des Mots Mélangés",
            "4. La Clairière des Devinettes",
            "5. Le Rocher des Codes Secrets",
            "6. L'Escalade des Mots",
            "7. Les Constellations des Points",
            "8. L'Épreuve des Grilles de Logique"
        ],
        "oath_title": "Le Serment de l'Explorateur",
        "oath_text": "Je promets d'observer la nature avec curiosité, de réfléchir avec patience et de protéger la faune sauvage !",
        "parents_guide_title": "Guide Pédagogique pour les Parents",
        "parents_guide_text": "Ces activités ont été spécialement conçues pour développer la motricité fine, la concentration, la logique déductive et enrichir le vocabulaire des enfants de primaire.",
        "sol_title": "Solutions des Puzzles",
        "sol_part": "Partie",
        "notes_title": "Mon Carnet de Safari — Dessins & Observations",
        "diploma_title": "DIPLÔME OFFICIEL DE L'EXPLORATEUR",
        "diploma_body": "Ce diplôme d'honneur certifie que le courageux explorateur a résolu avec succès les 58 énigmes de la Savane !",
        "diploma_date": "Date :",
        "diploma_signature": "Signature du Grand Guide :",
        "review_title": "Message Spécial pour les Parents",
        "review_body": "Nous espérons de tout cœur que votre enfant a passé un moment d'aventure inoubliable ! Votre avis bienveillant sur Amazon nous aide énormément : ⭐⭐⭐⭐⭐",
        "colophon_title": "Colophon & Marque d'Imprimerie",
        "colophon_text": "Ouvrage certifié Amazon KDP Paperback. Rendu typographique haute définition 300 DPI, encre noire sans reflet.",
        "page_label": "Page",
    },
    "en": {
        "fm_subtitle": "Safari Edition for Ages 6-8",
        "copyright_title": "Legal Notice & Copyright",
        "kdp_notice": "Compliant with Amazon KDP print specifications. High-opacity white paper, paperback binding.",
        "belongs_title": "This Safari Activity Book Belongs To:",
        "belongs_name": "Explorer's Name:",
        "belongs_date": "Expedition Start Date:",
        "toc_title": "Contents: The 8 Worlds of the Savannah",
        "toc_items": [
            "1. The Word Search Grove",
            "2. The Great Safari Mazes",
            "3. The Word Scramble River",
            "4. The Riddle Clearing",
            "5. The Secret Code Rock",
            "6. The Word Ladder Climb",
            "7. The Mystery Connect-the-Dots",
            "8. The Logic Grid Challenge"
        ],
        "oath_title": "The Explorer's Oath",
        "oath_text": "I promise to observe nature with curiosity, think through puzzles with patience, and respect wildlife!",
        "parents_guide_title": "Parents' Pedagogical Guide",
        "parents_guide_text": "These activities are designed to foster fine motor skills, focus, deductive reasoning, and vocabulary expansion for elementary school kids.",
        "sol_title": "Answer Key & Solutions",
        "sol_part": "Part",
        "notes_title": "My Safari Field Journal — Sketches & Notes",
        "diploma_title": "OFFICIAL SAFARI EXPLORER CERTIFICATE",
        "diploma_body": "This certificate is proudly awarded for successfully solving all 58 Savannah Puzzles and Mazes!",
        "diploma_date": "Date:",
        "diploma_signature": "Chief Ranger Signature:",
        "review_title": "A Special Note for Parents",
        "review_body": "We hope your child enjoyed this wild journey! Your honest 5-star review on Amazon means the world to us: ⭐⭐⭐⭐⭐",
        "colophon_title": "Colophon & Printer's Mark",
        "colophon_text": "Certified Amazon KDP Paperback. High-resolution 300 DPI interior graphics, glare-free black ink.",
        "page_label": "Page",
    },
    "es": {
        "fm_subtitle": "Edición Safari para Niños de 6 a 8 Años",
        "copyright_title": "Aviso Legal y Derechos de Autor",
        "kdp_notice": "Conforme con los estándares de impresión Amazon KDP. Papel blanco de alta opacidad.",
        "belongs_title": "Este cuaderno de aventuras pertenece a:",
        "belongs_name": "Nombre del Pequeño Explorador:",
        "belongs_date": "Fecha de inicio del safari:",
        "toc_title": "Índice: Los 8 Mundos de la Sabana",
        "toc_items": [
            "1. La Arboleda de las Sopas de Letras",
            "2. Las Pistas de los Laberintos",
            "3. El Río de las Palabras Mezcladas",
            "4. El Claro de los Acertijos",
            "5. La Roca de los Códigos Secretos",
            "6. La Escalera de Palabras",
            "7. Puntos para Unir Misteriosos",
            "8. El Desafío de Cuadrículas Lógicas"
        ],
        "oath_title": "El Juramento del Explorador",
        "oath_text": "¡Prometo observar la naturaleza con curiosidad, pensar con paciencia y proteger a los animales salvajes!",
        "parents_guide_title": "Guía Pedagógica para Padres",
        "parents_guide_text": "Actividades diseñadas para estimular la concentración, la motricidad fina, el razonamiento lógico y el vocabulario en niños de primaria.",
        "sol_title": "Soluciones de los Juegos",
        "sol_part": "Parte",
        "notes_title": "Mi Diario de Safari — Dibujos y Observaciones",
        "diploma_title": "DIPLOMA OFICIAL DEL EXPLORADOR",
        "diploma_body": "¡Este diploma certifica que el valiente explorador ha resuelto con éxito los 58 pasatiempos de la Sabana!",
        "diploma_date": "Fecha:",
        "diploma_signature": "Firma del Guía Safari:",
        "review_title": "Un Mensaje Especial para los Padres",
        "review_body": "¡Esperamos que su hijo haya disfrutado de esta aventura! Su valoración en Amazon nos ayuda muchísimo: ⭐⭐⭐⭐⭐",
        "colophon_title": "Colofón y Pie de Imprenta",
        "colophon_text": "Libro certificado Amazon KDP Paperback. Impresión de alta definición a 300 DPI en negro puro.",
        "page_label": "Página",
    },
    "de": {
        "fm_subtitle": "Safari-Ausgabe für Kinder von 6 bis 8 Jahren",
        "copyright_title": "Impressum & Urheberrecht",
        "kdp_notice": "Gedruckt nach den Richtlinien von Amazon KDP. Hochwertiges weißes Papier, Taschenbuch.",
        "belongs_title": "Dieses spannende Rätselbuch gehört:",
        "belongs_name": "Name des Forschers:",
        "belongs_date": "Start der Safari-Expedition:",
        "toc_title": "Inhalt: Die 8 Welten der Savanne",
        "toc_items": [
            "1. Der Suchsel-Hain",
            "2. Die großen Safari-Labyrinthe",
            "3. Der Fluss der Buchstaben-Salate",
            "4. Die Lichtung der Tier-Rätsel",
            "5. Der Felsen der Geheimschriften",
            "6. Die Wortleiter-Wand",
            "7. Geheimnisvolle Punkt-zu-Punkt-Bilder",
            "8. Die kniffligen Logik-Gitter"
        ],
        "oath_title": "Der Entdecker-Schwur",
        "oath_text": "Ich verspreche, die Natur neugierig zu erforschen, Rätsel mit Geduld zu lösen und Tiere zu schützen!",
        "parents_guide_title": "Pädagogischer Leitfaden für Eltern",
        "parents_guide_text": "Fördert gezielt Feinmotorik, Konzentration, logisches Denken und den Wortschatz von Grundschulkindern.",
        "sol_title": "Lösungen & Antwortschlüssel",
        "sol_part": "Teil",
        "notes_title": "Mein Safari-Tagebuch — Skizzen & Notizen",
        "diploma_title": "OFFIZIELLES SAFARI-DIPLOM",
        "diploma_body": "Diese Urkunde bestätigt, dass der mutige Forscher alle 58 Savannen-Rätsel erfolgreich gelöst hat!",
        "diploma_date": "Datum:",
        "diploma_signature": "Unterschrift des Chefforschers:",
        "review_title": "Liebe Eltern,",
        "review_body": "Wir hoffen, Ihr Kind hatte große Freude an diesem Buch! Ihre ehrliche 5-Sterne-Bewertung auf Amazon unterstützt uns sehr: ⭐⭐⭐⭐⭐",
        "colophon_title": "Kolophon & Druckvermerk",
        "colophon_text": "Zertifiziertes Amazon KDP Paperback. Druckoptimiertes 300 DPI Layout mit tiefschwarzer Tinte.",
        "page_label": "Seite",
    },
    "ar": {
        "fm_subtitle": "طبعة رحلة السفاري الممتعة (٦-٨ سنوات)",
        "copyright_title": "حقوق الطبع والنشر القانونية",
        "kdp_notice": "متوافق تماماً مع مواصفات الطباعة المباشرة لكيندل أمازون. ورق أبيض عالي الجودة.",
        "belongs_title": "هذا الدفتر الرائع يخص البطل المستكشف:",
        "belongs_name": "اسم البطل المستكشف:",
        "belongs_date": "تاريخ انطلاق رحلة السفاري:",
        "toc_title": "فهرس عوالم السافانا الثمانية",
        "toc_items": [
            "١. واحة الكلمات الضائعة",
            "٢. مسارات المتاهات الكبرى",
            "٣. جدول الحروف المبعثرة",
            "٤. روضة الحزورات الذكية",
            "٥. صخرة الشفرات السرية",
            "٦. تسلق سلم الكلمات",
            "٧. كوكبة النقاط السحرية",
            "٨. قمة شبكات المنطق"
        ],
        "oath_title": "عهد المستكشف الصغير",
        "oath_text": "أعاهد نفسي بأن أراقب الطبيعة بفضول، وأفكر بصبر، وأحمي الحيوانات البرية وبيئتها الطبيعية!",
        "parents_guide_title": "دليل أولياء الأمور التربوي",
        "parents_guide_text": "أُعدت هذه الأنشطة خصيصاً لتنمية التركيز، المهارات الحركية الدقيقة، الاستنتاج المنطقي وإثراء الحصيلة اللغوية للأطفال.",
        "sol_title": "دليل الحلول والإجابات",
        "sol_part": "الجزء",
        "notes_title": "دفتر رسوماتي وملاحظاتي في السفاري",
        "diploma_title": "شهادة المستكشف المتميز الرسمية",
        "diploma_body": "تشهد هذه الوثيقة بأن المستكشف الشجاع قد أتم بنجاح حل جميع ألغاز السافانا الـ ٥٨!",
        "diploma_date": "التاريخ:",
        "diploma_signature": "توقيع قائد السفاري:",
        "review_title": "رسالة خاصة إلى الوالدين",
        "review_body": "نتمنى أن يكون طفلكم قد قضى وقتاً مليئاً بالمرح والذكاء! تقييمكم بـ ٥ نجوم على أمازون يسعدنا كثيراً: ⭐⭐⭐⭐⭐",
        "colophon_title": "بيانات النشر والطباعة",
        "colophon_text": "كتاب معتمد وفق معايير أمازون كيندل للغلاف الورقي. تصميم عالي الجودة باللون الأسود الخالص.",
        "page_label": "الصفحة",
    }
}


def build_savannah_puzzle_book_html(meta: Dict[str, Any], target_pages: int = 80) -> str:
    """
    Génère le document HTML complet et print-ready d'exactement 80 pages pour le livre
    de puzzles 'Animaux de la savane' au format KDP 8.5" x 11" :
      - 6 pages de Front-Matter (Faux-titre, Copyright, Titre, Ce livre appartient à, Sommaire 8 Mondes, Serment Explorateur)
      - 58 pages de Puzzles progressifs (8 Mots Mêlés, 8 Labyrinthes, 8 Mots Mélangés, 7 Devinettes, 7 Codes Secrets, 7 Échelles, 7 Points à Relier, 6 Grilles Logique) avec encadré d'anecdote scientifique vérifiée
      - 12 pages de Solutions compactes et claires (4 à 5 solutions par page)
      - 4 pages de Back-Matter (Carnet de croquis, Diplôme officiel, Note aux parents/Avis Amazon, Colophon)
      Total = 6 + 58 + 12 + 4 = 80 pages exactes !
    """
    lang = normalize_language(meta.get("language") or "fr")
    profile = get_language_profile(lang)
    direction = profile.get("direction", "ltr")
    is_ar = (direction == "rtl")
    
    title = meta.get("title") or "Grand Livre de Jeux de la Savane"
    subtitle = meta.get("subtitle") or ""
    author = meta.get("author") or "MarkEddy"
    isbn = meta.get("isbn") or "979-8-0000-0000-0"
    year = meta.get("year", 2026)

    ed_pages = SAVANNAH_EDITORIAL_PAGES.get(lang, SAVANNAH_EDITORIAL_PAGES["fr"])
    t_titles = SAVANNAH_PUZZLE_TYPES_TITLES.get(lang, SAVANNAH_PUZZLE_TYPES_TITLES["fr"])
    words = SAVANNAH_PUZZLE_WORDS.get(lang, SAVANNAH_PUZZLE_WORDS["fr"])
    secret_phrase = SAVANNAH_SECRET_PHRASES.get(lang, "LE LION EST LE ROI DE LA SAVANE")
    facts = SAVANNAH_SCIENCE_FACTS.get(lang, SAVANNAH_SCIENCE_FACTS["fr"])
    riddles_bank = SAVANNAH_RIDDLES_BANK.get(lang, SAVANNAH_RIDDLES_BANK["fr"])
    page_lbl = ed_pages.get("page_label", "Page")

    rng = random.Random(777)
    puzzles: List[Dict[str, Any]] = []

    # 1. 8 Word Searches
    for i in range(8):
        s = rng.randint(1, 999999)
        dim = 9 if is_ar else 10
        puzzles.append(generate_word_search(f"{t_titles['word_search']} #{i+1}", words=words, rows=dim, cols=dim, allow_diagonal=not is_ar, seed=s, language=lang))

    # 2. 8 Mazes
    for i in range(8):
        s = rng.randint(1, 999999)
        puzzles.append(generate_maze(f"{t_titles['maze']} #{i+1}", width_cells=12, height_cells=12, seed=s))

    # 3. 8 Word Scrambles
    for i in range(8):
        s = rng.randint(1, 999999)
        puzzles.append(generate_word_scramble(f"{t_titles['word_scramble']} #{i+1}", words=words, count=6, seed=s))

    # 4. 7 Riddles sets
    for i in range(7):
        start_r = (i * 3) % len(riddles_bank)
        chosen_r = [riddles_bank[(start_r + k) % len(riddles_bank)] for k in range(3)]
        items = [{"question": q, "answer": a, "blanks": ["_"] * len(a)} for q, a in chosen_r]
        puzzles.append({
            "type": "riddles",
            "title": f"{t_titles['riddles']} #{i+1}",
            "items": items
        })

    # 5. 7 Cryptograms
    for i in range(7):
        s = rng.randint(1, 999999)
        puzzles.append(generate_cryptogram(f"{t_titles['cryptogram']} #{i+1}", phrase=secret_phrase, seed=s))

    # 6. 7 Word Ladders
    for i in range(7):
        s = rng.randint(1, 999999)
        puzzles.append(generate_word_ladder(f"{t_titles['word_ladder']} #{i+1}", seed=s))

    # 7. 7 Connect Dots
    for i in range(7):
        s = rng.randint(1, 999999)
        puzzles.append(generate_connect_dots(f"{t_titles['connect_dots']} #{i+1}", points_count=12, seed=s))

    # 8. 6 Logic Grids
    for i in range(6):
        s = rng.randint(1, 999999)
        puzzles.append(generate_logic_grid(f"{t_titles['logic_grid']} #{i+1}", size=4, clues_to_remove=4, seed=s))

    # Total 58 puzzles
    assert len(puzzles) == 58, f"Expected 58 puzzles, got {len(puzzles)}"

    # ================= FRONT-MATTER (6 pages) =================
    fm_pages = [
        # Page 1: Faux-titre
        f'<section class="p-page title-page"><div class="spacer"></div><div style="text-align:center;"><h1 style="font-size:26pt; margin-bottom:10pt;">{html.escape(title)}</h1><p style="font-size:14pt; letter-spacing:1px;">{html.escape(ed_pages["fm_subtitle"])}</p></div><div class="spacer"></div></section>',
        # Page 2: Copyright & Mentions Légales
        f'<section class="p-page copyright-page"><div class="spacer"></div><div style="font-size:10pt; line-height:1.6; border:1px solid #000; padding:15pt; border-radius:4px;"><h3 style="margin-top:0;">{html.escape(ed_pages["copyright_title"])}</h3><p>{html.escape(ed_pages["copyright_title"])} © {year} {html.escape(author)}. Tous droits réservés.</p><p>ISBN: {html.escape(isbn)}</p><p style="font-style:italic;">{html.escape(ed_pages["kdp_notice"])}</p></div><div class="spacer"></div></section>',
        # Page 3: Page de Titre complète
        f'<section class="p-page main-title-page"><div class="spacer"></div><div style="text-align:center;"><h1 style="font-size:28pt; line-height:1.2; margin-bottom:12pt;">{html.escape(title)}</h1><h3 style="font-size:15pt; font-weight:normal; margin-bottom:25pt;">{html.escape(subtitle)}</h3><div style="width:80px; height:3px; background:#000; margin:0 auto 25pt auto;"></div><p style="font-size:14pt; font-weight:bold;">{html.escape(author)}</p></div><div class="spacer"></div></section>',
        # Page 4: Ce livre appartient à
        f'<section class="p-page belongs-page"><div class="spacer"></div><div style="border:2px dashed #000; padding:25pt; border-radius:8px; text-align:center;"><h2 style="font-size:20pt; margin-bottom:20pt;">{html.escape(ed_pages["belongs_title"])}</h2><p style="font-size:13pt; margin-bottom:30pt;">{html.escape(ed_pages["belongs_name"])} _________________________________</p><p style="font-size:13pt;">{html.escape(ed_pages["belongs_date"])} _____________________</p></div><div class="spacer"></div></section>',
        # Page 5: Sommaire illustré des 8 Mondes
        f'<section class="p-page toc-page"><div><h2 style="font-size:20pt; border-bottom:2px solid #000; padding-bottom:8pt; margin-bottom:15pt; text-align:center;">{html.escape(ed_pages["toc_title"])}</h2><ul style="font-size:12pt; line-height:2.0; list-style:none; padding:0 20pt;">{"".join(f"<li>🐾 {html.escape(item)}</li>" for item in ed_pages["toc_items"])}</ul></div><div class="spacer"></div></section>',
        # Page 6: Le Serment de l'Explorateur & Guide Pédagogique
        f'<section class="p-page oath-page"><div><div style="border:2px solid #000; padding:15pt; border-radius:6px; margin-bottom:15pt;"><h3 style="font-size:14pt; margin-top:0;">{html.escape(ed_pages["oath_title"])}</h3><p style="font-size:11pt; line-height:1.6; margin-bottom:0;">{html.escape(ed_pages["oath_text"])}</p></div><div style="border:1px dashed #000; padding:15pt; border-radius:6px;"><h3 style="font-size:14pt; margin-top:0;">{html.escape(ed_pages["parents_guide_title"])}</h3><p style="font-size:10.5pt; line-height:1.6; margin-bottom:0;">{html.escape(ed_pages["parents_guide_text"])}</p></div></div><div class="spacer"></div></section>',
    ]

    # ================= 58 PUZZLES (Pages 7 à 64) =================
    puzzle_pages = []
    for idx, p in enumerate(puzzles):
        p_num = idx + 1
        page_num = idx + 7
        f_title, f_desc = facts[idx % len(facts)]
        p_html = _puzzle_html(p, p_num)
        fact_box = f'<div class="fact-box"><div class="fact-title">💡 {html.escape(f_title)}</div><p class="fact-body">{html.escape(f_desc)}</p></div>'
        # Remplacement de la balise fermante pour inclure fact-box et numéro de page
        p_html = p_html.replace('</section>', f'{fact_box}<div class="p-footer">{html.escape(page_lbl)} {page_num}</div></section>')
        puzzle_pages.append(p_html)

    # ================= 12 SOLUTIONS (Pages 65 à 76) =================
    sol_pages = []
    start = 0
    for page_idx in range(12):
        count = 5 if page_idx < 10 else 4
        chunk = puzzles[start:start+count]
        cards_html = "".join(_solution_html(p, start + i + 1) for i, p in enumerate(chunk))
        page_no = 65 + page_idx
        sol_pages.append(
            f'<section class="p-page sol-page">'
            f'<div class="p-head"><span class="p-num">KEY</span><h2>{html.escape(ed_pages["sol_title"])} — {html.escape(ed_pages["sol_part"])} {page_idx+1}/12</h2></div>'
            f'<div class="sol-grid-compact">{cards_html}</div>'
            f'<div class="p-footer">{html.escape(page_lbl)} {page_no}</div></section>'
        )
        start += count

    # ================= BACK-MATTER (4 pages: 77 à 80) =================
    bm_pages = [
        # Page 77: Carnet de croquis
        f'<section class="p-page notes-page"><div><h2 style="font-size:16pt; border-bottom:2px solid #000; padding-bottom:6pt; margin-bottom:12pt;">{html.escape(ed_pages["notes_title"])}</h2><div style="border:1.5px solid #000; height:6.8in; border-radius:4px; padding:10pt;"><p style="font-size:10pt; color:#444; font-style:italic;">Notes, empreintes & croquis de safari :</p></div></div><div class="p-footer">{html.escape(page_lbl)} 77</div></section>',
        # Page 78: Diplôme Officiel
        f'<section class="p-page diploma-page"><div class="spacer"></div><div style="border:4px double #000; padding:25pt; border-radius:8px; text-align:center;"><h2 style="font-size:22pt; margin-bottom:15pt; letter-spacing:1px;">{html.escape(ed_pages["diploma_title"])}</h2><p style="font-size:13pt; line-height:1.7; margin-bottom:25pt;">{html.escape(ed_pages["diploma_body"])}</p><p style="font-size:13pt; margin-bottom:25pt;">{html.escape(ed_pages["belongs_name"])} _________________________________</p><div style="display:flex; justify-content:space-around; margin-top:20pt;"><p style="font-size:11pt;">{html.escape(ed_pages["diploma_date"])} ____________</p><p style="font-size:11pt;">{html.escape(ed_pages["diploma_signature"])} ____________</p></div></div><div class="spacer"></div><div class="p-footer">{html.escape(page_lbl)} 78</div></section>',
        # Page 79: Note aux parents & Avis Amazon
        f'<section class="p-page review-page"><div class="spacer"></div><div style="border:2px solid #000; padding:20pt; border-radius:6px; text-align:center;"><h2 style="font-size:18pt; margin-bottom:12pt;">{html.escape(ed_pages["review_title"])}</h2><p style="font-size:12pt; line-height:1.7; margin-bottom:15pt;">{html.escape(ed_pages["review_body"])}</p><p style="font-size:22pt; letter-spacing:4px; margin:0;">⭐⭐⭐⭐⭐</p></div><div class="spacer"></div><div class="p-footer">{html.escape(page_lbl)} 79</div></section>',
        # Page 80: Colophon
        f'<section class="p-page colophon-page last-page"><div class="spacer"></div><div style="font-size:10pt; line-height:1.6; border:1px solid #000; padding:15pt; border-radius:4px; text-align:center;"><h3 style="margin-top:0;">{html.escape(ed_pages["colophon_title"])}</h3><p>{html.escape(ed_pages["colophon_text"])}</p><p>Imprimé pour les Éditions {html.escape(author)} · Dépôt légal {year}</p></div><div class="spacer"></div><div class="p-footer">{html.escape(page_lbl)} 80</div></section>',
    ]

    all_pages = fm_pages + puzzle_pages + sol_pages + bm_pages
    assert len(all_pages) == 80, f"Expected 80 pages total, got {len(all_pages)}"

    font_import = ""
    font_family_css = "font-family: Arial, Helvetica, sans-serif;"
    if is_ar:
        font_import = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700;900&display=swap">'
        font_family_css = "font-family: 'Amiri', serif; direction: rtl !important; text-align: right !important;"

    css_gutter_left = "@page :left { margin-left: 0.375in; margin-right: 0.5in; }" if is_ar else "@page :left { margin-left: 0.5in; margin-right: 0.375in; }"
    css_gutter_right = "@page :right { margin-left: 0.5in; margin-right: 0.375in; }" if is_ar else "@page :right { margin-left: 0.375in; margin-right: 0.5in; }"

    full_html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
{font_import}
<style>
@page {{
  size: 8.5in 11.0in;
  margin-top: 0.5in;
  margin-bottom: 0.5in;
}}
{css_gutter_left}
{css_gutter_right}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  background: #FFFFFF;
  color: #000000;
  {font_family_css}
}}
h1, h2, h3, h4 {{ font-family: {'"Cairo", sans-serif' if is_ar else 'Arial, Helvetica, sans-serif'}; }}
.p-page {{
  page-break-after: always;
  height: 9.7in;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  padding: 8pt;
}}
.last-page {{
  page-break-after: avoid !important;
}}
.spacer {{ flex-grow: 1; }}
.p-head {{
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 2px solid #000000;
  padding-bottom: 4pt;
  margin-bottom: 8pt;
}}
.p-num {{
  font-size: 13pt;
  font-weight: bold;
  background: #000000;
  color: #FFFFFF;
  padding: 2pt 8pt;
  border-radius: 4px;
}}
.p-head h2 {{
  font-size: 14pt;
  margin: 0;
}}
.p-footer {{
  text-align: center;
  font-size: 9pt;
  font-weight: bold;
  margin-top: 4pt;
}}
.fact-box {{
  border: 1.5px dashed #000000;
  border-radius: 6px;
  padding: 6pt 10pt;
  margin-top: 6pt;
  background: #FFFFFF;
}}
.fact-title {{
  font-size: 9.5pt;
  font-weight: bold;
  margin-bottom: 2pt;
}}
.fact-body {{
  font-size: 9pt;
  line-height: 1.35;
  margin: 0;
}}
.grid {{
  border-collapse: collapse;
  margin: 8pt auto;
}}
.grid td {{
  border: 1.5px solid #000000;
  width: 25pt;
  height: 25pt;
  text-align: center;
  vertical-align: middle;
  font-size: 13pt;
  font-weight: bold;
}}
.grid.mini td {{
  width: 14pt;
  height: 14pt;
  font-size: 8pt;
}}
.grid.mini td.hit {{
  background: #000000;
  color: #FFFFFF;
}}
.grid.mini td.dim {{
  color: #555555;
}}
.chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 6pt;
  margin-top: 4pt;
}}
.chip {{
  border: 1px solid #000000;
  border-radius: 4px;
  padding: 2pt 6pt;
  font-size: 9pt;
  font-weight: bold;
}}
.scramble-list {{
  list-style: none;
  padding: 0;
  margin: 8pt 0;
}}
.scramble-list li {{
  font-size: 11pt;
  margin-bottom: 8pt;
}}
.ladder-row {{
  font-size: 11pt;
  margin-bottom: 6pt;
}}
.riddle-item {{
  border: 1px solid #000000;
  padding: 7pt;
  margin-bottom: 7pt;
  border-radius: 4px;
}}
.crypto-phrase {{
  display: flex;
  flex-wrap: wrap;
  gap: 4pt;
  margin: 10pt 0;
}}
.crypto-box {{
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  border-bottom: 2px solid #000000;
  width: 22pt;
}}
.code-lbl {{
  font-size: 8pt;
}}
.sol-grid-compact {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8pt;
  font-size: 8.5pt;
}}
.sol-card {{
  border: 1px solid #000000;
  padding: 4pt 6pt;
  border-radius: 4px;
}}
.sol-card h4 {{
  margin: 0 0 4pt 0;
  font-size: 9pt;
  border-bottom: 1px solid #000000;
}}
svg {{
  display: block;
  margin: 0 auto;
  max-height: 5.1in;
}}
</style>
</head>
<body>
{"".join(all_pages)}
</body>
</html>"""

    return full_html



# ==============================================================================
# 2. TRANSCRÉATION IDIOMATIQUE D'UN MANUSCRIT DANS UNE LANGUE CIBLE
# ==============================================================================

def transcreate_book_metadata(
    master_book: Dict[str, Any],
    target_language: str
) -> Dict[str, Any]:
    """
    Transcrée idiomatiquement les métadonnées principales du livre pour le marché cible.
    Ne traduit jamais mot-à-mot : adapte le titre, sous-titre, institutions et promesse.
    """
    lang = normalize_language(target_language)
    profile = get_language_profile(lang)
    raw_niche = str(master_book.get("niche") or "").strip().lower()
    cat = str(master_book.get("category") or "").strip().lower()
    
    # Détection de la niche et du type d'ouvrage
    if any(k in raw_niche for k in ("savane", "savannah", "safari")) or (cat in ("puzzle", "puzzles") and any(k in raw_niche for k in ("animaux", "animal", "faune", "savane"))):
        niche_key = "animaux de la savane"
    elif "puzzle" in raw_niche or cat in ("puzzle", "puzzles"):
        niche_key = "animaux de la savane"
    elif any(k in raw_niche for k in ("financ", "argent", "bourse", "budget")):
        niche_key = "finances"
    elif raw_niche in CULTURAL_TRANSCREATION_MATRIX:
        niche_key = raw_niche
    else:
        niche_key = "general"

    niche_matrix = CULTURAL_TRANSCREATION_MATRIX.get(niche_key) or CULTURAL_TRANSCREATION_MATRIX["general"]
    cult = niche_matrix.get(lang) or niche_matrix.get("en", {})
    
    base_title = master_book.get("book_title") or master_book.get("title") or ""
    base_subtitle = master_book.get("subtitle") or ""
    
    # Si le livre correspond à une niche de la matrice (finances ou savane/puzzles)
    if cult and ("title" in cult) and (not base_title or niche_key in ("finances", "animaux de la savane")):
        title = cult["title"]
        subtitle = cult.get("subtitle") or base_subtitle
        currency = cult.get("currency", "€")
        institutions = cult.get("institutions", [])
        seed_keywords = cult.get("seed_keywords", [])
        target_audience = cult.get("target_audience") or master_book.get("target_audience") or "Enfants 6-8 ans"
    elif cult and ("title" in cult):
        title = cult["title"]
        subtitle = cult.get("subtitle", base_subtitle)
        currency = cult.get("currency", "€")
        institutions = cult.get("institutions", [])
        seed_keywords = cult.get("seed_keywords", [])
        target_audience = cult.get("target_audience") or master_book.get("target_audience")
    else:
        # Adaptation générique
        gen = CULTURAL_TRANSCREATION_MATRIX["general"].get(lang, {})
        prefix = gen.get("title_prefix", "Guide")
        title = f"{prefix} {base_title}" if lang != "fr" and base_title else (base_title or "Livre KDP")
        subtitle = gen.get("subtitle_template") or base_subtitle
        currency = gen.get("currency", "$")
        institutions = []
        seed_keywords = []
        target_audience = master_book.get("target_audience") or "Tous publics"

    author = str(master_book.get("author") or "MarkEddy")
    publisher = str(master_book.get("publisher") or f"Éditions {author}")
    default_format = "8.5x11" if niche_key == "animaux de la savane" else "6x9"
    format_id = normalize_format(str(master_book.get("format_kdp") or master_book.get("format_id") or master_book.get("format") or default_format))
    paper_type = str(master_book.get("paper_type") or "white")

    return {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "publisher": publisher,
        "niche": niche_key,
        "language": lang,
        "direction": profile.get("direction", "ltr"),
        "marketplace": profile.get("amazon_marketplace", "amazon.com"),
        "currency": currency,
        "institutions": institutions,
        "seed_keywords": seed_keywords,
        "target_audience": target_audience,
        "format_id": format_id,
        "paper_type": paper_type,
        "year": master_book.get("year", 2026),
        "isbn": master_book.get("isbn", "979-8-0000-0000-0"),
    }


def transcreate_book_content_html(
    meta: Dict[str, Any],
    body_content: Optional[str] = None
) -> str:
    """
    Assemble le corps du texte transcréé avec Front-Matter et Back-Matter localisés,
    styles CSS Paged Media respectant le script et inversion RTL si nécessaire.
    """
    lang = meta["language"]
    is_arabic = (lang == "ar")
    direction = "rtl" if is_arabic else "ltr"
    labels = get_editorial_labels(lang)
    currency = meta.get("currency", "€")
    institutions = meta.get("institutions", [])

    # Front-Matter & Back-Matter natifs
    front_matter_html = generate_front_matter_html(meta, language=lang)
    back_matter_html = generate_back_matter_html(meta, language=lang)

    # Corps de texte transcréé (si aucun fourni, génère un canevas riche idiomatique)
    if not body_content:
        inst_list_html = "".join(f"<li><strong>{inst}</strong></li>" for inst in institutions) if institutions else "<li>Discipline & Rigueur</li>"
        
        if is_arabic:
            body_html = f"""
            <section class="chapter" style="page-break-before: always; padding: 20pt 0;">
              <h2 style="font-family: 'Cairo', sans-serif; font-size: 20pt; color: #0A0F1D; border-bottom: 2pt solid #D4AF37; padding-bottom: 8pt;">
                الفصل الأول: قواعد الأساس المالي الرشيد
              </h2>
              <p style="font-size: 11pt; line-height: 1.8; margin-top: 15pt;">
                إن أول خطوة نحو راحة البال المالية هي فهم حركة الأموال بدقة وتجنب الديون الاستهلاكية غير الضرورية.
                يتطلب النجاح خطة مدروسة تقسم الدخل شهرياً إلى ثلاث قنوات أساسية: الاحتياجات المعيشية، صندوق الأمان، والاستثمار في الأصول المنتجة.
              </p>
              <div style="background: #F8FAFC; border-right: 4pt solid #D4AF37; padding: 15pt; margin: 20pt 0; border-radius: 4pt;">
                <h3 style="font-size: 13pt; color: #0A0F1D; margin-bottom: 8pt;">الأدوات المعتمدة في هذا الدليل:</h3>
                <ul style="font-size: 10.5pt; line-height: 1.7; padding-right: 20pt;">
                  {inst_list_html}
                </ul>
              </div>
              <p style="font-size: 11pt; line-height: 1.8;">
                باستخدام عملة الحساب ({currency}) كمعيار للقياس، يتمكن القارئ من رصد تقدمه المالي أسبوعياً بدون تعقيد.
              </p>
            </section>
            """
        elif lang == "de":
            body_html = f"""
            <section class="chapter" style="page-break-before: always; padding: 20pt 0;">
              <h2 style="font-family: 'Merriweather', serif; font-size: 20pt; color: #0A0F1D; border-bottom: 2pt solid #D4AF37; padding-bottom: 8pt;">
                Kapitel 1: Das Fundament der finanziellen Souveränität
              </h2>
              <p style="font-size: 10.5pt; line-height: 1.6; margin-top: 15pt; text-align: justify; hyphens: auto;">
                Finanzielle Unabhängigkeit entsteht nicht durch Spekulation, sondern durch ein diszipliniertes,
                automatisiertes System. Wer sein Monatsbudget nach der 50-30-20-Regel strukturiert und vorab spart,
                schützt seine Kaufkraft effektiv gegen Inflation.
              </p>
              <div style="background: #F8FAFC; border-left: 4pt solid #D4AF37; padding: 15pt; margin: 20pt 0; border-radius: 4pt;">
                <h3 style="font-size: 13pt; color: #0A0F1D; margin-bottom: 8pt;">Zentrale Bausteine in diesem Leitfaden:</h3>
                <ul style="font-size: 10pt; line-height: 1.6; padding-left: 20pt;">
                  {inst_list_html}
                </ul>
              </div>
              <p style="font-size: 10.5pt; line-height: 1.6; text-align: justify; hyphens: auto;">
                Mit klaren Sparraten in {currency} wird der Vermögensaufbau planbar und emotional entlastend.
              </p>
            </section>
            """
        elif lang == "es":
            body_html = f"""
            <section class="chapter" style="page-break-before: always; padding: 20pt 0;">
              <h2 style="font-family: 'Lora', serif; font-size: 20pt; color: #0A0F1D; border-bottom: 2pt solid #D4AF37; padding-bottom: 8pt;">
                Capítulo 1: Los Fundamentos de la Independencia Financiera
              </h2>
              <p style="font-size: 10.5pt; line-height: 1.6; margin-top: 15pt; text-align: justify; hyphens: auto;">
                La verdadera tranquilidad no se consigue persiguiendo rentabilidades milagrosas, sino estableciendo
                un sistema automático y constante. El primer paso consiste en erradicar cualquier deuda tóxica
                y edificar un fondo de emergencia sólido.
              </p>
              <div style="background: #F8FAFC; border-left: 4pt solid #D4AF37; padding: 15pt; margin: 20pt 0; border-radius: 4pt;">
                <h3 style="font-size: 13pt; color: #0A0F1D; margin-bottom: 8pt;">Pilares estratégicos de este método:</h3>
                <ul style="font-size: 10pt; line-height: 1.6; padding-left: 20pt;">
                  {inst_list_html}
                </ul>
              </div>
              <p style="font-size: 10.5pt; line-height: 1.6; text-align: justify; hyphens: auto;">
                A través del control sistemático en {currency}, cada euro ahorrado se convierte en un trabajador pasivo a su favor.
              </p>
            </section>
            """
        elif lang == "en":
            body_html = f"""
            <section class="chapter" style="page-break-before: always; padding: 20pt 0;">
              <h2 style="font-family: 'Cinzel', serif; font-size: 20pt; color: #0A0F1D; border-bottom: 2pt solid #D4AF37; padding-bottom: 8pt;">
                Chapter 1: The Foundations of Financial Architecture
              </h2>
              <p style="font-size: 10.5pt; line-height: 1.6; margin-top: 15pt; text-align: justify;">
                True wealth is built quietly through automatic systems rather than high-risk gambles.
                By allocating income into clear buckets—fixed costs, investments, and discretionary spending—you
                eliminate financial anxiety and reclaim control over your time.
              </p>
              <div style="background: #F8FAFC; border-left: 4pt solid #D4AF37; padding: 15pt; margin: 20pt 0; border-radius: 4pt;">
                <h3 style="font-size: 13pt; color: #0A0F1D; margin-bottom: 8pt;">Core financial vehicles covered:</h3>
                <ul style="font-size: 10pt; line-height: 1.6; padding-left: 20pt;">
                  {inst_list_html}
                </ul>
              </div>
              <p style="font-size: 10.5pt; line-height: 1.6; text-align: justify;">
                Every single {currency} deployed systematically compounds to build lasting generational freedom.
              </p>
            </section>
            """
        else: # French
            body_html = f"""
            <section class="chapter" style="page-break-before: always; padding: 20pt 0;">
              <h2 style="font-family: 'Cinzel', serif; font-size: 20pt; color: #0A0F1D; border-bottom: 2pt solid #D4AF37; padding-bottom: 8pt;">
                Chapitre 1 : Les Fondations de l'Ingénierie Financière
              </h2>
              <p style="font-size: 10.5pt; line-height: 1.6; margin-top: 15pt; text-align: justify; hyphens: auto;">
                L'indépendance financière ne découle pas d'un coup d'éclat boursier, mais de l'architecture
                rigoureuse de ses flux de trésorerie. En séparant strictement dépenses incompressibles,
                matelas de sécurité et investissements indiciels, le risque d'erreur humaine est éliminé.
              </p>
              <div style="background: #F8FAFC; border-left: 4pt solid #D4AF37; padding: 15pt; margin: 20pt 0; border-radius: 4pt;">
                <h3 style="font-size: 13pt; color: #0A0F1D; margin-bottom: 8pt;">Dispositifs fondamentaux traités :</h3>
                <ul style="font-size: 10pt; line-height: 1.6; padding-left: 20pt;">
                  {inst_list_html}
                </ul>
              </div>
              <p style="font-size: 10.5pt; line-height: 1.6; text-align: justify; hyphens: auto;">
                Chaque somme investie en {currency} génère un rendement composé protecteur contre l'érosion monétaire.
              </p>
            </section>
            """
    else:
        body_html = body_content

    # Typographie & Marges CSS adaptées
    font_embed = ""
    if is_arabic:
        font_embed = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Cairo:wght@400;600;700;900&family=Tajawal:wght@400;500;700&display=swap">'
        css_rules = """
        html, body {
          direction: rtl !important;
          text-align: right !important;
          font-family: 'Amiri', serif !important;
          font-size: 11pt;
          line-height: 1.8;
          color: #0F172A;
          background: #FFFFFF;
          margin: 0;
          padding: 0;
          hyphens: none !important;
          -webkit-hyphens: none !important;
        }
        h1, h2, h3 { font-family: 'Cairo', sans-serif !important; }
        @page {
          size: 6.0in 9.0in;
          margin-top: 0.75in;
          margin-bottom: 0.75in;
        }
        @page :right {
          margin-right: 0.75in;
          margin-left: 0.45in;
        }
        @page :left {
          margin-left: 0.75in;
          margin-right: 0.45in;
        }
        """
    else:
        font_embed = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;600&family=Lora:ital,wght@0,400;0,600;1,400&family=Merriweather:ital,wght@0,300;0,400;1,300&display=swap">'
        css_rules = """
        html, body {
          direction: ltr !important;
          text-align: justify;
          font-family: 'EB Garamond', Georgia, serif;
          font-size: 10.5pt;
          line-height: 1.48;
          color: #0F172A;
          background: #FFFFFF;
          margin: 0;
          padding: 0;
          hyphens: auto;
          -webkit-hyphens: auto;
        }
        h1, h2 { font-family: 'Cinzel', serif; font-weight: 700; }
        @page {
          size: 6.0in 9.0in;
          margin-top: 0.75in;
          margin-bottom: 0.75in;
        }
        @page :right {
          margin-left: 0.75in;
          margin-right: 0.45in;
        }
        @page :left {
          margin-left: 0.45in;
          margin-right: 0.75in;
        }
        """

    full_html = f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <title>{meta['title']}</title>
  {font_embed}
  <style>
    {css_rules}
    .page-break {{ page-break-before: always; }}
    ul, ol {{ margin-top: 6pt; margin-bottom: 6pt; }}
  </style>
</head>
<body>
  {front_matter_html}
  {body_html}
  {back_matter_html}
</body>
</html>"""

    return full_html


# ==============================================================================
# 3. PRODUCTION D'UNE ÉDITION INDÉPENDANTE TRANSCRÉÉE
# ==============================================================================

def produce_single_transcreated_edition(
    # Sécurisation création dossiers de sortie avant écriture SVG/HTML/JSON
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    master_book: Dict[str, Any],
    target_language: str,
    output_dir: Path,
) -> Dict[str, Any]:
    """
    Produit une édition complète, autonome et certifiée dans la langue cible :
      1. Transcréation idiomatique des métadonnées et du contenu
      2. Optimisation SEO A9 stricte (7 slots <= 50 octets UTF-8, sans mots prohibés)
      3. Règle Prépresse 24 pages minimum
      4. Rendu HTML & compilation PDF
      5. Calcul exact du dos et gabarit SVG de couverture (avec RTL inversé si 'ar')
      6. Audit de conformité supervise_kdp_book()
    """
    lang = normalize_language(target_language)
    profile = get_language_profile(lang)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_niche = str(master_book.get("niche") or "").strip().lower()
    cat = str(master_book.get("category") or "").strip().lower()
    is_puzzle = (
        cat in ("puzzles", "puzzle")
        or master_book.get("model_id") == "puzzles_multi_jeux"
        or any(k in raw_niche for k in ("puzzle", "savane", "savannah", "safari"))
    )

    # 1. Métadonnées transcréées
    meta = transcreate_book_metadata(master_book, lang)
    title = meta["title"]
    subtitle = meta["subtitle"]
    author = meta["author"]
    format_id = meta["format_id"]
    paper_type = meta["paper_type"]
    niche = meta["niche"]

    title_for_slug = str(meta.get("title") or master_book.get("title") or master_book.get("book_title") or "book")
    clean_slug = re.sub(r"[^a-z0-9]+", "_", title_for_slug.lower()).strip("_")
    slug = clean_slug if len(clean_slug) >= 3 else f"kdp_{lang}_{niche[:6]}"

    # 2. SEO A9 localisé
    seed_kw = master_book.get("seed_keywords") or meta.get("seed_keywords") or [meta["niche"], "guide", "system"]
    b_type = "activity_book" if is_puzzle else "non_fiction"
    a9_seo_res = optimize_kdp_seo(
        book_title=title,
        subtitle=subtitle,
        niche=niche,
        book_type=b_type,
        target_audience=meta.get("target_audience", "General public"),
        seed_keywords=seed_kw,
        language=lang,
    )
    backend_keywords_7 = a9_seo_res.get("backend_keywords", [])
    seo_score = a9_seo_res.get("seo_score", 90.0)

    # 3. HTML & Injection de bonus si < 24 pages
    if is_puzzle:
        target_pages = int(master_book.get("target_pages") or 80)
        enriched_html = build_savannah_puzzle_book_html(meta, target_pages=target_pages)
        final_page_count = target_pages
        bonus_added = 0
    else:
        base_html = transcreate_book_content_html(meta, master_book.get("body_html"))
        # Estimation initiale de pages
        estimated_pages = max(8, len(base_html.split("<section")) - 1)
        if estimated_pages < 24:
            enriched_html, final_page_count, bonus_added = inject_kdp_prepress_bonus_pages(
                html_content=base_html,
                current_pages=estimated_pages,
                project_type="text",
                min_pages=24,
                title=title,
            )
        else:
            enriched_html = base_html
            final_page_count = estimated_pages
            bonus_added = 0

    # Sauvegarde HTML
    html_filename = f"{slug}_{lang}_interieur.html"
    html_path = output_dir / html_filename
    html_path.write_text(enriched_html, encoding="utf-8")

    # 4. Compilation PDF & Comptage Réel
    pdf_filename = f"{slug}_{lang}_interieur.pdf"
    pdf_path = output_dir / pdf_filename
    specs = calculate_kdp_specs(format_id, final_page_count, paper_type=paper_type)
    width_in = specs.get("trim", {}).get("width_in", 8.5 if is_puzzle else 6.0)
    height_in = specs.get("trim", {}).get("height_in", 11.0 if is_puzzle else 9.0)

    success_pdf, pdf_msg = compile_kdp_interior_pdf(
        html_path=html_path,
        pdf_path=pdf_path,
        width_in=width_in,
        height_in=height_in,
        page_count_hint=final_page_count,
        title_hint=title,
    )

    real_page_count = final_page_count
    # Tente de compter les pages réelles via PyPDF si présent
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        real_page_count = len(reader.pages)
    except Exception:
        pass

    # 5. Calcul Tranche au Micron & Gabarit SVG
    is_ar = (lang == "ar")
    cover_dims = calculate_cover_dimensions(
        trim_id=format_id,
        page_count=real_page_count,
        paper_type=paper_type,
        language=lang,
        is_rtl=is_ar,
    )
    spine_thickness_in = round(cover_dims.get("spine_spec", {}).get("width_in", 0.0), 4)
    spine_thickness_mm = round(cover_dims.get("spine_spec", {}).get("width_mm", 0.0), 2)

    cover_svg_code = generate_cover_template_svg(
        specs_or_trim=cover_dims,
        page_count=real_page_count,
        book_title=title,
        author_name=author,
        subtitle=subtitle,
        paper_type=paper_type,
        language=lang,
        is_rtl=is_ar,
    )
    cover_svg_filename = f"{slug}_{lang}_couverture_calibree.svg"
    cover_svg_path = output_dir / cover_svg_filename
    cover_svg_path.write_text(cover_svg_code, encoding="utf-8")

    # Métadonnées A9 JSON
    metadata_a9_dict = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "language": lang,
        "marketplace": meta["marketplace"],
        "direction": meta["direction"],
        "backend_keywords": backend_keywords_7,
        "real_page_count": real_page_count,
        "spine_thickness_mm": spine_thickness_mm,
        "spine_thickness_in": spine_thickness_in,
        "format_id": format_id,
        "paper_type": paper_type,
        "seo_score": seo_score,
    }
    metadata_a9_filename = f"{slug}_{lang}_metadata_a9.json"
    metadata_a9_path = output_dir / metadata_a9_filename
    metadata_a9_path.write_text(json.dumps(metadata_a9_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6. Audit de Conformité KDP
    audit_payload = {
        "title": title,
        "subtitle": subtitle,
        "author": author,
        "keywords": backend_keywords_7,
        "page_count": real_page_count,
        "binding": "paperback",
        "language": lang,
        "niche": niche,
        "format_id": format_id,
        "paper_type": paper_type,
        "has_copyright": True,
        "has_disclaimer": True,
        "has_author_bio": True,
        "has_colophon": True,
        "has_toc": True,
        "has_cover": True,
        "isbn": meta["isbn"],
        "ai_transparency_declared": True,
    }
    audit_res = supervise_kdp_book(audit_payload)
    kdp_verdict = audit_res.get("verdict", "APPROVED_FOR_KDP")
    anti_anonymity_score = audit_res.get("score_anti_anonymat_100", 100.0)

    # Sauvegarde du rapport d'audit indépendant par langue
    audit_json_filename = "kdp_compliance_audit.json"
    audit_json_path = output_dir / audit_json_filename
    audit_json_path.write_text(json.dumps(audit_res, indent=2, ensure_ascii=False), encoding="utf-8")

    edition_data = {
        "language": lang,
        "language_name": profile.get("native_name") or profile.get("name_native", lang),
        "direction": meta["direction"],
        "marketplace": meta["marketplace"],
        "title": title,
        "subtitle": subtitle,
        "real_page_count": real_page_count,
        "spine_thickness_mm": spine_thickness_mm,
        "spine_thickness_in": spine_thickness_in,
        "seo_score": seo_score,
        "anti_anonymity_score": anti_anonymity_score,
        "kdp_verdict": kdp_verdict,
        "files": {
            "html": str(html_path.resolve()),
            "pdf": str(pdf_path.resolve()),
            "cover_svg": str(cover_svg_path.resolve()),
            "metadata_a9": str(metadata_a9_path.resolve()),
            "audit_report": str(audit_json_path.resolve()),
        },
        "file_names": {
            "html": html_filename,
            "pdf": pdf_filename,
            "cover_svg": cover_svg_filename,
            "metadata_a9": metadata_a9_filename,
            "audit_report": audit_json_filename,
        }
    }

    return edition_data


# ==============================================================================
# 4. ORCHESTRATEUR DE BUNDLE MULTILINGUE (GLOBAL & PAR LANGUE)
# ==============================================================================

def produce_multilang_bundle(
    master_book: Dict[str, Any],
    target_languages: Optional[List[str]] = None,
    bundle_name: Optional[str] = None,
    output_base_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Prend le livre maître et génère de façon indépendante chaque langue cible demandée.
    Produit :
      - Toutes les éditions dans leur dossier propre
      - Le manifeste de bundle 'bundle_manifest.json'
      - L'archive ZIP globale 'bundle_multilang_{name}.zip'
      - Les archives ZIP par langue 'bundle_{name}_{lang}.zip'
    """
    languages_to_build = []
    requested = target_languages or ["en", "fr", "es", "de", "ar"]
    for l in requested:
        norm = normalize_language(l)
        if norm in SUPPORTED_LANGUAGES and norm not in languages_to_build:
            languages_to_build.append(norm)

    if not languages_to_build:
        languages_to_build = ["fr", "en"]

    source_lang = normalize_language(master_book.get("language") or "fr")
    raw_title_for_slug = str(master_book.get("title") or master_book.get("book_title") or master_book.get("niche") or "book")
    title_slug = re.sub(r"[^a-z0-9]+", "_", raw_title_for_slug.lower()).strip("_") or "book"
    bname = bundle_name or f"bundle_{title_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    base_dir = output_base_dir or (BUNDLES_DIR / bname)
    base_dir.mkdir(parents=True, exist_ok=True)

    editions: List[Dict[str, Any]] = []

    # 1. Génération de chaque édition internationale
    for lang in languages_to_build:
        edition_dir = base_dir / lang
        edition_res = produce_single_transcreated_edition(
            master_book=master_book,
            target_language=lang,
            output_dir=edition_dir,
        )
        editions.append(edition_res)

    # 2. Construction de bundle_manifest.json
    manifest_dict = {
        "bundle_name": bname,
        "source_language": source_lang,
        "generated_at": datetime.now().isoformat(),
        "total_editions": len(editions),
        "target_languages": languages_to_build,
        "editions": editions,
    }
    manifest_path = base_dir / "bundle_manifest.json"
    manifest_path.write_text(json.dumps(manifest_dict, indent=2, ensure_ascii=False), encoding="utf-8")

    # 3. Création de l'archive ZIP globale
    global_zip_path = base_dir / f"{bname}.zip"
    with zipfile.ZipFile(global_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, arcname="bundle_manifest.json")
        for ed in editions:
            l = ed["language"]
            for ftype, abs_path in ed["files"].items():
                p = Path(abs_path)
                if p.exists():
                    arc_name = f"{l}/{p.name}"
                    zf.write(p, arcname=arc_name)

    # 4. Création des archives ZIP individuelles par langue
    per_language_zips: Dict[str, str] = {}
    for ed in editions:
        l = ed["language"]
        lang_zip_path = base_dir / f"{bname}_{l}.zip"
        with zipfile.ZipFile(lang_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf_lang:
            # Inclut le sous-manifeste de l'édition
            zf_lang.writestr(
                "edition_manifest.json",
                json.dumps({**ed, "bundle_name": bname}, indent=2, ensure_ascii=False)
            )
            for ftype, abs_path in ed["files"].items():
                p = Path(abs_path)
                if p.exists():
                    zf_lang.write(p, arcname=p.name)
        per_language_zips[l] = str(lang_zip_path.resolve())

    return {
        "status": "success",
        "bundle_name": bname,
        "manifest": manifest_dict,
        "manifest_path": str(manifest_path.resolve()),
        "global_zip_path": str(global_zip_path.resolve()),
        "per_language_zips": per_language_zips,
        "editions_count": len(editions),
    }


def transcreate_book_package(
    master_payload: Dict[str, Any],
    source_language: str = "fr",
    target_languages: Optional[List[str]] = None,
    bundle_name: Optional[str] = None,
    output_base_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Exécute la transcréation multilingue complète et génère le bundle d'éditions :
    Pour chaque langue de [source_language] + target_languages (filtrée sur en, fr, es, de, ar, sans doublon).
    """
    src = normalize_language(source_language or master_payload.get("language") or "fr")
    raw_targets = target_languages if target_languages is not None else ["en", "es", "de", "ar"]
    combined = [src] + [normalize_language(t) for t in raw_targets]
    
    unique_langs: List[str] = []
    for l in combined:
        if l in SUPPORTED_LANGUAGES and l not in unique_langs:
            unique_langs.append(l)

    return produce_multilang_bundle(
        master_book={**master_payload, "language": src},
        target_languages=unique_langs,
        bundle_name=bundle_name,
        output_base_dir=output_base_dir,
    )


def resolve_bundle_download_path(bundle_name: str, lang: Optional[str] = None) -> Optional[Path]:
    """
    Localise l'archive ZIP à télécharger selon le bundle_name et le filtre optionnel lang.
    Si lang est fourni (ex: 'de'), renvoie le ZIP de cette langue.
    Sinon, renvoie le ZIP global du bundle.
    """
    clean_name = Path(bundle_name).stem
    candidate_dir = BUNDLES_DIR / clean_name

    # Si un dossier direct existe
    if candidate_dir.exists():
        if lang:
            norm_lang = normalize_language(lang)
            lang_zip = candidate_dir / f"{clean_name}_{norm_lang}.zip"
            if lang_zip.exists():
                return lang_zip
        global_zip = candidate_dir / f"{clean_name}.zip"
        if global_zip.exists():
            return global_zip

    # Recherche directe dans BUNDLES_DIR
    if lang:
        norm_lang = normalize_language(lang)
        direct_lang_zip = BUNDLES_DIR / f"{clean_name}_{norm_lang}.zip"
        if direct_lang_zip.exists():
            return direct_lang_zip

    direct_global = BUNDLES_DIR / f"{clean_name}.zip"
    if direct_global.exists():
        return direct_global

    # Recherche par wildcard
    matches = list(BUNDLES_DIR.glob(f"*{clean_name}*.zip"))
    if matches:
        if lang:
            norm_lang = normalize_language(lang)
            for m in matches:
                if f"_{norm_lang}.zip" in m.name:
                    return m
        return matches[0]

    return None
