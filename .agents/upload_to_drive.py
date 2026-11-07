"""
Outil de transfert et de sauvegarde vers Google Drive (MarkEddy)
Permet de sauvegarder le PDF finalisé directement sur votre Drive pour sa publication.
"""

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Déclaration des accès requis pour Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

PDF_LOCAL = Path("livre_parfait_kdp.pdf")

def authentifier_google_drive():
    """Gère la connexion sécurisée Oauth2 avec Google Drive."""
    creds = None
    # Si des clés de connexion existent déjà, on les utilise
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si aucune clé ou si elles ont expiré, on lance la demande d'authentification
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ Fichier credentials.json introuvable.")
                print("👉 Pour l'obtenir : allez sur Google Cloud Console, créez un projet, activez la 'Drive API',")
                print("   puis téléchargez vos identifiants OAuth au format JSON dans ce dossier sous le nom 'credentials.json'.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Sauvegarde de la clé pour les prochaines connexions
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def transferer_fichier_sur_drive():
    if not PDF_LOCAL.exists():
        print(f"❌ Erreur : Le fichier local {PDF_LOCAL.name} est introuvable sur votre disque dur.")
        return

    creds = authentifier_google_drive()
    if not creds:
        return

    try:
        service = build('drive', 'v3', credentials=creds)

        print(f"☁️  Tentative de transfert de '{PDF_LOCAL.name}' vers votre Google Drive...")
        
        # Définition des métadonnées du fichier
        metadata_fichier = {
            'name': 'Maîtriser ses finances personnelles - Version finale d\'impression (6x9) - MarkEddy.pdf',
            'mimeType': 'application/pdf'
        }
        
        media = MediaFileUpload(
            str(PDF_LOCAL),
            mimetype='application/pdf',
            resumable=True
        )

        # Envoi effectif
        fichier_drive = service.files().create(
            body=metadata_fichier,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        print("=" * 65)
        print("🎉 TRANSFERT RÉUSSI AVEC SUCCÈS !")
        print("=" * 65)
        print(f"📁 Fichier sur votre ordinateur : {PDF_LOCAL.resolve()}")
        print(f"🆔 Identifiant Google Drive       : {fichier_drive.get('id')}")
        print(f"🔗 Lien direct pour le Drive     : {fichier_drive.get('webViewLink')}")
        print("=" * 65)

    except Exception as e:
        print(f"❌ Une erreur s'est produite lors du transfert : {e}")

if __name__ == "__main__":
    transferer_fichier_sur_drive()