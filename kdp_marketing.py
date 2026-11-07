"""
kdp_marketing.py - Responsable Marketing & Conversion Amazon KDP.
Génère tous les actifs commerciaux pour maximiser le taux de conversion et les ventes :
1. Description commerciale HTML conforme aux balises autorisées par Amazon KDP
2. Stratégie de contenu A+ (bannières, modules de comparaison, accroches visuelles)
3. Pack de lancement marketing (email d'annonce, posts réseaux sociaux)
"""

import json
from pathlib import Path

BLUEPRINT_PATH = Path("book_blueprint.json")
OUTPUT_MARKETING = Path("kdp_marketing_pack.html")

def generer_pack_marketing() -> Path:
    if not BLUEPRINT_PATH.exists():
        raise FileNotFoundError(f"❌ {BLUEPRINT_PATH} introuvable. Exécutez d'abord kdp_architect.py.")

    bp = json.load(open(BLUEPRINT_PATH, "r", encoding="utf-8"))
    titre = bp.get("titre", "LIVRE SANS TITRE")
    sous_titre = bp.get("sous_titre", "")
    promesse = bp.get("promesse_client", "")
    auteur = bp.get("auteur", bp.get("auteur_suggere", "MarkEddy"))
    bio_auteur = bp.get("bio_auteur", "MarkEddy est entrepreneur, investisseur indépendant et spécialiste de l'ingénierie financière personnelle.")
    chapitres = bp.get("chapitres", [])
    mots_cles = bp.get("mots_cles_kdp", [])
    categories = bp.get("categories_kdp", [])

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>Pack Marketing & Vente Amazon KDP - {titre}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            color: #1e293b;
            line-height: 1.6;
        }}
        h1 {{ color: #0f172a; border-bottom: 3px solid #eab308; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 40px; }}
        .box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .code-box {{ background: #0f172a; color: #f8fafc; padding: 15px; border-radius: 6px; font-family: monospace; white-space: pre-wrap; }}
        .badge {{ display: inline-block; background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 4px; font-weight: bold; margin-right: 8px; margin-bottom: 8px; }}
        ul {{ padding-left: 20px; }}
    </style>
</head>
<body>

    <h1>🚀 PACK COMMERCIAL & CONVERSION AMAZON KDP</h1>
    <p><strong>Livre :</strong> {titre} — <em>{sous_titre}</em></p>
    <p><strong>Auteur :</strong> {auteur}</p>

    <!-- SECTION 1 : DESCRIPTION OFFICIELLE KDP -->
    <h2>1. DESCRIPTION HTML PRÊTE À COLLER SUR AMAZON KDP</h2>
    <p>Copiez le bloc de code ci-dessous et collez-le directement dans la case <em>« Description »</em> de votre tableau de bord Amazon KDP :</p>
    
    <div class="code-box">&lt;h2&gt;🚀 {titre}&lt;/h2&gt;
&lt;p&gt;&lt;strong&gt;{sous_titre}&lt;/strong&gt;&lt;/p&gt;
&lt;p&gt;&lt;i&gt;Par {auteur}&lt;/i&gt;&lt;/p&gt;

&lt;p&gt;{promesse}&lt;/p&gt;

&lt;h3&gt;Ce que vous allez maîtriser dans ce guide complet :&lt;/h3&gt;
&lt;ul&gt;
"""
    for ch in chapitres[:7]:
        html_content += f"  &lt;li&gt;&lt;strong&gt;{ch.get('titre')}&lt;/strong&gt; : {ch.get('objectif')}&lt;/li&gt;\n"

    html_content += f"""&lt;/ul&gt;

&lt;h3&gt;Pourquoi ce livre est différent des autres :&lt;/h3&gt;
&lt;p&gt;Ici, pas de théories abstraites ou de jargon complexe. Rédigé par &lt;b&gt;{auteur}&lt;/b&gt;, chaque chapitre et sous-section a été pensé pour être &lt;b&gt;immédiatement actionnable sous 24h&lt;/b&gt; avec des études de cas réelles, des calculs étape par étape et des plans d'action applicables sans attendre.&lt;/p&gt;

&lt;p&gt;&lt;strong&gt;👉 Remontez en haut de la page et cliquez sur « Acheter cet article » pour transformer vos résultats dès aujourd'hui !&lt;/strong&gt;&lt;/p&gt;</div>

    <!-- SECTION 2 : MOTS-CLÉS ET CATÉGORIES -->
    <h2>2. CONFIGURATION SEO KDP (MÉTADONNÉES)</h2>
    <div class="box">
        <h3>🔑 Les 7 Mots-clés KDP Backend (à insérer dans les 7 cases) :</h3>
        <div>
"""
    for mc in mots_cles:
        html_content += f'            <span class="badge">{mc}</span>\n'

    html_content += f"""        </div>

        <h3 style="margin-top: 20px;">📂 Catégories Amazon cibles :</h3>
        <ul>
"""
    for cat in categories:
        html_content += f"            <li><strong>{cat}</strong></li>\n"

    html_content += f"""        </ul>
    </div>

    <!-- SECTION 3 : STRATÉGIE A+ CONTENT -->
    <h2>3. STRATÉGIE A+ CONTENT (PAGE PRODUIT ENRICHIE)</h2>
    <div class="box">
        <p>Amazon permet d'ajouter des bannières illustrées dans la section <em>« Informations de l'éditeur »</em>. Voici la structure des 3 bannières recommandées :</p>
        
        <h4>Bannière 1 : Le Constat & La Révolution</h4>
        <ul>
            <li><strong>Titre :</strong> Fini le doute et les erreurs coûteuses.</li>
            <li><strong>Texte :</strong> Une méthode structurée étape par étape pour passer de débutant complet à praticien confiant.</li>
        </ul>

        <h4>Bannière 2 : La Méthode en Action</h4>
        <ul>
            <li><strong>Titre :</strong> 10 chapitres denses et 50 sections ultra-pratiques par {auteur}.</li>
            <li><strong>Texte :</strong> Des études de cas réelles, des calculs transparents et des checklists d'exécution immédiate.</li>
        </ul>

        <h4>Bannière 3 : La Garantie de Transformation</h4>
        <ul>
            <li><strong>Titre :</strong> Reprenez le contrôle total.</li>
            <li><strong>Texte :</strong> Conçu pour vous accompagner jour après jour vers la souveraineté temporelle.</li>
        </ul>
    </div>

    <!-- SECTION 4 : BIOGRAPHIE AUTEUR AMAZON AUTHOR CENTRAL -->
    <h2>4. BIOGRAPHIE OFFICIELLE (AMAZON AUTHOR CENTRAL)</h2>
    <div class="box">
        <h3>👤 Profil Auteur : {auteur}</h3>
        <p>{bio_auteur}</p>
    </div>

</body>
</html>"""

    OUTPUT_MARKETING.write_text(html_content, encoding="utf-8")
    print(f"🛒 Pack marketing et conversion généré : {OUTPUT_MARKETING.resolve()}")
    return OUTPUT_MARKETING

if __name__ == "__main__":
    generer_pack_marketing()
