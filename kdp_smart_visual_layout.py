"""
Moteur d'Orchestration Visuelle et Typographique Intelligent (KDP & Ouvrages Scientifiques/Sci-Fi).
- Analyse sémantique du texte (densité, concepts visuels, scènes narratives).
- Prise de décision heuristique : Où placer une figure ? Où s'abstenir pour préserver le rythme ?
- Sélection adaptative du gabarit : Pleine page (Hero/Cinématique), Demi-page (Figure technique),
  ou Flottant latéral (Callout/Focus).
- Injection HTML/CSS Paged Media 6x9 pouces avec figures légendées numérotées.
"""

import re
import json
from pathlib import Path

# Lexiques sémantiques pour détecter l'intensité visuelle
MOTS_CLES_CINEMATIQUES = {
    "vaisseau", "horizon", "orbite", "nébuleuse", "galaxie", "trou noir", "quasar",
    "paysage", "ruines", "cataclysme", "explosion", "lumière", "titan", "abîme",
    "foule", "megastructure", "dôme", "silicium", "station", "surface", "atmosphère"
}

MOTS_CLES_TECHNIQUES = {
    "orbite", "trajectoire", "courbure", "spectre", "équation", "vecteur", "fréquence",
    "densité", "pression", "gradient", "diagramme", "schéma", "réacteur", "matière",
    "antimatière", "énergie", "gravité", "flux", "singularité", "champ"
}

# Lieux où il NE FAUT PAS mettre d'image (introspection, dialogues intenses)
MOTS_CLES_ABSTRAITS_OU_DIALOGUES = {
    "pensa", "demanda", "répondit", "chuchota", "hésita", "conscience", "philosophie",
    "morale", "doute", "souvenir", "sentiment", "regret", "silence", "regarda"
}


class AnalyseurPlacementVisuel:
    def __init__(self, seuil_intervalle_mots=1100):
        # Espace minimum entre deux visuels pour ne pas noyer le lecteur
        self.dernier_placement_mots = -seuil_intervalle_mots
        self.seuil_intervalle_mots = seuil_intervalle_mots
        self.index_figure = 1

    def evaluer_paragraphe(self, paragraphe: str, position_mots: int):
        """
        Détermine si un paragraphe appelle une illustration et sélectionne le format adapté.
        """
        # Règle de respiration : Ne pas placer deux visuels trop proches
        if (position_mots - self.dernier_placement_mots) < self.seuil_intervalle_mots:
            return None

        mots = re.findall(r'\b\w+\b', paragraphe.lower())
        if len(mots) < 40:
            return None

        score_cinematique = sum(1 for m in mots if m in MOTS_CLES_CINEMATIQUES)
        score_technique = sum(1 for m in mots if m in MOTS_CLES_TECHNIQUES)
        score_abstrait = sum(1 for m in mots if m in MOTS_CLES_ABSTRAITS_OU_DIALOGUES)

        # RÈGLE D'ABSTENTION : Dialogue ou introspection pure = ZÉRO image
        if score_abstrait > (score_cinematique + score_technique):
            return None

        # 1. SCÈNE CINÉMATIQUE MAJEURE -> Pleine page (Hero)
        if score_cinematique >= 4 and len(mots) >= 70:
            self.dernier_placement_mots = position_mots
            fig_data = {
                "type": "hero_cinematique",
                "numero": self.index_figure,
                "legende": f"Figure {self.index_figure}. Panorama d'observation synoptique de la zone stellaire."
            }
            self.index_figure += 1
            return fig_data

        # 2. DÉMONSTRATION TECHNIQUE / SCIENTIFIQUE -> Demi-page horizontale
        elif score_technique >= 3:
            self.dernier_placement_mots = position_mots
            fig_data = {
                "type": "figure_scientifique",
                "numero": self.index_figure,
                "legende": f"Figure {self.index_figure}. Modélisation cinétique et relevé dimensionnel des gradients d'énergie."
            }
            self.index_figure += 1
            return fig_data

        return None


def convertir_manuscrit_en_mise_en_page_illustree(fichier_md: Path, fichier_html: Path):
    if not fichier_md.exists():
        print(f"❌ Fichier source introuvable : {fichier_md}")
        return

    contenu = fichier_md.read_text(encoding="utf-8")
    paragraphes = contenu.split("\n\n")

    analyseur = AnalyseurPlacementVisuel(seuil_intervalle_mots=1100)
    mots_cumules = 0
    blocs_html = []

    # Feuille de style Paged Media 6x9 pouces adaptée à l'édition illustrée
    css_style = """
    @page {
        size: 6in 9in;
        margin: 0.85in 0.65in 0.8in 0.85in;
        @bottom-center {
            content: counter(page);
            font-family: 'EB Garamond', 'Garamond', serif;
            font-size: 9pt;
            color: #475569;
        }
    }
    body {
        font-family: 'EB Garamond', 'Georgia', serif;
        font-size: 10.5pt;
        line-height: 1.5;
        color: #0f172a;
        text-align: justify;
    }
    h1, h2, h3 {
        font-family: 'Cinzel', 'Trajan Pro', serif;
        text-align: center;
        page-break-after: avoid;
    }
    h1 {
        page-break-before: always;
        margin-top: 1.6in;
        margin-bottom: 1.2in;
        font-size: 20pt;
        letter-spacing: 2px;
    }
    p {
        margin: 0;
        text-indent: 1.3em;
    }
    
    /* GABARIT 1 : HERO CINÉMATIQUE (PLEINE PAGE / FORMAT SPECTACULAIRE) */
    figure.hero_cinematique {
        page-break-inside: avoid;
        page-break-before: always;
        margin: 0 auto 1.6em auto;
        text-align: center;
    }
    figure.hero_cinematique img {
        width: 100%;
        max-height: 5.6in;
        object-fit: cover;
        border-radius: 2px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.18);
    }
    
    /* GABARIT 2 : FIGURE SCIENTIFIQUE (DEMI-PAGE / COUPE TECHNIQUE) */
    figure.figure_scientifique {
        page-break-inside: avoid;
        margin: 1.8em 0;
        text-align: center;
        background: #f8fafc;
        border-top: 1px solid #cbd5e1;
        border-bottom: 1px solid #cbd5e1;
        padding: 12px 0 8px 0;
    }
    figure.figure_scientifique img {
        width: 92%;
        max-height: 3.4in;
        object-fit: contain;
    }
    
    /* LÉGENDES RIGUREUSES DES FIGURES */
    figcaption {
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 8pt;
        line-height: 1.35;
        color: #475569;
        margin-top: 8px;
        text-align: justify;
        padding: 0 20px;
    }
    figcaption strong {
        color: #0f172a;
        text-transform: uppercase;
        font-size: 7.5pt;
        letter-spacing: 0.5px;
    }
    """

    blocs_html.append(f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css_style}</style></head><body>")

    for p in paragraphes:
        p_clean = p.strip()
        if not p_clean:
            continue

        if p_clean.startswith("#"):
            blocs_html.append(f"<h1>{p_clean.lstrip('#').strip()}</h1>")
            continue

        mots_p = len(p_clean.split())
        mots_cumules += mots_p

        # Évaluation intelligente du placement
        decision_visuelle = analyseur.evaluer_paragraphe(p_clean, mots_cumules)

        if decision_visuelle:
            type_fig = decision_visuelle["type"]
            num_fig = decision_visuelle["numero"]
            legende = decision_visuelle["legende"]

            # Remplacement par vos images locales générées (Dossier images/)
            image_src = f"images/figure_{num_fig:02d}.png"

            blocs_html.append(f"""
            <figure class="{type_fig}">
                <img src="{image_src}" alt="Figure {num_fig}">
                <figcaption><strong>Figure {num_fig}.</strong> {legende}</figcaption>
            </figure>
            """)

        blocs_html.append(f"<p>{p_clean}</p>")

    blocs_html.append("</body></html>")

    fichier_html.write_text("\n".join(blocs_html), encoding="utf-8")
    print(f"✅ Maquette visuelle intelligente générée : {fichier_html.resolve()}")
    print(f"📊 Total des illustrations placées : {analyseur.index_figure - 1}")


if __name__ == "__main__":
    source_md = Path("manuscrit_enrichi.md") if Path("manuscrit_enrichi.md").exists() else Path("manuscrit_complet.md")
    destination_html = Path("livre_science_fiction_illustre.html")
    convertir_manuscrit_en_mise_en_page_illustree(source_md, destination_html)