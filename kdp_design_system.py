"""
kdp_design_system.py - Système de Design & Charte Graphique Haute Couture pour Amazon KDP.
Définit les palettes de prestige, les accords typographiques d'exception,
les métriques du nombre d'or et les ornements visuels pour des livres haut de gamme.
"""

# ==============================================================================
# 🎨 1. PALETTES CHROMATIQUES DE PRESTIGE (LUXURY COLOR PALETTES)
# ==============================================================================

PALETTES_PRESTIGE = {
    "obsidian_gold": {
        "nom": "Obsidienne & Or Impérial",
        "niche": "Finances, Leadership, Stratégie, Pouvoir, Entreprise",
        "primaire": "#0A0F1D",       # Bleu nuit / Noir obsidienne profond
        "secondaire": "#1E293B",     # Ardoise feutrée pour le dos
        "accent": "#D4AF37",         # Or impérial chaud (Dorure)
        "texte_clair": "#F8FAFC",    # Blanc lin soyeux
        "texte_sourd": "#94A3B8",    # Gris argenté doux
        "encadre_fond": "#F7F9FB",   # Fond des encadrés intérieurs
        "encadre_bordure": "#B8860B" # Or brossé
    },
    "emerald_champagne": {
        "nom": "Émeraude Royale & Champagne",
        "niche": "Immobilier, Richesse durable, Nature, Bien-être d'élite",
        "primaire": "#062C22",       # Vert émeraude sombre et noble
        "secondaire": "#0D3D32",     # Teinte dos émeraude profonde
        "accent": "#C5A059",         # Champagne doré
        "texte_clair": "#FAF7F2",    # Blanc ivoire
        "texte_sourd": "#8BA89F",    # Sauge doux
        "encadre_fond": "#F3F7F5",   # Fond intérieur menthe très douce
        "encadre_bordure": "#2D6A4F" # Vert noble
    },
    "royal_sapphire": {
        "nom": "Saphir Majestueux & Argent Polaire",
        "niche": "Technologie, IA, Science, Méthode, Efficacité, Ingénierie",
        "primaire": "#0B192C",       # Saphir abysse
        "secondaire": "#1E3E62",     # Bleu nuit acier
        "accent": "#00ADB5",         # Cyan métallisé / Argent vif
        "texte_clair": "#FFFFFF",    # Blanc pur
        "texte_sourd": "#9BA8B8",    # Gris métal brossé
        "encadre_fond": "#F0F4F8",   # Fond givré très doux
        "encadre_bordure": "#1E3E62" # Bleu marine profond
    },
    "grand_cru_rose": {
        "nom": "Bordeaux Grand Cru & Or Rose",
        "niche": "Psychologie, Relations, Philosophie, Développement personnel d'élite",
        "primaire": "#2C0B0E",       # Lie-de-vin velouté profond
        "secondaire": "#421217",     # Bordeaux dos
        "accent": "#E8C5C8",         # Or rose nacré
        "texte_clair": "#FFF8F8",    # Blanc poudré
        "texte_sourd": "#C49A9E",    # Cacao rose sourd
        "encadre_fond": "#FCF5F5",   # Fond rose poudré subtil
        "encadre_bordure": "#841426" # Grenat noble
    }
}

# ==============================================================================
# 🔤 2. DUOS TYPOGRAPHIQUES D'ÉDITION HAUT DE GAMME
# ==============================================================================

ACCORDS_TYPOGRAPHIQUES = {
    "classic_heritage": {
        "nom": "Héritage Classique (Style Pléiade & Gallimard)",
        "titres": "'Georgia', 'Garamond', 'Palatino', serif",
        "corps": "'Garamond', 'Georgia', 'Times New Roman', serif",
        "taille_corps": "10.5pt",
        "interlignage": "1.45",
        "drop_caps": True,
        "style_titres": "uppercase; letter-spacing: 2px; font-weight: 700;"
    },
    "modern_authority": {
        "nom": "Autorité Moderne (Style Harvard Business Review)",
        "titres": "'Helvetica Neue', 'Arial', 'Montserrat', sans-serif",
        "corps": "'Georgia', 'Merriweather', serif",
        "taille_corps": "10pt",
        "interlignage": "1.5",
        "drop_caps": True,
        "style_titres": "letter-spacing: 0.5px; font-weight: 800;"
    }
}

# ==============================================================================
# 📐 3. STANDARDS DIMENSIONNELS AMAZON KDP BROCHÉ 6x9 POUCES
# ==============================================================================

KDP_METRICS_6X9 = {
    "trim_width_in": 6.0,
    "trim_height_in": 9.0,
    "bleed_in": 0.125,
    "gutter_margin_in": 0.85,    # Marge intérieure de reliure pour ouverture parfaite
    "outside_margin_in": 0.55,   # Marge extérieure
    "top_margin_in": 0.75,
    "bottom_margin_in": 0.75,
    "dpi": 300,
    "epaisseur_page_blanc": 0.002252, # Pouces par page (White Paper)
    "epaisseur_page_creme": 0.0025,   # Pouces par page (Cream Paper)
    "isbn_zone_largeur_px": 600,
    "isbn_zone_hauteur_px": 360
}

# ==============================================================================
# ❦ 4. ORNEMENTS & SÉPARATEURS VISUELS DE PRESTIGE
# ==============================================================================

ORNEMENTS_EDITION = {
    "fleuron": "❦",
    "etoile_triomphale": "✦ ✦ ✦",
    "losange_dore": "◆",
    "separateur_fin": "— ✦ —"
}

def get_palette_par_defaut(nom: str = "obsidian_gold") -> dict:
    return PALETTES_PRESTIGE.get(nom, PALETTES_PRESTIGE["obsidian_gold"])
