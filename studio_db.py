"""
studio_db.py - Gestionnaire de Base de Données SQLite Multi-Utilisateurs.
Prend en charge :
1. Table 'users' (authentification, quotas, crédits, plan).
2. Table 'books' avec isolation stricte par 'user_id'.
3. Migration dynamique et utilisateur admin par défaut.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

import auth

DB_PATH = Path("kdp_studio.db")
BASE_DIR = Path(__file__).resolve().parent

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise les tables users et books, effectue les migrations et configure l'admin."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. TABLE DES UTILISATEURS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                credits INTEGER DEFAULT 3,
                plan TEXT DEFAULT 'gratuit',
                created_at TEXT NOT NULL
            )
        """)

        # 2. TABLE DES LIVRES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1 REFERENCES users(id),
                type_projet TEXT DEFAULT 'non-fiction',
                theme_coloriage TEXT,
                nb_illustrations INTEGER DEFAULT 0,
                image_couverture_url TEXT,
                project_type TEXT DEFAULT 'non_fiction',
                cover_image_url TEXT,
                titre TEXT NOT NULL,
                sous_titre TEXT,
                niche TEXT,
                format_kdp TEXT DEFAULT '6x9',
                nb_chapitres INTEGER DEFAULT 10,
                statut TEXT DEFAULT 'en_attente',
                progression INTEGER DEFAULT 0,
                etape_courante TEXT DEFAULT 'Initialisation...',
                nb_mots INTEGER DEFAULT 0,
                nb_pages INTEGER DEFAULT 0,
                chemin_pdf_interieur TEXT,
                chemin_pdf_couverture TEXT,
                chemin_epub TEXT,
                chemin_marketing_html TEXT,
                chemin_couverture_jpg TEXT,
                chemin_manuscrit_md TEXT,
                chemin_interieur_html TEXT,
                score_qa INTEGER DEFAULT 100,
                date_creation TEXT NOT NULL
            )
        """)
        conn.commit()

        # MIGRATIONS DYNAMIQUES
        cursor.execute("PRAGMA table_info(books)")
        colonnes = [col["name"] for col in cursor.fetchall()]
        if "user_id" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN user_id INTEGER DEFAULT 1 REFERENCES users(id)")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'user_id' ajoutée à la table 'books'.")
        if "type_projet" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN type_projet TEXT DEFAULT 'non-fiction'")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'type_projet' ajoutée à la table 'books'.")
        if "theme_coloriage" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN theme_coloriage TEXT")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'theme_coloriage' ajoutée à la table 'books'.")
        if "nb_illustrations" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN nb_illustrations INTEGER DEFAULT 0")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'nb_illustrations' ajoutée à la table 'books'.")
        if "image_couverture_url" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN image_couverture_url TEXT")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'image_couverture_url' ajoutée à la table 'books'.")
        if "project_type" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN project_type TEXT DEFAULT 'non_fiction'")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'project_type' ajoutée à la table 'books'.")
        if "cover_image_url" not in colonnes:
            cursor.execute("ALTER TABLE books ADD COLUMN cover_image_url TEXT")
            conn.commit()
            print("🔄 Migration effectuée : colonne 'cover_image_url' ajoutée à la table 'books'.")

    # Création du compte administrateur par défaut
    admin_id = _creer_admin_par_defaut()

    # Rattachement des livres orphelins à l'admin
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET user_id = ? WHERE user_id IS NULL OR user_id = 0", (admin_id,))
        conn.commit()

    # Import du livre pilote si absent
    importer_livre_pilote(admin_id=admin_id)


def _creer_admin_par_defaut() -> int:
    """Crée l'utilisateur administrateur par défaut s'il n'existe pas encore."""
    admin_email = "admin@markeddy.com"
    admin_user = obtenir_utilisateur_par_email(admin_email)
    if admin_user:
        return admin_user["id"]

    hash_mdp = auth.hacher_mot_de_passe("Admin123!")
    admin_id = creer_utilisateur(
        email=admin_email,
        password_hash=hash_mdp,
        credits=999,
        plan="admin"
    )
    print(f"👑 Compte administrateur par défaut créé : {admin_email} (ID #{admin_id}).")
    return admin_id


# ==============================================================================
# GESTION DES UTILISATEURS
# ==============================================================================

def creer_utilisateur(
    email: str,
    password_hash: str,
    credits: int = 3,
    plan: str = "gratuit"
) -> int:
    """Insère un nouvel utilisateur avec ses crédits initiaux."""
    with get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO users (email, password_hash, credits, plan, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (email.lower().strip(), password_hash, credits, plan, now))
        conn.commit()
        return cursor.lastrowid


def obtenir_utilisateur_par_email(email: str) -> Optional[Dict[str, Any]]:
    """Récupère un utilisateur via son adresse email."""
    if not email:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None


def obtenir_utilisateur_par_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un utilisateur via son ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def modifier_credits_utilisateur(user_id: int, delta: int) -> int:
    """
    Modifie le solde de crédits de l'utilisateur (delta positif ou négatif).
    Retourne le nouveau solde de crédits.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (delta, user_id))
        cursor.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.commit()
        return row["credits"] if row else 0


# ==============================================================================
# GESTION DES LIVRES (ISOLATION MULTI-UTILISATEURS)
# ==============================================================================

def importer_livre_pilote(admin_id: int = 1):
    """
    Importe automatiquement le projet pilote 'L'INTELLIGENCE FINANCIÈRE PRATIQUE'
    au démarrage de init_db() si la table 'books' est vide (ou si le livre pilote n'est pas encore enregistré)
    et que 'manuscrit_complet.md' existe à la racine du projet.
    """
    manuscrit_path = BASE_DIR / "manuscrit_complet.md"
    if not manuscrit_path.exists():
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as nb FROM books")
        nb_total = cursor.fetchone()["nb"]

        cursor.execute("SELECT id FROM books WHERE titre = ?", ("L'INTELLIGENCE FINANCIÈRE PRATIQUE",))
        deja_present = cursor.fetchone()

        # Si des livres existent déjà et que le pilote est déjà présent, pas d'import en double
        if nb_total > 0 and deja_present:
            return

        titre = "L'INTELLIGENCE FINANCIÈRE PRATIQUE"
        sous_titre = "Comprendre vos biais émotionnels, automatiser votre épargne et investir sereinement pour bâtir votre liberté financière sans privation : la méthode pas-à-pas en 10 étapes"
        niche = "Finances Personnelles & Psychologie de l'Argent"
        format_kdp = "6x9"
        nb_chapitres = 10
        nb_mots = 28143
        nb_pages = 112

        chemin_pdf_couverture = "couverture_kdp_complete.pdf" if (BASE_DIR / "couverture_kdp_complete.pdf").exists() else "couvertures_finales/Couverture_OFFICIELLE_KDP.pdf"
        chemin_pdf_interieur = "livre_kdp_interieur.pdf" if (BASE_DIR / "livre_kdp_interieur.pdf").exists() else "interieurs_finaux/Interieur_6.0x9.0.pdf"
        chemin_epub = "livre_ebook_kdp.epub" if (BASE_DIR / "livre_ebook_kdp.epub").exists() else "ebooks_finaux/l-intelligence-financiere-pratique.epub"
        chemin_marketing_html = "kdp_marketing_pack.html"
        chemin_couverture_jpg = "couverture_ebook.jpg" if (BASE_DIR / "couverture_ebook.jpg").exists() else "couvertures_export/01_amazon_kdp_ebook_cover.jpg"
        chemin_manuscrit_md = "manuscrit_complet.md"
        chemin_interieur_html = "livre_kdp_interieur.html"

        date_creation = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO books (
                user_id, titre, sous_titre, niche, format_kdp, nb_chapitres,
                statut, progression, etape_courante, nb_mots, nb_pages,
                chemin_pdf_interieur, chemin_pdf_couverture, chemin_epub,
                chemin_marketing_html, chemin_couverture_jpg, chemin_manuscrit_md,
                chemin_interieur_html, score_qa, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            admin_id, titre, sous_titre, niche, format_kdp, nb_chapitres,
            "termine", 100, "Livre certifié KDP 100/100 (Print & eBook Ready)", nb_mots, nb_pages,
            str(chemin_pdf_interieur), str(chemin_pdf_couverture), str(chemin_epub),
            str(chemin_marketing_html), str(chemin_couverture_jpg), str(chemin_manuscrit_md),
            str(chemin_interieur_html), 100, date_creation
        ))
        conn.commit()
        print("✅ Livre pilote 'L'INTELLIGENCE FINANCIÈRE PRATIQUE' importé et rattaché à l'administrateur.")


def lister_livres(user_id: Optional[int] = None, est_admin: bool = False) -> List[Dict[str, Any]]:
    """
    Retourne la liste des livres.
    - Si est_admin=True ou user_id=None : retourne tous les livres de la plateforme.
    - Pour un utilisateur ordinaire ou compte démo : retourne ses propres livres
      ainsi que le livre pilote officiel 'L\'INTELLIGENCE FINANCIÈRE PRATIQUE' (modèle vitrine KDP).
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        if est_admin or user_id is None:
            cursor.execute("SELECT * FROM books ORDER BY id DESC")
        else:
            cursor.execute("""
                SELECT * FROM books 
                WHERE user_id = ? OR titre = 'L''INTELLIGENCE FINANCIÈRE PRATIQUE'
                ORDER BY id DESC
            """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]


def obtenir_livre(book_id: int, user_id: Optional[int] = None, est_admin: bool = False) -> Optional[Dict[str, Any]]:
    """
    Récupère un livre par son ID avec contrôle d'accès.
    L'administrateur, le créateur du livre, ou tout utilisateur consultant
    le livre pilote de référence ont un accès autorisé.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        if not row:
            return None
        livre = dict(row)
        if est_admin or user_id is None:
            return livre
        # Le livre pilote est accessible à tous en lecture / téléchargement
        if livre.get("titre") == "L'INTELLIGENCE FINANCIÈRE PRATIQUE":
            return livre
        # Livre privé de l'utilisateur
        if livre.get("user_id") == user_id:
            return livre
        return None


def creer_livre(
    user_id: int,
    titre: str,
    sous_titre: str = "",
    niche: str = "",
    format_kdp: str = "6x9",
    nb_chapitres: int = 10,
    statut: str = "en_cours",
    progression: int = 5,
    etape_courante: str = "Initialisation du pipeline de production...",
    type_projet: str = "non-fiction",
    theme_coloriage: Optional[str] = None,
    nb_illustrations: int = 0,
    image_couverture_url: Optional[str] = None,
    project_type: str = "non_fiction",
    cover_image_url: Optional[str] = None
) -> int:
    """Insère immédiatement un nouveau projet de livre rattaché à son propriétaire user_id."""
    with get_connection() as conn:
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO books (
                user_id, titre, sous_titre, niche, format_kdp, nb_chapitres,
                statut, progression, etape_courante, type_projet, theme_coloriage,
                nb_illustrations, image_couverture_url, project_type, cover_image_url,
                score_qa, date_creation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 100, ?)
        """, (
            user_id, titre, sous_titre, niche, format_kdp, nb_chapitres,
            statut, progression, etape_courante, type_projet, theme_coloriage,
            nb_illustrations, image_couverture_url,
            project_type or "non_fiction", cover_image_url, now
        ))
        conn.commit()
        return cursor.lastrowid


def mettre_a_jour_livre(book_id: int, **kwargs):
    """Met à jour les attributs d'un livre désigné."""
    if not kwargs:
        return
    champs = []
    valeurs = []
    for k, v in kwargs.items():
        champs.append(f"{k} = ?")
        valeurs.append(v)
    valeurs.append(book_id)

    requete = f"UPDATE books SET {', '.join(champs)} WHERE id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(requete, valeurs)
        conn.commit()


def supprimer_livre(book_id: int, user_id: Optional[int] = None, est_admin: bool = False) -> bool:
    """
    Supprime un livre.
    Seul l'administrateur est autorisé à supprimer le livre pilote officiel.
    Un utilisateur ordinaire ne peut supprimer que ses propres projets.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        if not row:
            return False
        livre = dict(row)
        if livre.get("titre") == "L'INTELLIGENCE FINANCIÈRE PRATIQUE" and not est_admin:
            return False  # Protection du livre pilote

        if est_admin or user_id is None:
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        else:
            cursor.execute("DELETE FROM books WHERE id = ? AND user_id = ?", (book_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


if __name__ == "__main__":
    init_db()
    livres = lister_livres(est_admin=True)
    print(f"Total de livres en base : {len(livres)}")
    for l in livres:
        print(f" - [ID {l['id']} / User #{l.get('user_id')}] {l['titre']} ({l['statut']})")
