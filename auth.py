"""
auth.py - Module d'Authentification & Sécurité pour MarkEddy KDP Studio.
Gère le hachage sécurisé des mots de passe (PBKDF2/SHA-256 et Bcrypt)
et la génération/validation de jetons JWT conformes RFC 7519.
"""

import os
import time
import json
import hmac
import hashlib
import base64
import secrets
from typing import Optional, Dict, Any

# Clé secrète pour la signature des jetons JWT
JWT_SECRET = os.getenv("JWT_SECRET", "markeddy_kdp_luxury_secret_key_2026_super_secure_vault")
TOKEN_DUREE_HEURES_DEFAUT = 720  # 30 jours de validité

# ==============================================================================
# HACHAGE & VÉRIFICATION DES MOTS DE PASSE
# ==============================================================================

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """
    Hache le mot de passe de manière sécurisée.
    Utilise bcrypt s'il est installé, sinon PBKDF2-HMAC-SHA256 (100 000 itérations + sel).
    """
    try:
        import bcrypt
        sel = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel).decode("utf-8")
    except ImportError:
        pass

    # Fallback standard cryptographiquement sûr (NIST SP 800-132)
    sel = secrets.token_hex(16)
    derive = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode("utf-8"), sel.encode("utf-8"), 100000)
    return f"pbkdf2:sha256:100000${sel}${derive.hex()}"


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    """Vérifie si le mot de passe brut correspond au hash stocké."""
    if not mot_de_passe or not hash_stocke:
        return False

    # 1. Vérification bcrypt
    if hash_stocke.startswith("$2b$") or hash_stocke.startswith("$2a$"):
        try:
            import bcrypt
            return bcrypt.checkpw(mot_de_passe.encode("utf-8"), hash_stocke.encode("utf-8"))
        except ImportError:
            pass

    # 2. Vérification PBKDF2
    if hash_stocke.startswith("pbkdf2:sha256:"):
        morceaux = hash_stocke.split("$")
        if len(morceaux) == 3:
            _, sel, h_hex = morceaux
            calcule = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode("utf-8"), sel.encode("utf-8"), 100000).hex()
            return hmac.compare_digest(calcule, h_hex)

    return False


# ==============================================================================
# GESTION DES JETONS JWT (RFC 7519)
# ==============================================================================

def _b64url_encode(donnees: bytes) -> str:
    return base64.urlsafe_b64encode(donnees).decode("utf-8").rstrip("=")


def _b64url_decode(chaine: str) -> bytes:
    padding = "=" * (-len(chaine) % 4)
    return base64.urlsafe_b64decode(chaine + padding)


def creer_jeton_acces(payload: Dict[str, Any], expire_heures: int = TOKEN_DUREE_HEURES_DEFAUT) -> str:
    """Génère un jeton JWT HS256 signé."""
    payload_complet = payload.copy()
    payload_complet["iat"] = int(time.time())
    payload_complet["exp"] = int(time.time()) + (expire_heures * 3600)

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload_complet, separators=(",", ":")).encode("utf-8"))

    msg = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decoder_jeton_acces(jeton: str) -> Dict[str, Any]:
    """
    Vérifie la signature et la validité temporelle du jeton JWT.
    Lève ValueError si le jeton est invalide ou expiré.
    """
    if not jeton or not jeton.strip():
        raise ValueError("Jeton absent ou vide.")

    parties = jeton.strip().split(".")
    if len(parties) != 3:
        raise ValueError("Structure JWT invalide.")

    header_b64, payload_b64, sig_b64 = parties

    # Vérification de la signature HMAC
    msg = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig_attendue = hmac.new(JWT_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    sig_reçue = _b64url_decode(sig_b64)

    if not hmac.compare_digest(sig_reçue, sig_attendue):
        raise ValueError("Signature du jeton invalide.")

    # Décodage du payload
    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as e:
        raise ValueError("Payload JWT non décodable.") from e

    # Contrôle de l'expiration
    if "exp" in payload and payload["exp"] < time.time():
        raise ValueError("Jeton de session expiré. Veuillez vous reconnecter.")

    return payload
