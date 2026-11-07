import re
from pathlib import Path
from collections import Counter

MANUSCRIT_PATH = Path("manuscrit_complet.md")
MANUSCRIT_OPTI_PATH = Path("manuscrit_ameliore.md")

# Mots ou tics fréquents à surveiller
TICS_IA = [
    "il est important de noter", "en conclusion", "comme nous l'avons vu",
    "dans ce chapitre", "il convient de", "crucial", "fondamental", "véritable"
]

def appliquer_micro_typographie(texte: str) -> str:
    """Insère des espaces insécables devant la ponctuation double et les symboles monétaires."""
    # Remplacement des espaces simples avant : ; ! ? % € par une espace insécable
    texte = re.sub(r' +([:;!?%€])', r'&nbsp;\1', texte)
    # Remplacement des guillemets français
    texte = re.sub(r'« +', r'«&nbsp;', texte)
    texte = re.sub(r' +»', r'&nbsp;»', texte)
    return texte

def auditer_et_ameliorer():
    if not MANUSCRIT_PATH.exists():
        print(f"❌ {MANUSCRIT_PATH} introuvable.")
        return

    contenu = MANUSCRIT_PATH.read_text(encoding="utf-8")
    mots = re.findall(r'\b\w+\b', contenu.lower())
    total_mots = len(mots)
    pages_estimees = total_mots // 250

    print("=" * 60)
    print("🔬 AUDIT QUALITATIF DU MANUSCRIT (PYTHON)")
    print("=" * 60)
    print(f"📊 Volume de texte global : {total_mots:,} mots")
    print(f"📄 Pages estimées (6x9 po standard) : ~{pages_estimees} pages")

    # Alerte de seuil commercial
    if total_mots < 35000:
        print("⚠️ ALERTE : Le livre fait moins de 35 000 mots. Risque de faire moins de 150 pages réelles.")
    else:
        print("✅ OBJECTIF ATTEINT : Densité conforme au standard 150+ pages.")

    # Détection des tics d'écriture
    print("\n🔍 Analyse des tics de langage détectés :")
    texte_lower = contenu.lower()
    for tic in TICS_IA:
        occ = texte_lower.count(tic)
        if occ > 5:
            print(f"  ⚠️ Expression '{tic}' détectée {occ} fois (recommandation : varier le vocabulaire).")

    # Application de la micro-typographie
    contenu_propre = appliquer_micro_typographie(contenu)
    MANUSCRIT_OPTI_PATH.write_text(contenu_propre, encoding="utf-8")
    print(f"\n✨ Manuscrit peaufiné avec micro-typographie enregistré : {MANUSCRIT_OPTI_PATH.name}")

if __name__ == "__main__":
    auditer_et_ameliorer()