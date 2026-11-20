import json
import time
from pathlib import Path
from call_ai import generer_texte_gemini

BLUEPRINT_PATH = Path("book_blueprint.json")
OUTPUT_DIR = Path("livre_sections")
LIVRE_FINAL_PATH = Path("manuscrit_complet.md")
AGENT_PLUME_PATH = Path(".agents/02_plume_editoriale.md")


def charger_consignes_agent_plume() -> str:
    """Charge dynamiquement les directives et règles de l'Agent 02 (La Plume Éditoriale)."""
    if AGENT_PLUME_PATH.exists():
        consignes = AGENT_PLUME_PATH.read_text(encoding="utf-8")
        return (
            "Tu incarnes l'Agent IA suivant. Respecte rigoureusement l'ensemble de ses directives, "
            "son style, sa densité et ses règles anti-remplissage :\n\n"
            f"{consignes}"
        )
    return (
        "Tu es un auteur d'élite de non-fiction pour Amazon KDP. "
        "Rédige un contenu dense, sans remplissage, avec des cas concrets et des actions immédiates."
    )


def charger_blueprint() -> dict:
    if not BLUEPRINT_PATH.exists():
        raise FileNotFoundError(
            f"❌ Le fichier {BLUEPRINT_PATH} est introuvable. "
            "Exécutez d'abord 'python kdp_architect.py'."
        )
    with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def rediger_section(
    system_prompt: str,
    titre_livre: str,
    chapitre_num: int,
    chapitre_titre: str,
    section_index: int,
    section_titre: str,
    points_cles: list,
    contexte_precedent: str = "",
) -> str:
    prompt = f"""
    LIVRE : "{titre_livre}"
    CHAPITRE {chapitre_num} : "{chapitre_titre}"
    SECTION {chapitre_num}.{section_index} : "{section_titre}"
    
    POINTS CLÉS À TRAITER IMPÉRATIVEMENT :
    {json.dumps(points_cles, ensure_ascii=False, indent=2)}
    
    CONTEXTE RÉCENT DU LIVRE (ce qui a été dit juste avant pour éviter les redondances) :
    "{contexte_precedent[-600:] if contexte_precedent else 'Début du livre.'}"
    
    Rédige l'intégralité de la section {chapitre_num}.{section_index} en respectant strictement tes règles éditoriales (densité, cas réels, aucun préambule métatexte, encadré Action Immédiate final).
    """

    return generer_texte_gemini(system_prompt=system_prompt, prompt=prompt, temperature=0.5)


def assembler_livre():
    blueprint = charger_blueprint()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Chargement dynamique des consignes de l'Agent Plume Éditoriale
    system_prompt_plume = charger_consignes_agent_plume()

    titre_livre = blueprint.get("titre", "Livre sans titre")
    sous_titre = blueprint.get("sous_titre", "")
    chapitres = blueprint.get("chapitres", [])

    print("\n=======================================================")
    print(f"📚 USINE DE RÉDACTION KDP : {titre_livre}")
    print(f"🎯 SOUS-TITRE : {sous_titre}")
    print(f"🤖 AGENT ACTIF : Agent 02 - La Plume Éditoriale (.agents/02_plume_editoriale.md)")
    print(f"📑 Total de chapitres à traiter : {len(chapitres)}")
    print("=======================================================\n")

    contexte_dynamique = ""
    total_sections_generees = 0

    for chap in chapitres:
        c_num = chap.get("numero", 1)
        c_titre = chap.get("titre", f"Chapitre {c_num}")
        sections = chap.get("sections", [])

        print(f"\n--- [CHAPITRE {c_num}/{len(chapitres)}] : {c_titre} ---")

        for s_idx, sec in enumerate(sections, start=1):
            s_titre = sec.get("titre", f"Section {s_idx}")
            points = sec.get("points_cles", [])
            if not points:
                points = [
                    f"Concept fondamental de {s_titre}",
                    "Étude de cas concrète et chiffrée",
                    "Piège classique à éviter absolument",
                    "Protocole d'action immédiate sous 24h"
                ]

            nom_fichier = OUTPUT_DIR / f"chapitre_{c_num:02d}_section_{s_idx:02d}.md"

            # Reprise sur incident : si le fichier existe déjà, lecture pour alimenter le contexte
            if nom_fichier.exists():
                print(f"  ⏩ Déjà existant : Chapitre {c_num}.{s_idx} - {s_titre}")
                contexte_dynamique = nom_fichier.read_text(encoding="utf-8")
                continue

            print(f"  ✍️ Rédaction de la section {c_num}.{s_idx} : {s_titre}...")

            try:
                contenu = rediger_section(
                    system_prompt=system_prompt_plume,
                    titre_livre=titre_livre,
                    chapitre_num=c_num,
                    chapitre_titre=c_titre,
                    section_index=s_idx,
                    section_titre=s_titre,
                    points_cles=points,
                    contexte_precedent=contexte_dynamique,
                )

                section_markdown = f"\n### {c_num}.{s_idx} {s_titre}\n\n{contenu.strip()}\n"
                nom_fichier.write_text(section_markdown, encoding="utf-8")

                contexte_dynamique = contenu
                total_sections_generees += 1

                # Temporisation pour respecter les quotas de l'API
                time.sleep(2)

            except Exception as e:
                print(f"\n❌ Erreur sur la section {c_num}.{s_idx} : {e}")
                print("Le script s'arrête ici. Relancez-le pour reprendre exactement à cette section.")
                return

    # Compilation globale une fois les sections rédigées
    compiler_manuscrit_global(blueprint)


def compiler_manuscrit_global(blueprint: dict):
    print("\n📦 Compilation de toutes les sections avec pages liminaires, mentions légales et biographie de MarkEddy...")
    try:
        from kdp_toc_and_frontmatter import assembler_livre_complet_kdp
        assembler_livre_complet_kdp()
        return
    except Exception as e:
        print(f"⚠️ Repli sur compilation standard : {e}")
    
    lignes = [
        f"# {blueprint.get('titre')}\n",
        f"*{blueprint.get('sous_titre')}*\n\n",
        "---\n",
    ]

    for chap in blueprint.get("chapitres", []):
        c_num = chap.get("numero", 1)
        c_titre = chap.get("titre", "")
        lignes.append(f"\n\n# Chapitre {c_num} : {c_titre}\n\n")

        for s_idx in range(1, len(chap.get("sections", [])) + 1):
            f_sec = OUTPUT_DIR / f"chapitre_{c_num:02d}_section_{s_idx:02d}.md"
            if f_sec.exists():
                lignes.append(f_sec.read_text(encoding="utf-8"))

    LIVRE_FINAL_PATH.write_text("\n".join(lignes), encoding="utf-8")
    
    texte_total = LIVRE_FINAL_PATH.read_text(encoding="utf-8")
    mots = len(texte_total.split())
    pages_estimees = mots // 250

    print(f"✅ MANUSCRIT COMPLET GÉNÉRÉ : {LIVRE_FINAL_PATH.resolve()}")
    print(f"📊 Volume total : {mots:,} mots")
    print(f"📄 Volume estimé en livre broché KDP : ~{pages_estimees} pages")


if __name__ == "__main__":
    assembler_livre()