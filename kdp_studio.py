"""
kdp_studio.py - Studio Interactif & Tableau de Bord de la Machine KDP.
Console de commande pour piloter l'armée d'agents, tester les palettes de luxe
et orchestrer la création de livres professionnels sans ligne de commande complexe.
"""

import os
import sys
import subprocess
from pathlib import Path

def afficher_banniere():
    print("""
╔═════════════════════════════════════════════════════════════════════════╗
║   🏛️  STUDIO DE CRÉATION DE LIVRES AMAZON KDP HAUTE COUTURE          ║
║   Machine Multi-Agents Professionnelle • Résolution 300 DPI • 6x9 po    ║
╚═════════════════════════════════════════════════════════════════════════╝
    """)

def menu_principal():
    while True:
        afficher_banniere()
        print("Sélectionnez l'action souhaitée :")
        print("  [1] 🚀 Pipeline Complet : Créer un livre de A à Z (Orchestrateur)")
        print("  [2] 🧠 Agent 01 : Concevoir le Blueprint (10 chapitres × 5 sections)")
        print("  [3] ✍️  Agent 02 : Rédiger le manuscrit complet (50 sections)")
        print("  [4] 🎨 Agent 03 : Générer la couverture 300 DPI (Sélection de Palette)")
        print("  [5] 📐 Agent 04 : Formater l'intérieur 6x9 po (Lettrines & Gouttière)")
        print("  [6] 🛒 Agent 05 : Générer le pack Marketing Amazon (HTML & A+ Content)")
        print("  [7] 🔬 Agent 06 : Lancer l'Audit Qualité & Conformité KDP (Score /100)")
        print("  [8] 🧪 Banc d'essai : Exécuter la suite de 14 tests automatisés")
        print("  [9] 🌐 Démarrer le Hub API FastAPI (Intégration n8n / Hermes)")
        print("  [0] ❌ Quitter le studio\n")

        choix = input("👉 Votre choix (0-9) : ").strip()

        if choix == "1":
            niche = input("\nEntrez la niche du livre (ex: Investissement immobilier) : ").strip()
            if not niche: niche = "Maîtriser ses finances personnelles et investir simplement"
            cible = input("Entrez le public cible (ex: Débutants) : ").strip()
            if not cible: cible = "Débutants sans compétences préalables"
            
            print("\nChoisissez la palette de luxe :")
            print("  1. Obsidienne & Or Impérial (Finance, Leadership, Stratégie)")
            print("  2. Émeraude Royale & Champagne (Immobilier, Patrimoine)")
            print("  3. Saphir Majestueux & Platine (Tech, IA, Méthodes)")
            print("  4. Bordeaux Grand Cru & Or Rose (Psychologie, Développement)")
            p_choix = input("Choix (1-4, défaut 1) : ").strip()
            palettes = {"1": "obsidian_gold", "2": "emerald_champagne", "3": "royal_sapphire", "4": "grand_cru_rose"}
            palette_sel = palettes.get(p_choix, "obsidian_gold")

            cmd = [sys.executable, "orchestrator.py", "--niche", niche, "--cible", cible, "--palette", palette_sel]
            subprocess.run(cmd)

        elif choix == "2":
            niche = input("\nNiche du livre : ").strip() or "Maîtriser ses finances personnelles et investir simplement"
            cible = input("Public cible : ").strip() or "Débutants sans compétences financières préalables"
            cmd = [sys.executable, "orchestrator.py", "--step", "architect", "--niche", niche, "--cible", cible]
            subprocess.run(cmd)

        elif choix == "3":
            print("\nLancement de la rédaction séquentielle...")
            cmd = [sys.executable, "orchestrator.py", "--step", "writer"]
            subprocess.run(cmd)

        elif choix == "4":
            print("\nSélectionnez une harmonie chromatique haute couture :")
            print("  [1] Obsidienne & Or Impérial (obsidian_gold)")
            print("  [2] Émeraude Royale & Champagne (emerald_champagne)")
            print("  [3] Saphir Majestueux & Platine (royal_sapphire)")
            print("  [4] Bordeaux Grand Cru & Or Rose (grand_cru_rose)")
            c = input("Choix (1-4) : ").strip()
            pals = {"1": "obsidian_gold", "2": "emerald_champagne", "3": "royal_sapphire", "4": "grand_cru_rose"}
            pal = pals.get(c, "obsidian_gold")
            subprocess.run([sys.executable, "cover_generator.py", "--palette", pal])

        elif choix == "5":
            print("\nFormatage intérieur d'édition 6x9 pouces...")
            subprocess.run([sys.executable, "kdp_formatter.py"])

        elif choix == "6":
            print("\nGénération de la fiche produit Amazon KDP...")
            subprocess.run([sys.executable, "kdp_marketing.py"])

        elif choix == "7":
            print("\nExécution de l'audit chirurgical...")
            subprocess.run([sys.executable, "kdp_qa.py"])

        elif choix == "8":
            print("\nExécution des 14 tests automatisés...")
            subprocess.run([sys.executable, "test_suite.py"])

        elif choix == "9":
            print("\nDémarrage du serveur FastAPI local...")
            print("Ouvrez http://127.0.0.1:8000/docs dans votre navigateur (Ctrl + C pour arrêter).")
            subprocess.run(["uvicorn", "server:app", "--reload", "--port", "8000"])

        elif choix == "0":
            print("\nAu revoir et bonnes publications sur Amazon KDP !\n")
            break
        else:
            print("\n⚠️ Option invalide. Veuillez réessayer.")

        input("\nAppuyez sur Entrée pour revenir au menu principal...")

if __name__ == "__main__":
    menu_principal()
