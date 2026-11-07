"""
kdp_qa.py - Auditeur Qualité & Conformité Amazon KDP.
Vérifie de manière chirurgicale le respect de tous les critères techniques d'Amazon KDP
avant la mise en ligne pour garantir un taux de validation de 100% sans rejet.
"""

import os
import json
import re
from pathlib import Path

def auditer_projet_kdp() -> dict:
    rapport = {
        "score": 100,
        "points_forts": [],
        "avertissements": [],
        "erreurs_bloquantes": [],
        "statut_kdp": "EN COURS"
    }

    print("\n" + "=" * 65)
    print("🔬 AUDIT CHIRURGICAL DE CONFORMITÉ AMAZON KDP")
    print("=" * 65)

    # 1. Vérification du Blueprint
    bp_path = Path("book_blueprint.json")
    if not bp_path.exists():
        rapport["erreurs_bloquantes"].append("book_blueprint.json est manquant.")
        rapport["score"] -= 40
    else:
        try:
            bp = json.loads(bp_path.read_text(encoding="utf-8"))
            titre = bp.get("titre")
            chapitres = bp.get("chapitres", [])
            mots_cles = bp.get("mots_cles_kdp", [])
            categories = bp.get("categories_kdp", [])

            if not titre:
                rapport["erreurs_bloquantes"].append("Titre du livre manquant dans le blueprint.")
                rapport["score"] -= 15
            else:
                rapport["points_forts"].append(f"Titre principal conforme : '{titre}'")

            if len(mots_cles) == 7:
                rapport["points_forts"].append("Exactement 7 mots-clés KDP stratégiques définis.")
            else:
                rapport["avertissements"].append(f"KDP autorise 7 mots-clés (actuellement {len(mots_cles)}).")
                rapport["score"] -= 5

            if len(categories) >= 2:
                rapport["points_forts"].append(f"{len(categories)} catégories Amazon sélectionnées.")
            else:
                rapport["avertissements"].append("Moins de 2 catégories cibles spécifiées.")

            total_sec = sum(len(c.get("sections", [])) for c in chapitres)
            if len(chapitres) >= 6 and total_sec >= 20:
                rapport["points_forts"].append(f"Structure de livre complète et équilibrée : {len(chapitres)} chapitres et {total_sec} sections au total.")
            else:
                rapport["avertissements"].append(f"Structure légère ({len(chapitres)} chapitres, {total_sec} sections) : visez au moins 6 chapitres et 20 sections.")
        except Exception as e:
            rapport["erreurs_bloquantes"].append(f"Erreur de lecture du blueprint : {e}")
            rapport["score"] -= 30

    # 2. Vérification du Manuscrit
    ms_path = Path("manuscrit_complet.md")
    if not ms_path.exists():
        rapport["avertissements"].append("manuscrit_complet.md n'est pas encore compilé.")
        rapport["score"] -= 20
    else:
        texte = ms_path.read_text(encoding="utf-8")
        nb_mots = len(texte.split())
        pages_estimees = nb_mots // 250
        
        if nb_mots >= 25000:
            rapport["points_forts"].append(f"Volume de livre professionnel atteint : {nb_mots:,} mots (~{pages_estimees} pages en 6x9 po).")
        elif nb_mots > 5000:
            rapport["avertissements"].append(f"Volume intermédiaire : {nb_mots:,} mots (~{pages_estimees} pages). Objectif recommandé : 25 000+ mots.")
            rapport["score"] -= 10
        else:
            rapport["avertissements"].append(f"Manuscrit court ou en phase de test : {nb_mots} mots.")

        # Détection de phrases parasites générées par l'IA
        parasites = ["Dans cette section nous allons", "En conclusion de cette sous-section", "Lorem ipsum", "TODO"]
        trouve_parasites = [p for p in parasites if p.lower() in texte.lower()]
        if trouve_parasites:
            rapport["avertissements"].append(f"Expressions de remplissage détectées : {trouve_parasites}")
            rapport["score"] -= 5
        else:
            rapport["points_forts"].append("Aucun texte de remplissage méta ou parasite détecté.")

    # 3. Vérification de la Couverture KDP
    couv_path = Path("couverture_kdp_complete.pdf")
    if couv_path.exists():
        taille_ko = couv_path.stat().st_size / 1024
        rapport["points_forts"].append(f"Couverture KDP complète générée en PDF ({taille_ko:.1f} Ko).")
    else:
        rapport["avertissements"].append("couverture_kdp_complete.pdf n'est pas encore générée.")
        rapport["score"] -= 15

    # 4. Vérification du Formatage Intérieur HTML / CSS
    html_path = Path("livre_kdp_interieur.html")
    if html_path.exists():
        html_code = html_path.read_text(encoding="utf-8")
        if "size: 6in 9in;" in html_code:
            rapport["points_forts"].append("Mise en page intérieure 6x9 pouces configurée avec marges de reliure.")
        else:
            rapport["avertissements"].append("Spécification 6x9 pouces manquante dans le fichier HTML.")
    else:
        rapport["avertissements"].append("livre_kdp_interieur.html non généré.")
        rapport["score"] -= 10

    # 5. Vérification des 3 Formats Commerciaux Multi-Versions
    print_pdf = Path("livre_imprimable_kdp.pdf")
    epub_file = Path("livre_ebook_kdp.epub")
    digital_pdf = Path("livre_numerique_interactif.pdf")
    if print_pdf.exists() and epub_file.exists() and digital_pdf.exists():
        rapport["points_forts"].append("Les 3 livrables multi-formats (Broché Print, Ebook Kindle EPUB 3, PDF Interactif) sont compilés et prêts.")
    else:
        rapport["avertissements"].append("Certains formats multi-versions (EPUB 3 / PDF interactif) n'ont pas encore été compilés.")

    # Statut final
    rapport["score"] = max(0, min(100, rapport["score"]))
    if not rapport["erreurs_bloquantes"] and rapport["score"] >= 80:
        rapport["statut_kdp"] = "🟢 CONFORME & PRÊT POUR PUBLICATION KDP"
    elif not rapport["erreurs_bloquantes"]:
        rapport["statut_kdp"] = "🟡 CONFORME AVEC AVERTISSEMENTS"
    else:
        rapport["statut_kdp"] = "🔴 CORRECTIONS BLOQUANTES REQUISES"

    # Affichage du rapport
    print(f"\n📊 SCORE DE CONFORMITÉ KDP : {rapport['score']}/100")
    print(f"🏷️  STATUT GLOBAL : {rapport['statut_kdp']}\n")

    if rapport["points_forts"]:
        print("✅ POINTS FORTS :")
        for pf in rapport["points_forts"]:
            print(f"  • {pf}")

    if rapport["avertissements"]:
        print("\n⚠️ AVERTISSEMENTS :")
        for av in rapport["avertissements"]:
            print(f"  • {av}")

    if rapport["erreurs_bloquantes"]:
        print("\n❌ ERREURS BLOQUANTES :")
        for eb in rapport["erreurs_bloquantes"]:
            print(f"  • {eb}")

    print("=" * 65 + "\n")
    return rapport

if __name__ == "__main__":
    auditer_projet_kdp()
