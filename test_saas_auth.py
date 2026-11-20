"""
test_saas_auth.py - Validation chirurgicale du SaaS Multi-Utilisateurs & Système de Crédits.
Appelle directement les gestionnaires d'API FastAPI et vérifie les contrats de sécurité.
"""
import sys
import time
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from fastapi import BackgroundTasks, HTTPException

import app_studio
import studio_db
import auth

print("=" * 65)
print("🧪 TESTS DU SYSTÈME SAAS MULTI-UTILISATEURS & CRÉDITS KDP")
print("=" * 65)

try:
    # 1. Test Admin Login
    print("\n🔍 1. Test Connexion Compte Administrateur...")
    login_req = app_studio.LoginRequest(email="admin@markeddy.com", password="Admin123!")
    res_admin_login = app_studio.api_login(login_req)
    admin_body = json.loads(res_admin_login.body.decode("utf-8"))
    assert admin_body["status"] == "success"
    admin_token = admin_body["token"]
    assert admin_body["user"]["plan"] == "admin"
    print(f"  ✅ Admin connecté avec succès : {admin_body['user']['email']} (Crédits : {admin_body['user']['credits']})")

    # 2. Test Inscription Nouvel Utilisateur (3 crédits gratuits)
    test_email = f"user_test_{int(time.time())}@example.com"
    print(f"\n🔍 2. Test Inscription Nouvel Utilisateur ({test_email})...")
    reg_req = app_studio.RegisterRequest(email=test_email, password="Password123!")
    res_reg = app_studio.api_register(reg_req)
    reg_body = json.loads(res_reg.body.decode("utf-8"))
    assert res_reg.status_code == 201
    user_token = reg_body["token"]
    user_id = reg_body["user"]["id"]
    assert reg_body["user"]["credits"] == 3, "Le nouvel utilisateur doit avoir exactement 3 crédits !"
    assert reg_body["user"]["plan"] == "gratuit"
    print(f"  ✅ Utilisateur créé (ID #{user_id}) avec 3 crédits gratuits.")

    # 3. Test Validation de la Dépendance get_current_user (Bearer & Query param)
    print("\n🔍 3. Test Dépendance get_current_user...")
    dummy_req = MagicMock()
    # Test avec Header
    current_u1 = app_studio.get_current_user(dummy_req, authorization=f"Bearer {user_token}", token=None)
    assert current_u1["id"] == user_id
    # Test avec Query param ?token=
    current_u2 = app_studio.get_current_user(dummy_req, authorization=None, token=user_token)
    assert current_u2["id"] == user_id
    print("  ✅ Validation JWT par en-tête Bearer et paramètre ?token= confirmée.")

    # 4. Test Visibilité du Livre Pilote & Isolation des Livres Privés
    print("\n🔍 4. Test Visibilité du Livre Pilote & Isolation...")
    res_books = app_studio.api_lister_livres(current_user=current_u1)
    books_body = json.loads(res_books.body.decode("utf-8"))
    user_books = books_body["books"]
    # Le livre pilote doit être visible pour tout utilisateur (modèle de référence)
    titres = [b["titre"] for b in user_books]
    assert "L'INTELLIGENCE FINANCIÈRE PRATIQUE" in titres, "Le livre pilote doit être visible pour un nouvel utilisateur !"
    print("  ✅ Visibilité confirmée : le livre pilote de référence est visible pour le nouvel utilisateur.")

    # 5. Test Déduction de 1 Crédit lors de la création d'un livre
    print("\n🔍 5. Test Déduction de Crédit sur POST /api/books/create...")
    create_req = app_studio.CreateBookRequest(
        niche="Stoïcisme Moderne",
        titre="L'Art Stoïcien du Calme Intérieur",
        format_kdp="6x9",
        nb_chapitres=3
    )
    mock_bg = MagicMock(spec=BackgroundTasks)
    res_create = app_studio.api_creer_livre(create_req, mock_bg, current_user=current_u1)
    create_body = json.loads(res_create.body.decode("utf-8"))
    assert res_create.status_code == 200, f"Attendu HTTP 200, reçu {res_create.status_code}"
    new_book_id = create_body["book_id"]
    assert create_body["credits_restants"] == 2, f"Le solde de crédits devrait être 2, reçu : {create_body['credits_restants']}"

    # Vérification insertion immédiate statut='en_cours' et progression=5
    livre_initial = studio_db.obtenir_livre(new_book_id, user_id=user_id)
    assert livre_initial["statut"] == "en_cours", f"Attendu 'en_cours', reçu '{livre_initial['statut']}'"
    assert livre_initial["progression"] == 5, f"Attendu 5, reçu {livre_initial['progression']}"
    print(f"  ✅ Livre #{new_book_id} immédiatement inséré en base (statut='en_cours', progression=5%).")
    print(f"  ✅ Route retourne HTTP 200, solde débité de 1 crédit (Crédits restants : 2).")

    # Vérification que l'utilisateur voit son livre
    res_my_books = app_studio.api_lister_livres(current_user=current_u1)
    my_books = json.loads(res_my_books.body.decode("utf-8"))["books"]
    my_book_ids = [b["id"] for b in my_books]
    assert new_book_id in my_book_ids
    print(f"  ✅ L'utilisateur voit son propre livre (#{new_book_id}).")

    # 6. Test Épuisement des Crédits & Blocage HTTP 402 Payment Required
    print("\n🔍 6. Test Épuisement des Crédits & Blocage HTTP 402...")
    studio_db.modifier_credits_utilisateur(user_id, -2) # de 2 à 0
    refreshed_user = studio_db.obtenir_utilisateur_par_id(user_id)
    assert refreshed_user["credits"] == 0

    try:
        app_studio.api_creer_livre(create_req, mock_bg, current_user=refreshed_user)
        assert False, "Aurait dû lever HTTPException 402 !"
    except HTTPException as h_err:
        assert h_err.status_code == 402, f"Attendu 402, reçu {h_err.status_code}"
        print(f"  ✅ Blocage 402 Payment Required confirmé : '{h_err.detail}'")

    # 7. Test Sécurité Fichiers & Accès au Livre Pilote
    print("\n🔍 7. Test Accès Fichiers & Protection Inter-Utilisateurs...")
    # L'utilisateur a accès au fichier du livre pilote de référence (ID #1)
    res_pilot_file = app_studio.api_telecharger_fichier(
        book_id=1,
        file_type="manuscrit_md",
        preview=True,
        current_user=refreshed_user
    )
    assert res_pilot_file.status_code == 200, "Le livre pilote doit être consultable et téléchargeable !"
    print("  ✅ Accès et prévisualisation des fichiers du livre pilote confirmés.")

    # L'utilisateur ordinaire NE peut PAS supprimer le livre pilote
    suppr_pilote = studio_db.supprimer_livre(1, user_id=user_id, est_admin=False)
    assert suppr_pilote is False, "Le livre pilote ne doit pas être supprimable par un utilisateur standard !"
    print("  ✅ Protection anti-suppression du livre pilote confirmée.")

    # 8. Test Remboursement Automatique si Erreur
    print("\n🔍 8. Test Remboursement de Crédit en cas d'erreur de production...")
    solde_avant = studio_db.obtenir_utilisateur_par_id(user_id)["credits"]
    # Déclencher une erreur dans produire_livre_background avec nb_chapitres invalide
    app_studio.produire_livre_background(
        book_id=new_book_id,
        niche="Crash Test",
        titre="Erreur Provoquée",
        sous_titre="",
        format_kdp="6x9",
        nb_chapitres=None, # provoque TypeError
        user_id=user_id
    )
    solde_apres = studio_db.obtenir_utilisateur_par_id(user_id)["credits"]
    assert solde_apres == solde_avant + 1, f"Le crédit aurait dû être remboursé (+1), avant={solde_avant}, apres={solde_apres}"
    print(f"  ✅ Remboursement validé : Solde rétabli de {solde_avant} à {solde_apres} crédits (+1).")

    # Nettoyage du livre et dossier de test
    studio_db.supprimer_livre(new_book_id, user_id=user_id)
    dossier_test = Path("books") / f"livre_{new_book_id}_lart_stoicien_du_calme_interieur"
    if dossier_test.exists():
        shutil.rmtree(dossier_test, ignore_errors=True)
    dossier_crash = Path("books") / f"livre_{new_book_id}_erreur_provoquee"
    if dossier_crash.exists():
        shutil.rmtree(dossier_crash, ignore_errors=True)
    dossier_inv = Path("books") / "livre_999999_invalide_path"
    if dossier_inv.exists():
        shutil.rmtree(dossier_inv, ignore_errors=True)
    print("  ✅ Nettoyage des fichiers temporaires effectué.")

    print("\n" + "=" * 65)
    print("🎉 TOUS LES 8 TESTS SAAS MULTI-UTILISATEURS & CRÉDITS SONT AU VERT !")
    print("=" * 65)

except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
