"""
kdp_extensions/interior_layout_master.py — « kdp-interior-layout-master »
Orchestrateur unique de la mise en page intérieure KDP (sur-ensemble zéro-casse).

Chaîne : correctif pré-presse (kdp_layout_fixer) → composition 6x9/16 formats
(kdp_universal_publishing_engine) → inspection (kdp_layout_inspector).

Aucun fichier existant n'est modifié : le manuscrit corrigé est écrit à côté
de l'original en `*_corrige.md`, les signatures historiques restent intactes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

THEMES_ENFANTS = ("enfant", "enfants", "4-8", "4 ans", "coloriage", "jeunesse", "kids")


def choisir_thematique(public_cible: Optional[str] = None,
                       thematique_forcee: Optional[str] = None,
                       format_kdp: Optional[str] = None) -> str:
    """Sélectionne la charte typographique ENFANT_EDUCATIF ou NON_FICTION."""
    if thematique_forcee:
        return thematique_forcee.strip().upper()
    indice = " ".join(filter(None, [public_cible or "", format_kdp or ""])).lower()
    if any(mot in indice for mot in THEMES_ENFANTS):
        return "ENFANT_EDUCATIF"
    return "NON_FICTION"


def composer_interieur(
    chemin_manuscrit: str,
    chemin_sortie_html: str,
    format_kdp: str = "6x9",
    thematique_choisie: Optional[str] = None,
    titre_livre: Optional[str] = None,
    public_cible: Optional[str] = None,
    font_family: Optional[str] = None,
    appliquer_correctifs: bool = True,
    auditer: bool = False,
) -> Dict[str, Any]:
    """
    Compose l'intérieur print-ready et retourne un rapport de traçabilité.

    Parameters
    ----------
    chemin_manuscrit : manuscrit Markdown source (jamais écrasé).
    chemin_sortie_html : HTML print-ready de destination.
    format_kdp : identifiant du référentiel 16 formats (défaut 6x9).
    thematique_choisie : NON_FICTION | ENFANT_EDUCATIF | COLORIAGE_WORKBOOK (auto si absent).
    titre_livre : titre imprimé en page de garde (défaut « LIVRE KDP »).
    public_cible : utilisé pour sélectionner automatiquement la charte enfant.
    font_family : police Google Fonts choisie dans le dashboard (informationnelle).
    appliquer_correctifs : active kdp_layout_fixer sur une COPIE du manuscrit.
    auditer : lance kdp_layout_inspector.inspecter_html sur le HTML produit.
    """
    source = Path(chemin_manuscrit)
    sortie = Path(chemin_sortie_html)
    sortie.parent.mkdir(parents=True, exist_ok=True)

    texte_original = source.read_text(encoding="utf-8")
    rapport: Dict[str, Any] = {
        "manuscrit_source": str(source),
        "manuscrit_corrige": str(source),
        "html_sortie": str(sortie),
        "format_kdp": format_kdp,
        "correctifs": {},
        "police": font_family or "Playfair Display",
    }
    manuscrit_a_composer = source

    if appliquer_correctifs:
        try:
            from kdp_layout_fixer import reparer_texte_markdown
            texte_corrige, stats = reparer_texte_markdown(texte_original)
            corrige = source.with_name(f"{source.stem}_corrige.md")
            corrige.write_text(texte_corrige, encoding="utf-8")
            manuscrit_a_composer = corrige
            rapport["manuscrit_corrige"] = str(corrige)
            rapport["correctifs"] = stats
        except Exception as e:
            rapport["correctifs"] = {"erreur": str(e)}

    thematique = choisir_thematique(public_cible, thematique_choisie, format_kdp)
    rapport["thematique"] = thematique

    from kdp_universal_publishing_engine import compiler_livre_sur_mesure

    compiler_livre_sur_mesure(
        chemin_manuscrit=str(manuscrit_a_composer),
        chemin_sortie_html=str(sortie),
        format_choisi=format_kdp,
        thematique_choisie=thematique,
        titre_livre=titre_livre or "LIVRE KDP",
    )

    if auditer:
        try:
            from kdp_layout_inspector import inspecter_html
            rapport["audit"] = inspecter_html(sortie)
        except Exception as e:
            rapport["audit"] = {"erreur": str(e)}

    return rapport


__all__ = ["composer_interieur", "choisir_thematique"]
