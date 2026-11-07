"""
Auditeur pré-presse autonome (KDP Preflight Inspector).
Analyse l'intégralité des fichiers de sortie avant téléversement sur Amazon KDP.
"""

import json
from pathlib import Path
import pypdf  # Si non installé: pip install pypdf

MANUSCRIT = Path("manuscrit_enrichi.md") if Path("manuscrit_enrichi.md").exists() else Path("manuscrit_complet.md")
PDF_COUVERTURE = Path("couverture_kdp_complete.pdf")
PDF_INTERIEUR = Path("livre_kdp_interieur.pdf")
RAPPORT_BAT = Path("rapport_preflight_kdp.json")


def inspecter_manuscrit():
    if not MANUSCRIT.exists():
        return {"status": "ERREUR", "detail": "Manuscrit absent."}

    texte = MANUSCRIT.read_text(encoding="utf-8")
    mots = len(texte.split())
    pages_estimees = mots // 250

    anomalies = []
    if "TODO" in texte or "[insérer" in texte.lower():
        anomalies.append("Marqueurs résiduels de rédaction détectés (TODO/insérer).")
    if mots < 35000:
        anomalies.append(f"Volume insuffisant : {mots:,} mots (seuil recommandé : 35 000 mots).")

    return {
        "status": "SUCCÈS" if not anomalies else "AVERTISSEMENT",
        "total_mots": mots,
        "pages_estimees": pages_estimees,
        "anomalies": anomalies
    }


def inspecter_couverture_pdf():
    if not PDF_COUVERTURE.exists():
        return {"status": "NON_GÉNÉRÉ", "detail": "Fichier couverture_kdp_complete.pdf absent."}

    try:
        reader = pypdf.PdfReader(str(PDF_COUVERTURE))
        page = reader.pages[0]
        largeur_pt = float(page.mediabox.width)
        hauteur_pt = float(page.mediabox.height)

        # 1 pouce = 72 points typographiques
        largeur_in = largeur_pt / 72
        hauteur_in = hauteur_pt / 72

        return {
            "status": "SUCCÈS",
            "largeur_pouces": round(largeur_in, 3),
            "hauteur_pouces": round(hauteur_in, 3),
            "hauteur_conforme_kdp_9_25in": abs(hauteur_in - 9.25) < 0.05
        }
    except Exception as e:
        return {"status": "ERREUR", "detail": str(e)}


def executer_audit_global():
    print("=" * 60)
    print("🛡️ INSPECTION PRÉ-PRESSE KDP (PREFLIGHT CONTROL)")
    print("=" * 60)

    rapport = {
        "audit_manuscrit": inspecter_manuscrit(),
        "audit_couverture": inspecter_couverture_pdf()
    }

    RAPPORT_BAT.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n1. Manuscrit :", rapport["audit_manuscrit"]["status"])
    print(f"   -> {rapport['audit_manuscrit'].get('total_mots', 0):,} mots (~{rapport['audit_manuscrit'].get('pages_estimees', 0)} pages)")
    
    print("\n2. Couverture PDF :", rapport["audit_couverture"]["status"])
    if rapport["audit_couverture"]["status"] == "SUCCÈS":
        print(f"   -> Dimensions : {rapport['audit_couverture']['largeur_pouces']}\" x {rapport['audit_couverture']['hauteur_pouces']}\"")
        if rapport["audit_couverture"]["hauteur_conforme_kdp_9_25in"]:
            print("   -> Hauteur conforme (9 po + 0.25 po de fond perdu).")

    print(f"\n📄 Rapport d'inspection enregistré : {RAPPORT_BAT.name}")


if __name__ == "__main__":
    executer_audit_global()