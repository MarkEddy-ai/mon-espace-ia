"""
cover_prompts.py - Générateur de Prompts Visuels pour Midjourney v6, Flux.1 et DALL-E 3.
Conçoit des invites artistiques haut de gamme pour illustrer les couvertures de livres KDP.
"""

import json
import argparse
from pathlib import Path
from kdp_design_system import PALETTES_PRESTIGE, get_palette_par_defaut

BLUEPRINT_PATH = Path("book_blueprint.json")

STYLES_VISUELS = {
    "obsidian_gold": {
        "fond": "dark obsidian black marble with fine liquid gold veins, volumetric lighting",
        "symbolique": "minimalist 3D geometric golden polyhedral structure floating in deep navy darkness",
        "photographique": "high-end luxury architectural interior, dramatic side lighting, black slate and brushed brass accents"
    },
    "emerald_champagne": {
        "fond": "deep royal emerald green velvet background with delicate champagne gold foil patterns",
        "symbolique": "stylized origami golden tree rooted in deep emerald stone, clean editorial photography",
        "photographique": "modern architectural luxury villa with lush green botanical elements and warm champagne lighting"
    },
    "royal_sapphire": {
        "fond": "abyssal sapphire blue gradient with floating crystalline platinum geometric particles",
        "symbolique": "futuristic glowing neural nodes connected by thin silver threads, clean minimalist tech",
        "photographique": "sleek aerodynamic dark metallic sculpture with subtle cyan rim lighting, studio setup"
    },
    "grand_cru_rose": {
        "fond": "luxurious deep burgundy velvet texture with soft rose gold metallic reflections",
        "symbolique": "abstract continuous single-line rose gold sculpture representing personal growth and clarity",
        "photographique": "fine art portrait photography in silhouette, warm amber and rose gold cinematic backlight"
    }
}

def generer_prompts_visuels(palette_name: str = "obsidian_gold") -> dict:
    palette = get_palette_par_defaut(palette_name)
    titre = "Livre sans titre"
    niche = "Développement personnel et réussite"
    
    if BLUEPRINT_PATH.exists():
        bp = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
        titre = bp.get("titre", titre)
        niche = bp.get("promesse_client", niche)

    ambiance = STYLES_VISUELS.get(palette_name, STYLES_VISUELS["obsidian_gold"])

    prompts = {
        "variante_1_texture_fond": (
            f"Luxury book cover background texture, {ambiance['fond']}, "
            f"ultra-clean space in the upper half for typography, subtle depth of field, "
            f"shot on Hasselblad 100MP, award-winning editorial design, cinematic lighting, 8k resolution --ar 2:3 --v 6.0"
        ),
        "variante_2_concept_symbolique": (
            f"Central luxury symbol for a book about {niche}, {ambiance['symbolique']}, "
            f"dark isolated clean background in {palette['primaire']}, hyper-detailed, elegant minimalism, "
            f"octane render, unreal engine 5, ray tracing, studio lighting --ar 2:3 --v 6.0"
        ),
        "variante_3_photographie_prestige": (
            f"Editorial book cover photograph, {ambiance['photographique']}, "
            f"color palette {palette['primaire']} and {palette['accent']}, "
            f"shot with 85mm f/1.4 lens, clean minimalist composition, plenty of negative space at the top --ar 2:3 --v 6.0"
        )
    }

    print("\n" + "=" * 70)
    print(f"🎨 PROMPTS ARTISTIQUES COUVERTURE ({palette['nom'].upper()})")
    print(f"📖 Livre : {titre}")
    print("=" * 70)
    print("\n[OPTION 1 : TEXTURE DE FOND ÉLÉGANTE (Prêt pour Midjourney)]")
    print(prompts["variante_1_texture_fond"])
    print("\n[OPTION 2 : SYMBOLE 3D HAUTE COUTURE (Prêt pour Midjourney)]")
    print(prompts["variante_2_concept_symbolique"])
    print("\n[OPTION 3 : PHOTOGRAPHIE ÉDITORIALE PRESTIGE (Prêt pour Midjourney)]")
    print(prompts["variante_3_photographie_prestige"])
    print("=" * 70 + "\n")

    return prompts

def main():
    parser = argparse.ArgumentParser(description="Générateur de prompts visuels Midjourney / Flux.")
    parser.add_argument("--palette", choices=list(PALETTES_PRESTIGE.keys()), default="obsidian_gold")
    args = parser.parse_args()
    generer_prompts_visuels(args.palette)

if __name__ == "__main__":
    main()
