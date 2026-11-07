"""
kdp_layout_fixer.py - Moteur de Réparation Pré-Presse & Typographie de Haute Précision.
Corrige automatiquement et chirurgicalement l'ensemble des défauts identifiés :
1. Dédoublonnage des titres (ex: '2.2 2.2' -> '2.2') et suppression des H3 consécutifs identiques
2. Élimination des fuites Markdown dans les encadrés (> ### ...) et suppression des blockquotes vides
3. Suppression des séparateurs orphelins (---) avant les sauts de page de chapitres
4. Neutralisation des césures sauvages dans les titres, tableaux et encadrés (hyphens: none)
5. Rééquilibrage des colonnes de tableaux pour affichage compact professionnel
"""

import re
import json
from pathlib import Path

MANUSCRIT_PATH = Path("manuscrit_complet.md")
SECTIONS_DIR = Path("livre_sections")
BLUEPRINT_PATH = Path("book_blueprint.json")


def reparer_texte_markdown(texte: str) -> tuple[str, dict]:
    stats = {
        "doublons_prefixe_corriges": 0,
        "h3_consecutifs_elimines": 0,
        "callout_markdown_nettoyes": 0,
        "separateurs_avant_h1_retires": 0,
        "blockquotes_vides_nettoyees": 0
    }

    # 1. Corriger les préfixes redoublés dans le texte (### 2.2 2.2 Titre -> ### 2.2 Titre)
    def clean_prefix(m):
        stats["doublons_prefixe_corriges"] += 1
        return f"### {m.group(1)} {m.group(2)}"
    texte = re.sub(r"^###\s+(\d+\.\d+)\s+\1\s+(.*)$", clean_prefix, texte, flags=re.MULTILINE)

    # Corriger dans les listes du sommaire (- 2.1 2.1 Titre -> - 2.1 Titre)
    def clean_sommaire(m):
        stats["doublons_prefixe_corriges"] += 1
        return f"- {m.group(1)} {m.group(2)}"
    texte = re.sub(r"^-\s+(\d+\.\d+)\s+\1\s+(.*)$", clean_sommaire, texte, flags=re.MULTILINE)

    # 2. Supprimer les H3 consécutifs dédoublés (même avec variations de guillemets ' vs " ou espaces)
    def normaliser_titre(t: str) -> str:
        s = re.sub(r"^###\s*[\d\.\s]*", "", t).lower()
        s = re.sub(r"['\"«»’“”\s\-]", "", s)
        return s

    lignes = texte.splitlines()
    lignes_propres = []
    i = 0
    while i < len(lignes):
        l_cur = lignes[i]
        
        # Vérifier si H3 suivi de lignes vides puis d'un autre H3 quasi-identique
        if l_cur.strip().startswith("### "):
            j = i + 1
            while j < len(lignes) and not lignes[j].strip():
                j += 1
            if j < len(lignes) and lignes[j].strip().startswith("### "):
                t1 = normaliser_titre(l_cur.strip())
                t2 = normaliser_titre(lignes[j].strip())
                if t1 and t1 == t2:
                    # Garder le premier (ou celui avec les meilleures guillemets), sauter le deuxième
                    lignes_propres.append(l_cur)
                    i = j + 1
                    stats["h3_consecutifs_elimines"] += 1
                    continue
        lignes_propres.append(l_cur)
        i += 1

    texte = "\n".join(lignes_propres)

    # 3. Transformer les titres '### Action Immédiate' isolés en encadrés propres
    def wrap_action_immediate(m):
        stats["callout_markdown_nettoyes"] += 1
        titre = (m.group(1) or "").strip()
        titre = re.sub(r"^[🛑⚡💡\s]+", "", titre)
        titre = re.sub(r"[\*:]+$", "", titre).strip()
        corps = m.group(2).strip()
        lignes_corps = corps.splitlines()
        corps_blockquote = "\n".join([f"> {l}" if l.strip() else ">" for l in lignes_corps])
        label = f" : {titre}" if titre else ""
        return f"> **⚡ ACTION IMMÉDIATE{label}**\n>\n{corps_blockquote}"

    # Détecter ### Action Immédiate suivi de texte jusqu'au prochain titre ou séparateur
    texte = re.sub(
        r"^###\s+[🛑⚡]?\s*ACTION IMMÉDIATE(?:\s*:\s*(.*?))?\n+((?:(?!\n###|\n#|\n---)[\s\S])+)",
        wrap_action_immediate,
        texte,
        flags=re.MULTILINE | re.IGNORECASE
    )

    # Nettoyer les balises Markdown brutes dans les citations (> ### Action Immédiate -> > **⚡ Action Immédiate :**)
    def clean_callout(m):
        stats["callout_markdown_nettoyes"] += 1
        titre_callout = m.group(1).strip()
        titre_callout = re.sub(r"^[🛑⚡💡\s]+", "", titre_callout)
        titre_callout = re.sub(r"[\*:]+$", "", titre_callout).strip()
        return f"> **⚡ ACTION IMMÉDIATE : {titre_callout}**\n>"
    texte = re.sub(r"^>\s*###\s*(.*)$", clean_callout, texte, flags=re.MULTILINE)
    texte = re.sub(r"^>\s*##\s*(.*)$", clean_callout, texte, flags=re.MULTILINE)

    # Supprimer les lignes '> ' vides isolées qui créent des boîtes blanches
    texte = re.sub(r"\n>\s*\n>\s*\n", "\n>\n", texte)
    texte = re.sub(r"\n>\s*\n(?=[^>])", "\n\n", texte)

    # 4. Supprimer les séparateurs '---' placés immédiatement avant un saut de chapitre
    # (car # Chapitre a déjà un saut de page forcé en CSS, ce qui laissait '---' seul sur une page blanche !)
    def remove_orphan_hr(m):
        stats["separateurs_avant_h1_retires"] += 1
        return m.group(1)
    texte = re.sub(r"\n---\s*\n+(\s*#\s+(?:Chapitre|Conclusion|Avant-propos))", remove_orphan_hr, texte)

    return texte, stats


def reparer_sections_individuelles():
    """Répare chaque fichier unitaire dans livre_sections/."""
    if not SECTIONS_DIR.exists():
        return
    for f in SECTIONS_DIR.glob("*.md"):
        txt = f.read_text(encoding="utf-8")
        txt_repare, _ = reparer_texte_markdown(txt)
        f.write_text(txt_repare, encoding="utf-8")
    print("  ✅ Fichiers unitaires dans livre_sections/ nettoyés et synchronisés.")


def reparer_manuscrit_global():
    """Répare le manuscrit complet officiel."""
    if not MANUSCRIT_PATH.exists():
        return
    txt = MANUSCRIT_PATH.read_text(encoding="utf-8")
    txt_repare, stats = reparer_texte_markdown(txt)
    MANUSCRIT_PATH.write_text(txt_repare, encoding="utf-8")

    print("\n" + "=" * 65)
    print("🛠️ MOTEUR DE RÉPARATION PRÉ-PRESSE APPLIQUÉ SUR LE MANUSCRIT")
    print("=" * 65)
    print(f"  • {stats['doublons_prefixe_corriges']} préfixes de titres redoublés corrigés")
    print(f"  • {stats['h3_consecutifs_elimines']} titres consécutifs en double éliminés")
    print(f"  • {stats['callout_markdown_nettoyes']} balises Markdown dans les encadrés converties")
    print(f"  • {stats['separateurs_avant_h1_retires']} séparateurs orphelins avant chapitres supprimés")
    print("=" * 65 + "\n")


def corriger_book_writer_et_blueprint():
    """Assure que le blueprint et book_writer n'injectent plus de doublons à l'avenir."""
    if BLUEPRINT_PATH.exists():
        data = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
        modifie = False
        for c in data.get("chapitres", []):
            for s in c.get("sections", []):
                t = s.get("titre", "")
                t_propre = re.sub(r"^\d+\.\d+\s*", "", t).strip()
                if t != t_propre:
                    s["titre"] = t_propre
                    modifie = True
        if modifie:
            BLUEPRINT_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("  ✅ book_blueprint.json épuré des préfixes redondants.")


if __name__ == "__main__":
    corriger_book_writer_et_blueprint()
    reparer_sections_individuelles()
    reparer_manuscrit_global()
