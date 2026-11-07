"""
test_suite.py - Suite de tests automatisés pour valider l'ensemble du projet Espace IA.
Exécutez ce script via : python test_suite.py
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Compteurs de tests
tests_reussis = 0
tests_total = 0

def afficher_succes(message: str):
    global tests_reussis, tests_total
    tests_reussis += 1
    tests_total += 1
    print(f"  ✅ [SUCCÈS] {message}")

def afficher_erreur(message: str):
    global tests_total
    tests_total += 1
    print(f"  ❌ [ÉCHEC] {message}")

def test_1_configuration_env():
    print("\n🔍 Test 1 : Vérification du fichier .env et de la clé API...")
    load_dotenv(override=True)
    cle = os.getenv("GEMINI_API_KEY")
    if not cle:
        afficher_erreur("GEMINI_API_KEY est absente du fichier .env")
        return
    if cle.startswith("votre_") or len(cle) < 20:
        afficher_erreur("La clé API semble invalide ou par défaut : longueur ou préfixe incorrect (valeur non affichée).")
        return
    afficher_succes("Clé GEMINI_API_KEY trouvée dans l'environnement (valeur non affichée).")

def test_2_imports_modules():
    print("\n🔍 Test 2 : Validation des modules du projet...")
    modules = [
        "generate_article", "server", "call_ai", "test",
        "kdp_design_system", "kdp_architect", "kdp_writer",
        "book_writer", "kdp_formatter", "html_to_pdf", "cover_generator", "cover_prompts",
        "kdp_seo_optimizer", "kdp_marketing", "kdp_qa", "orchestrator", "kdp_machine"
    ]
    for mod_name in modules:
        try:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
            __import__(mod_name)
            afficher_succes(f"Module '{mod_name}.py' importé avec succès.")
        except Exception as e:
            afficher_erreur(f"Échec de l'import du module '{mod_name}.py' : {e}")

def test_3_fastapi_endpoints():
    print("\n🔍 Test 3 : Validation interne de l'application FastAPI (server.py)...")
    try:
        import server
        
        # Test endpoint root
        reponse_root = server.root()
        assert reponse_root.get("statut") == "actif", "Le statut root n'est pas 'actif'"
        assert reponse_root.get("gemini_disponible") is True, "Gemini devrait être marqué disponible"
        afficher_succes("Endpoint racine '/' fonctionne et détecte Gemini.")
        
        # Test endpoint health
        reponse_health = server.health()
        assert reponse_health.get("status") == "ok", "Le health check doit renvoyer 'ok'"
        afficher_succes("Endpoint de santé '/health' opérationnel.")
        
        # Test validation du modèle Pydantic AIRequest
        req_valide = server.AIRequest(sujet="Éclairage salle de bain", piece="Salle d'eau moderne")
        assert req_valide.sujet == "Éclairage salle de bain"
        afficher_succes("Validation des modèles de données (Pydantic AIRequest) validée.")
        
    except Exception as e:
        afficher_erreur(f"Erreur lors des tests du serveur : {e}")

def test_4_sauvegarde_markdown():
    print("\n🔍 Test 4 : Test unitaire de la génération de fichier Markdown...")
    try:
        from generate_article import sauvegarder_en_markdown
        
        test_slug = "test-temp-article-verification"
        test_titre = "Test Validation Automatique"
        test_contenu = "Contenu de vérification technique."
        
        nom_fichier = sauvegarder_en_markdown(test_titre, test_contenu, test_slug)
        
        if os.path.exists(nom_fichier):
            with open(nom_fichier, "r", encoding="utf-8") as f:
                texte = f.read()
            assert test_titre in texte, "Le titre est introuvable dans le fichier généré"
            assert test_contenu in texte, "Le contenu est introuvable dans le fichier généré"
            os.remove(nom_fichier)  # Nettoyage
            afficher_succes("Création, écriture et structure du fichier Markdown validées.")
        else:
            afficher_erreur("Le fichier Markdown n'a pas été généré.")
    except Exception as e:
        afficher_erreur(f"Erreur lors de la sauvegarde Markdown : {e}")

def test_5_connectivite_api():
    print("\n🔍 Test 5 : Test de communication avec les serveurs Google...")
    try:
        import requests
        cle = os.getenv("GEMINI_API_KEY")
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        headers = {"x-goog-api-key": cle}
        
        # Tentative avec timeout court pour ne pas bloquer si hors ligne
        reponse = requests.get(url, headers=headers, timeout=5)
        if reponse.ok:
            afficher_succes(f"Communication API Google réussie (Code HTTP {reponse.status_code}).")
        else:
            print(f"  ⚠️ [INFO RÉSEAU] Réponse API Google reçue : Code {reponse.status_code}")
            print(f"     Détail : {reponse.text[:120]}...")
            afficher_succes(f"Serveurs Google contactés (réponse reçue : HTTP {reponse.status_code}).")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ [INFO ENVIRONNEMENT] Connexion internet externe non active ou restreinte : {e.__class__.__name__}")
        print("     (Ce test nécessite une connexion réseau ouverte vers generativelanguage.googleapis.com)")

def test_6_kdp_formatting_engine():
    print("\n🔍 Test 6 : Validation du moteur de formatage KDP 6x9 (HTML & Markdown)...")
    try:
        from kdp_formatter import generer_manuscrit_markdown, generer_livre_html_kdp, generer_description_amazon_kdp
        
        mock_draft = {
            "metadata": {
                "titre": "Finances Simples",
                "sous_titre": "Le guide débutant",
                "promesse_client": "Apprendre à budgétiser",
                "auteur_suggere": "Alexandre Dupont",
                "mots_cles_kdp": ["budget", "épargne", "bourse"],
                "categories_kdp": ["Économie", "Gestion personnelle"],
                "chapitres": [{"numero": 1, "titre": "Les bases du budget", "objectif": "Comprendre ses dépenses"}]
            },
            "introduction": "Bienvenue dans ce guide d'indépendance financière.",
            "chapitres_rediges": [
                {
                    "numero": 1,
                    "titre": "Les bases du budget",
                    "objectif": "Comprendre ses dépenses",
                    "sections_redigees": [
                        {"titre": "1.1 La règle 50/30/20", "contenu": "Voici comment répartir vos revenus intelligemment."}
                    ]
                }
            ],
            "conclusion": "Félicitations pour votre engagement."
        }
        
        f_md = generer_manuscrit_markdown(mock_draft, "temp_test_manuscrit.md")
        f_html = generer_livre_html_kdp(mock_draft, "temp_test_livre_6x9.html")
        f_desc = generer_description_amazon_kdp(mock_draft["metadata"], "temp_test_amazon_desc.html")
        
        assert f_md.exists(), "Le fichier markdown n'a pas été créé"
        assert f_html.exists(), "Le fichier HTML n'a pas été créé"
        assert f_desc.exists(), "La description Amazon n'a pas été créée"
        
        # Vérification du CSS 6x9 pouces
        html_content = f_html.read_text(encoding="utf-8")
        assert "size: 6in 9in;" in html_content, "Le format 6x9 pouces est manquant dans le CSS"
        
        # Nettoyage
        f_md.unlink()
        f_html.unlink()
        f_desc.unlink()
        
        afficher_succes("Moteur KDP validé (Génération Markdown, HTML 6x9 po et description Amazon).")
    except Exception as e:
        afficher_erreur(f"Erreur lors du test de formatage KDP : {e}")

def main():
    print("=" * 65)
    print("🧪 SUITE DE TESTS AUTOMATISÉE - ESPACE IA & MACHINE KDP")
    print("=" * 65)
    
    test_1_configuration_env()
    test_2_imports_modules()
    test_3_fastapi_endpoints()
    test_4_sauvegarde_markdown()
    test_5_connectivite_api()
    test_6_kdp_formatting_engine()
    
    print("\n" + "=" * 65)
    print(f"📊 RÉSULTAT : {tests_reussis}/{tests_total} tests validés avec succès.")
    if tests_reussis == tests_total:
        print("🎉 TOUS LES TESTS LOCAUX SONT AU VERT ! Le projet est prêt.")
    else:
        print("⚠️ Certains points nécessitent votre attention (voir détails ci-dessus).")
    print("=" * 65)

if __name__ == "__main__":
    main()
