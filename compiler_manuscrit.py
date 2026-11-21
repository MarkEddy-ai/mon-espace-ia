# -*- coding: utf-8 -*-
"""
compiler_manuscrit.py - Compilation Haute Couture de manuscrit_complet.md
L'ARCHITECTE FINANCIER par MarkEddy
"""

import json
from pathlib import Path

BLUEPRINT_PATH = Path("book_blueprint.json")
SECTIONS_DIR = Path("livre_sections")
MANUSCRIT_PATH = Path("manuscrit_complet.md")

with open(BLUEPRINT_PATH, "r", encoding="utf-8") as f:
    bp = json.load(f)

titre = bp.get("titre", "L'ARCHITECTE FINANCIER")
sous_titre = bp.get("sous_titre", "")
auteur = bp.get("auteur", "MarkEddy")
chapitres = bp.get("chapitres", [])

lignes = []

# Page de Titre
lignes.append(f"# {titre.upper()}")
lignes.append(f"*{sous_titre}*\n")
lignes.append(f"**Par {auteur}**\n")
lignes.append("---\n")

# Mentions Légales et Avertissement
lignes.append("## MENTIONS LÉGALES & AVERTISSEMENT DU LECTEUR\n")
lignes.append("""*L'Architecte Financier : Le Système Automatisé pour Maîtriser son Budget sans Privation, Éliminer ses Dettes et Bâtir un Patrimoine Passif avec un Salaire Ordinaire.*

© 2026 MarkEddy. Tous droits réservés.

Aucune partie de cette publication ne peut être reproduite, distribuée ou transmise sous quelque forme ou par quelque moyen que ce soit, y compris par photocopie, enregistrement ou autres méthodes électroniques ou mécaniques, sans l'autorisation écrite préalable de l'auteur, excepté dans le cadre de courtes citations intégrées dans des recensions critiques ou analyses autorisées par la loi.

**Avertissement de non-responsabilité :** Ce livre a été rédigé à des fins strictement pédagogiques, éducatives et d'information générale. L'auteur et l'éditeur ne fournissent pas de conseils financiers, juridiques ou fiscaux personnalisés. Les stratégies, études de cas et calculs présentés reflètent des situations documentées et des principes généraux de gestion budgétaire et d'investissement indiciel. Tout investissement comporte un risque de perte en capital et les performances passées ne préjugent pas des performances futures. Chaque lecteur est invité à évaluer sa propre situation patrimoniale et à consulter des professionnels réglementés (conseillers en gestion de patrimoine, notaires, experts-comptables) avant de prendre des décisions financières significatives.
""")
lignes.append("---\n")

# Table des Matières
lignes.append("## TABLE DES MATIÈRES DÉTAILLÉE\n")
for c in chapitres:
    c_num = c.get("numero")
    c_titre = c.get("titre")
    lignes.append(f"**Chapitre {c_num} : {c_titre}**")
    for s_idx, s in enumerate(c.get("sections", []), start=1):
        s_titre = s.get("titre")
        lignes.append(f"- *{c_num}.{s_idx} {s_titre}*")
    lignes.append("")
lignes.append("---\n")

# Introduction Générale
lignes.append("# INTRODUCTION : LE DÉCLIC DE LA SOUVERAINETÉ\n")
lignes.append("""Si vous tenez ce livre entre vos mains, c'est probablement parce que vous ressentez, de manière diffuse ou aiguë, une contradiction intolérable au cœur de votre existence matérielle.

Vous travaillez dur. Vous respectez les règles du jeu social : vous avez poursuivi des études ou appris un métier, vous vous levez chaque matin pour échanger 40 heures de votre énergie hebdomadaire contre un virement bancaire mensuel. Pourtant, le 20 ou le 25 du mois venu, lorsque vous consultez le solde de votre compte sur votre smartphone, la même question lancinante vous étreint la gorge : *« Mais où est donc passé tout cet argent ? »*

Le sentiment de vulnérabilité financière n'a rien à voir avec le montant de vos revenus. Des ouvriers du bâtiment dorment sur leurs deux oreilles avec 1 900 € net par mois, tandis que des cadres dirigeants à 5 000 € passent leurs nuits en sueur, tétanisés par l'échéance d'une régularisation d'impôts ou le bruit suspect sous le capot de leur voiture en leasing.

La vérité que l'industrie bancaire et la société de consommation vous dissimulent soigneusement est la suivante : **vos difficultés ne proviennent pas d'un manque de salaire, elles proviennent d'une faillite de structure**.

On vous a appris à travailler pour l'argent ; on ne vous a jamais appris à concevoir l'architecture qui force l'argent à travailler pour vous. Vous avez été dressé à vous comporter en consommateur réactif — payant d'abord votre propriétaire, vos fournisseurs d'énergie, l'État et les plateformes de commerce en ligne — avant de vous accorder les miettes résiduelles de votre propre labeur.

Ce livre est le plan de démolition de cette prison dorée.

En tant qu'**Architecte Financier**, vous n'allez pas apprendre à vous priver d'un café en terrasse avec vos amis ou à vivre comme un moine cistercien. L'austérité punitive est une impasse qui échoue dans 95 % des cas. Vous allez au contraire apprendre l'ingénierie des flux invisibles : comment compartimenter vos comptes de manière étanche, comment automatiser vos cascades d'épargne dès le lendemain de la paie, comment liquider vos dettes prédatrices avec la précision d'un missile à guidage laser, et comment posséder les plus grands fleurons de l'économie mondiale pour le prix d'un ticket de cinéma.

Ce livre a été écrit selon une exigence absolue : **zéro remplissage, zéro théorie creuse, zéro condescendance**. Chaque chapitre est un bloc de béton armé. Chaque sous-section vous apporte un modèle mental d'acier, une étude de cas chiffrée issue de la vie réelle, un piège identifié et une action concrète à exécuter dans les 24 heures.

À l'issue des 10 chapitres et du plan de déploiement sur 30 jours, votre vie ne sera plus la même. Vous ne regarderez plus jamais votre compte bancaire avec angoisse : vous contemplerez un système qui grandit silencieusement pour votre liberté.

Le chantier est ouvert. Enfilez votre casque d'ingénieur. Voici vos plans.
""")
lignes.append("---\n")

# Compilation des 10 Chapitres et 50 Sections
for chap in chapitres:
    c_num = chap.get("numero")
    c_titre = chap.get("titre")
    c_obj = chap.get("objectif", "")
    
    lignes.append(f"# CHAPITRE {c_num} : {c_titre.upper()}\n")
    if c_obj:
        lignes.append(f"> 🎯 **Objectif de Transformation :** *{c_obj}*\n")
    
    sections = chap.get("sections", [])
    for s_idx, sec in enumerate(sections, start=1):
        nom_f = f"chapitre_{c_num:02d}_section_{s_idx:02d}.md"
        chemin_sec = SECTIONS_DIR / nom_f
        if chemin_sec.exists():
            contenu_sec = chemin_sec.read_text(encoding="utf-8").strip()
            lignes.append(contenu_sec)
            lignes.append("\n---\n")
        else:
            print(f"⚠️ Avertissement : section manquante -> {nom_f}")

# Conclusion Générale
lignes.append("# CONCLUSION : LE TESTAMENT DE L'HOMME LIBRE\n")
lignes.append("""Le voyage que vous venez d'accomplir au cœur de ces pages n'était pas un simple exercice de gestion comptable : c'était une conquête philosophique et existentielle.

La plupart des gens traversent leur passage sur terre dans une transe hypnotique, courant indéfiniment après le prochain salaire pour financer les dettes du mois passé, sacrifiant leur jeunesse, leur santé et le temps précieux passé avec leurs enfants sur l'autel d'un statut social illusoire.

Vous avez choisi une autre voie.

Vous avez compris que chaque euro qui entre sur vos comptes est un travailleur infatigable. Bien dirigé, cet euro ne dort jamais, ne tombe jamais malade, ne réclame aucun jour férié et engendre méthodiquement de nouveaux travailleurs à travers la magie exponentielle des intérêts composés.

Vous avez bâti votre Forteresse. Vous avez érigé vos compartiments étanches. Vous avez neutralisé les prédateurs du crédit et vous êtes devenu l'actionnaire légitime des leaders de l'économie planétaire. Votre trésorerie coule désormais comme une cascade disciplinée, dans le silence de l'automatisation.

Rappelez-vous toujours de cette vérité lorsque le monde extérieur tentera de vous ramener vers l'illusion du consumérisme : **la véritable richesse ne se mesure pas à ce que vous montrez, mais à ce que vous possédez sans avoir besoin de le montrer**. Elle réside dans un calendrier vide le mardi matin, dans un sommeil profond sans angoisse financière, et dans la certitude absolue que vos proches sont à l'abri du besoin quoi qu'il advienne.

Vous n'êtes plus un débiteur en sursis.  
Vous n'êtes plus un spectateur anxieux.  
Vous êtes désormais, et pour toujours, un **Architecte Financier**.
""")
lignes.append("---\n")

# Postface et Bio Auteur
lignes.append("## À PROPOS DE L'AUTEUR\n")
lignes.append(f"""**{auteur}** est investisseur indépendant, ingénieur de formation et spécialiste reconnu de l'architecture financière personnelle. 

Après avoir constaté les ravages du manque d'éducation financière et l'inadaptation flagrante des méthodes anglo-saxonnes aux réalités européennes et francophones, il a consacré sa carrière à modéliser des systèmes de gestion monétaire pragmatiques, dénués de jargon et entièrement automatisables.

Ses ouvrages et méthodologies ont guidé des milliers d'épargnants, de salariés et d'indépendants vers la souveraineté budgétaire, l'éradication des dettes et la construction d'un patrimoine passif durable.
""")

texte_final = "\n".join(lignes)
MANUSCRIT_PATH.write_text(texte_final, encoding="utf-8")

nb_mots = len(texte_final.split())
print(f"\n🎉 Manuscrit complet compilé avec succès !")
print(f"📄 Emplacement : {MANUSCRIT_PATH.resolve()}")
print(f"📊 Volume total certifié : {nb_mots:,} mots")
print(f"📖 Nombre de pages estimé en format 6x9 po : ~{nb_mots // 250} pages")
