"""
kdp_writer.py - Moteur de rédaction séquentielle et approfondie de livre KDP.
Rédige chaque chapitre et sous-section avec une haute densité d'information,
des exemples concrets, des cas pratiques et un ton professionnel d'expert.
Prend en charge la reprise sur incident (checkpoints automatiques).
"""

import os
import json
import time
import argparse
from pathlib import Path
from call_ai import generer_texte_gemini

def rediger_section(
    titre_livre: str,
    promesse: str,
    cible: str,
    numero_chapitre: int,
    titre_chapitre: str,
    objectif_chapitre: str,
    titre_section: str,
    points_cles: list,
    model: str = "gemini-1.5-flash"
) -> str:
    """
    Rédige une sous-section dense et détaillée (600 à 1000 mots).
    """
    system_prompt = (
        "Tu es un auteur best-seller international de livres pratiques et de non-fiction. "
        "Ton style est fluide, captivant, pédagogue, structuré et hautement actionnable. "
        "Tu évites le remplissage creux. Tu apportes des explications concrètes, des méthodes étape par étape, "
        "des études de cas réalistes, des encadrés d'avertissement et des conseils d'application immédiate. "
        "Formate en Markdown soigné : sous-titres ###, listes à puces, texte en gras pour les concepts clés, "
        "et encadrés '> [!TIP]' ou '> [!IMPORTANT]' pour les passages essentiels."
    )

    prompt = f"""
    LIVRE : "{titre_livre}"
    PROMESSE DU LIVRE : {promesse}
    PUBLIC CIBLE : {cible}
    
    CHAPITRE {numero_chapitre} : "{titre_chapitre}"
    OBJECTIF DU CHAPITRE : {objectif_chapitre}
    
    SECTION À RÉDIGER : "{titre_section}"
    POINTS CLÉS À COUVRIR DANS CETTE SECTION :
    {json.dumps(points_cles, ensure_ascii=False, indent=2)}
    
    CONSIGNES DE RÉDACTION :
    1. Ne répète pas le titre du chapitre ou de la section au tout début.
    2. Développe chaque point clé avec profondeur (théorie claire, exemple concret illustré, piège à éviter).
    3. Inclus une étude de cas ou un exemple chiffré/scénario réaliste.
    4. Conclus la section par une sous-partie "Plan d'action immédiat" avec 2 ou 3 étapes concrètes que le lecteur peut appliquer dès aujourd'hui.
    5. Vise une rédaction dense et complète d'environ 600 à 900 mots pour cette sous-section.
    """

    texte = generer_texte_gemini(prompt=prompt, system_prompt=system_prompt, temperature=0.6, model=model)
    return texte.strip()

def rediger_introduction(blueprint: dict, model: str = "gemini-1.5-flash") -> str:
    """Rédige l'introduction et l'avant-propos du livre."""
    system_prompt = (
        "Tu es un auteur best-seller. Rédige une introduction captivante qui accroche le lecteur, "
        "met en lumière son problème profond, lui montre pourquoi ce livre est différent, "
        "et lui donne une feuille de route claire pour réussir sa transformation."
    )
    prompt = f"""
    Rédige l'Introduction complète du livre :
    - Titre : "{blueprint.get('titre')}"
    - Sous-titre : "{blueprint.get('sous_titre')}"
    - Promesse : "{blueprint.get('promesse_client')}"
    - Public cible : "{blueprint.get('public_cible', 'Lecteurs ambitieux')}"
    
    Structure de l'introduction :
    1. L'Accroche : La réalité difficile vécue par le lecteur aujourd'hui
    2. Le déclic : Pourquoi les méthodes traditionnelles échouent
    3. La promesse de ce guide et la méthode pas-à-pas
    4. Comment tirer le meilleur parti de votre lecture
    5. Le pacte de réussite
    
    Longueur attendue : 800 à 1200 mots. Rédige en Markdown sans inclure '# Introduction' en tête.
    """
    print("✍️  Rédaction de l'Introduction du livre...")
    return generer_texte_gemini(prompt=prompt, system_prompt=system_prompt, temperature=0.6, model=model).strip()

def rediger_conclusion(blueprint: dict, model: str = "gemini-1.5-flash") -> str:
    """Rédige la conclusion inspirante et l'appel à l'action pour les avis KDP."""
    system_prompt = (
        "Tu es un auteur best-seller. Rédige une conclusion motivante, un appel à l'action final, "
        "et un mot personnel sincère demandant au lecteur de laisser un avis honnête sur Amazon KDP."
    )
    prompt = f"""
    Rédige la Conclusion et la postface du livre :
    - Titre : "{blueprint.get('titre')}"
    - Promesse réalisée : "{blueprint.get('promesse_client')}"
    
    Structure :
    1. Récapitulatif du chemin parcouru
    2. Le passage à l'action : Rien ne change sans exécution continue
    3. Mot personnel de l'auteur
    4. Demande d'avis Amazon KDP : Explique avec élégance et sincérité à quel point laisser une évaluation 5 étoiles sur Amazon aide les auteurs indépendants et permet à d'autres lecteurs de découvrir ce guide.
    
    Longueur attendue : 600 à 900 mots.
    """
    print("✍️  Rédaction de la Conclusion et de l'appel à avis...")
    return generer_texte_gemini(prompt=prompt, system_prompt=system_prompt, temperature=0.6, model=model).strip()

def orchestrer_redaction_livre(
    blueprint_path: str = "book_blueprint.json",
    draft_output_path: str = "book_draft.json",
    limite_chapitres: int = None,
    delai_entre_requetes: float = 1.0
) -> dict:
    """
    Parcourt le blueprint, rédige chaque partie et sauvegarde à chaque étape.
    Gère la reprise automatique si une rédaction a déjà commencé.
    """
    chemin_bp = Path(blueprint_path)
    if not chemin_bp.exists():
        raise FileNotFoundError(f"Le fichier blueprint {blueprint_path} est introuvable. Lancez d'abord kdp_architect.py.")

    blueprint = json.loads(chemin_bp.read_text(encoding="utf-8"))
    titre_livre = blueprint.get("titre", "Livre sans titre")
    promesse = blueprint.get("promesse_client", "")
    cible = blueprint.get("public_cible", "Grand public")

    # Chargement d'un brouillon existant pour reprise sur crash
    chemin_draft = Path(draft_output_path)
    if chemin_draft.exists():
        draft = json.loads(chemin_draft.read_text(encoding="utf-8"))
        print(f"🔄 Reprise d'un brouillon existant : {draft_output_path}")
    else:
        draft = {
            "metadata": blueprint,
            "introduction": None,
            "chapitres_rediges": [],
            "conclusion": None
        }

    # 1. Introduction
    if not draft.get("introduction"):
        draft["introduction"] = rediger_introduction(blueprint)
        chemin_draft.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(delai_entre_requetes)

    # 2. Chapitres
    chapitres = blueprint.get("chapitres", [])
    if limite_chapitres:
        chapitres = chapitres[:limite_chapitres]

    for index_ch, chap in enumerate(chapitres):
        num_ch = chap.get("numero", index_ch + 1)
        titre_ch = chap.get("titre", f"Chapitre {num_ch}")
        objectif_ch = chap.get("objectif", "")
        sections = chap.get("sections", [])

        # Vérifier si le chapitre est déjà rédigé
        chap_existant = next((c for c in draft["chapitres_rediges"] if c.get("numero") == num_ch), None)
        if not chap_existant:
            chap_existant = {
                "numero": num_ch,
                "titre": titre_ch,
                "objectif": objectif_ch,
                "sections_redigees": []
            }
            draft["chapitres_rediges"].append(chap_existant)

        print(f"\n📖 [Chapitre {num_ch}/10] : {titre_ch}")

        for index_sec, sec in enumerate(sections):
            titre_sec = sec.get("titre", f"Section {index_sec + 1}")
            points_cles = sec.get("points_cles", [])

            # Vérifier si la section a déjà été écrite
            sec_existante = next((s for s in chap_existant["sections_redigees"] if s.get("titre") == titre_sec), None)
            if sec_existante:
                print(f"  ⏩ Déjà rédigée : {titre_sec}")
                continue

            print(f"  ✍️ Rédaction de : {titre_sec}...")
            contenu_sec = rediger_section(
                titre_livre=titre_livre,
                promesse=promesse,
                cible=cible,
                numero_chapitre=num_ch,
                titre_chapitre=titre_ch,
                objectif_chapitre=objectif_ch,
                titre_section=titre_sec,
                points_cles=points_cles
            )

            chap_existant["sections_redigees"].append({
                "titre": titre_sec,
                "contenu": contenu_sec
            })

            # Sauvegarde incrémentale à chaque section
            chemin_draft.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")
            time.sleep(delai_entre_requetes)

    # 3. Conclusion
    if not draft.get("conclusion"):
        draft["conclusion"] = rediger_conclusion(blueprint)
        chemin_draft.write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")

    # Calcul du nombre de mots total
    total_mots = len(draft["introduction"].split())
    if draft.get("conclusion"):
        total_mots += len(draft["conclusion"].split())
    for c in draft.get("chapitres_rediges", []):
        for s in c.get("sections_redigees", []):
            total_mots += len(s.get("contenu", "").split())

    pages_estimees = int(total_mots / 250)
    print("\n" + "=" * 60)
    print(f"🎉 RÉDACTION DU LIVRE ACHEVÉE AVEC SUCCÈS !")
    print(f"📊 Total de mots rédigés : ~{total_mots:,} mots")
    print(f"📑 Pages estimées en format 6x9 po : ~{pages_estimees} pages")
    print(f"💾 Sauvegarde : {chemin_draft.resolve()}")
    print("=" * 60)

    return draft

def main():
    parser = argparse.ArgumentParser(description="Moteur de rédaction de livres Amazon KDP.")
    parser.add_argument("--blueprint", default="book_blueprint.json", help="Chemin vers le blueprint JSON")
    parser.add_argument("--draft", default="book_draft.json", help="Fichier de sortie du brouillon rédigé")
    parser.add_argument("--max-chapitres", type=int, default=None, help="Nombre maximal de chapitres à rédiger (pour test rapide)")
    args = parser.parse_args()

    orchestrer_redaction_livre(
        blueprint_path=args.blueprint,
        draft_output_path=args.draft,
        limite_chapitres=args.max_chapitres
    )

if __name__ == "__main__":
    main()
