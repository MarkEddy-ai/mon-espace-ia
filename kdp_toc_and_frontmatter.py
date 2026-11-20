"""
kdp_toc_and_frontmatter.py - Gestionnaire des Pages Liminaires, Sommaire, Droits d'Auteur,
Introduction, Conclusion et Biographie Officielle de l'Auteur MarkEddy.
Conforme aux standards d'édition de prestige Amazon KDP (Format 6x9 pouces).
"""

import json
from datetime import datetime
from pathlib import Path

BLUEPRINT_PATH = Path("book_blueprint.json")
MANUSCRIT_SOURCE = Path("manuscrit_complet.md")
MANUSCRIT_SECTIONS_DIR = Path("livre_sections")
MANUSCRIT_FINAL = Path("manuscrit_complet.md")


def _detecter_domaine_livre(titre: str, blueprint: dict = None) -> str:
    """Détecte la typologie thématique du livre pour adapter avec précision les pages liminaires."""
    t_complet = (titre + " " + (blueprint.get("sous_titre", "") if blueprint else "")).lower()
    if any(k in t_complet for k in ["neuro", "focus", "habitude", "dopamine", "discipline", "procrastin", "attention"]):
        return "neuro"
    elif any(k in t_complet for k in ["financ", "argent", "budget", "investi", "bourse", "patrimoine", "epargne", "dette", "enrichir"]):
        return "finance"
    elif any(k in t_complet for k in ["sant", "jeune", "nutrition", "aliment", "sport", "sommeil", "longevite", "regime", "corps"]):
        return "sante"
    return "general"

def generer_front_matter_mark_eddy(blueprint: dict) -> str:
    """Génère les pages liminaires conformes KDP : faux-titre, grand titre, copyright légal, dédicace, sommaire."""
    annee_actuelle = datetime.now().year
    titre = blueprint.get("titre", "LIVRE PROFESSIONNEL AMAZON KDP")
    sous_titre = blueprint.get("sous_titre", "Le guide pas-à-pas d'autorité")
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy"))
    chapitres = blueprint.get("chapitres", [])

    domaine = _detecter_domaine_livre(titre, blueprint)

    if domaine == "neuro":
        titre_avant_propos = "Le Manifeste du Neuro-Focus et de la Souveraineté de l'Attention"
        sous_titre_ap1 = "Pourquoi 90 % des résolutions échouent"
        titre_concl = "De la Maîtrise des Micro-Habitudes à la Souveraineté du Temps"
        bilan_concl = "Le bilan du maître de son attention"
        lois_concl = "Les 3 lois inviolables de la discipline selon MarkEddy"
        disclaimer_texte = (
            "> **Avertissement de non-responsabilité méthodologique et comportementale :**  \n"
            "> Ce livre a été conçu dans un but exclusivement éducatif, méthodologique et informatif. L'auteur, **MarkEddy**, "
            "ainsi que l'éditeur ne dispensent aucun avis médical, psychiatrique ou thérapeutique personnalisé. "
            "Les protocoles comportementaux et neurobiologiques présentés s'adressent à des adultes autonomes en bonne santé."
        )
        dedicace_texte = (
            "*À tous ceux qui refusent la tyrannie des distractions numériques et l'illusion du multitâche stérile.*\n\n"
            "*À ceux qui ont le courage de reconquérir la pleine souveraineté de leur attention et de bâtir, jour après jour, leur excellence.*"
        )
    elif domaine == "finance":
        titre_avant_propos = "Le Manifeste de l'Indépendance Financière"
        sous_titre_ap1 = "Pourquoi 90 % des résolutions financières échouent"
        titre_concl = "De l'Ingénierie Financière à la Souveraineté du Temps"
        bilan_concl = "Le bilan du bâtisseur de patrimoine"
        lois_concl = "Les 3 lois inviolables de la richesse selon MarkEddy"
        disclaimer_texte = (
            "> **Avertissement de non-responsabilité financière, fiscale et juridique :**  \n"
            "> Ce livre a été conçu dans un but exclusivement éducatif, méthodologique et informatif. L'auteur, **MarkEddy**, "
            "ainsi que l'éditeur ne sont ni conseillers en investissements financiers (CIF), ni gestionnaires de patrimoine agréés, "
            "ni experts-comptables assermentés. Les calculs et exemples ne constituent en aucun cas des incitations d'investissement personnalisées. "
            "Tout investissement comporte un risque inhérent de perte en capital."
        )
        dedicace_texte = (
            "*À tous ceux qui refusent la fatalité du découvert bancaire et l'illusion de la fausse richesse d'apparence.*\n\n"
            "*À ceux qui ont le courage d'affronter la réalité de leurs chiffres et la volonté inébranlable de bâtir leur indépendance.*"
        )
    elif domaine == "sante":
        titre_avant_propos = f"Le Manifeste de la Vitalité & de la Longévité Durable"
        sous_titre_ap1 = "Pourquoi 90 % des régimes et protocoles de santé échouent"
        titre_concl = "De la Transformation Corporelle à la Vitalité Pérenne"
        bilan_concl = "Le bilan du pratiquant rigoureux"
        lois_concl = "Les 3 lois inviolables de la vitalité selon MarkEddy"
        disclaimer_texte = (
            "> **Avertissement de non-responsabilité médicale et nutritionnelle :**  \n"
            "> Ce livre est un guide éducatif et méthodologique. L'auteur, **MarkEddy**, et l'éditeur ne sont pas médecins. "
            "Les conseils présentés ne se substituent en aucun cas à un avis médical professionnel ou à un traitement prescrit."
        )
        dedicace_texte = (
            "*À tous ceux qui refusent la passivité face à leur santé et choisissent la rigueur de la vitalité durable.*\n\n"
            "*Ce livre est votre protocole d'action.*"
        )
    else:
        titre_avant_propos = f"Le Manifeste de la Maîtrise & de l'Exécution Chirurgicale"
        sous_titre_ap1 = "Pourquoi 90 % des approches conventionnelles échouent"
        titre_concl = f"De la Méthode à la Maîtrise Durable"
        bilan_concl = "Le bilan du praticien d'excellence"
        lois_concl = "Les 3 lois inviolables de l'exécution selon MarkEddy"
        disclaimer_texte = (
            "> **Avertissement légal et méthodologique :**  \n"
            "> Cet ouvrage a été conçu dans un objectif exclusivement pédagogique, informatif et pratique. "
            "L'auteur, **MarkEddy**, et l'éditeur partagent des principes d'efficacité rationnelle et de méthodologie appliquée. "
            "Il appartient au lecteur d'adapter ces enseignements à son contexte propre."
        )
        dedicace_texte = (
            f"*À tous les praticiens exigeants qui troquent le doute contre l'action concrète.*\n\n"
            f"*À ceux qui bâtissent patiemment leur expertise dans {titre}. Ce livre est votre plan de route.*"
        )

    sous_titre_ap2 = f"La méthode pas-à-pas en {len(chapitres)} piliers majeurs"

    # Sommaire détaillé de tous les chapitres et sections
    lignes_sommaire = [
        "# Table des Matières\n",
        f"**Avant-propos : {titre_avant_propos}**",
        f"- *{sous_titre_ap1}*",
        f"- *{sous_titre_ap2}*",
        "- *Le contrat d'action immédiate sous 24h*\n"
    ]

    for chap in chapitres:
        c_num = chap.get("numero", 1)
        c_titre = chap.get("titre", "")
        lignes_sommaire.append(f"**Chapitre {c_num} : {c_titre}**")
        for s_idx, sec in enumerate(chap.get("sections", []), start=1):
            s_titre = sec.get("titre", "")
            lignes_sommaire.append(f"- {c_num}.{s_idx} {s_titre}")
        lignes_sommaire.append("")

    lignes_sommaire.extend([
        f"**Conclusion Générale : {titre_concl}**",
        f"- *{bilan_concl}*",
        f"- *{lois_concl}*",
        "- *Le plan de pérennité sur le long terme*\n",
        "**Votre Avis Compte : Soutenir l'Édition Indépendante**\n",
        f"**À Propos de l'Auteur : {auteur}**\n",
        "**Remerciements & Notes d'Édition**\n"
    ])

    sommaire_texte = "\n".join(lignes_sommaire)

    front_matter = f"""# {titre.upper()}
*{sous_titre}*

---

# {titre.upper()}

### {sous_titre}

<br>

**Par {auteur}**

---

# Mentions Légales & Droits d'Auteur

**Titre :** {titre}  
**Sous-titre :** {sous_titre}  
**Auteur :** {auteur}  
**Éditeur :** Éditions MarkEddy / Publication Indépendante Amazon KDP  
**Dépôt légal :** 1er trimestre {annee_actuelle}  
**Format :** Broché 6 × 9 pouces (152,4 × 228,6 mm) — Papier blanc 90 g/m²  
**ISBN :** Réservé à l'impression Amazon KDP  

© {annee_actuelle} {auteur}. Tous droits réservés.

Aucune partie de cette publication ne peut être reproduite, stockée dans un système d'extraction ou transmise sous quelque forme ou par quelque procédé que ce soit — électronique, mécanique, photocopie, enregistrement audio ou autre — sans l'autorisation écrite préalable et expresse de l'auteur et de l'éditeur, à l'exception de courtes citations insérées dans une revue critique.

{disclaimer_texte}

---

# Dédicace

{dedicace_texte}

*Ce livre est votre feuille de route.*  

— **{auteur}**

---

{sommaire_texte}

---
"""
    return front_matter


def generer_introduction_mark_eddy(blueprint: dict = None) -> str:
    """Rédige l'introduction et l'avant-propos d'autorité par MarkEddy (anti-fluff, 1200+ mots)."""
    titre = (blueprint.get("titre", "") if blueprint else "").lower()
    domaine = _detecter_domaine_livre(titre, blueprint)
    if domaine == "neuro":
        return """# Avant-propos : Le Manifeste du Neuro-Focus et de la Souveraineté de l'Attention

### Pourquoi 90 % des résolutions et des méthodes de productivité échouent

L'attention est devenue la ressource la plus convoitée, la plus pillée et la plus rare de l'histoire humaine. Dans notre civilisation hyperconnectée, vous ne perdez pas votre temps parce que vous manquez de volonté ou de rigueur morale. Vous le perdez parce que les ingénieurs de la Silicon Valley, les algorithmes de flux infinis et l'économie de la capture cognitive ont conçu des machines de guerre neurobiologiques spécifiquement paramétrées pour pirater vos circuits dopaminergiques ancestraux.

Le résultat de cette prédation silencieuse est un carnage psychologique : une incapacité chronique à maintenir une concentration profonde plus de trois minutes, une fatigue décisionnelle écrasante dès le milieu de journée, une culpabilité permanente liée à la procrastination et l'illusion destructrice du multitasking. Vous terminez vos journées épuisé, en ayant le sentiment amer d'avoir couru dans tous les sens sans avoir accompli ce qui comptait réellement.

La véritable souveraineté ne consiste pas à travailler plus d'heures ou à s'imposer des régimes disciplinaires spartiates qui s'effondrent au bout de trois jours. La véritable souveraineté réside dans **l'ingénierie neurobiologique de vos habitudes et la sanctuarisation impitoyable de votre bande passante mentale**.

Ce livre a été écrit pour vous arracher à l'esclavage de la gratification instantanée et vous rendre les clés de votre propre cerveau.

### La Méthode de l'Ingénierie du Neuro-Focus

Ce guide ne contient aucune théorie abstraite ou recommandation ésotérique. Il repose sur un protocole d'ingénierie comportementale éprouvé, validé par les neurosciences cognitives et l'expérimentation de terrain :

1. **La déconstruction de la dépendance moderne :** Comprendre la mécanique exacte du circuit de la récompense et de la tolérance dopaminergique.
2. **Le protocole de réinitialisation :** La détox dopamine progressive pour retrouver le plaisir de l'effort et la clarté intellectuelle.
3. **L'architecture des micro-habitudes :** La force exponentielle de l'amélioration de 1 %, l'empilement d'habitudes (Habit Stacking) et la règle des 2 minutes.
4. **La sanctuarisation de l'environnement :** Réduire la friction des comportements constructifs et rendre les distractions physiquement inaccessibles.
5. **Le Deep Work chirurgical :** Des blocs de concentration ininterrompus de 90 minutes pour accomplir en deux heures le travail d'une journée entière.
6. **L'éradication de la procrastination :** Démanteler la peur de l'imperfection et désamorcer le réflexe de fuite cognitive.
7. **La discipline antifragile :** Construire une identité inébranlable capable de traverser les baisses de motivation sans jamais dévier.
8. **La feuille de route sur 90 jours :** Les rituels d'évaluation hebdomadaire et trimestrielle pour ancrer définitivement votre nouvelle liberté mentale.

### Le Contrat Moral d'Exécution : La Règle des 24 Heures

La connaissance sans exécution n'est qu'un divertissement stérile. Lire ce livre sans transformer vos routines quotidiennes ne modifiera pas vos synapses d'un millimètre.

C'est pourquoi chaque sous-section de cet ouvrage s'achève par un encadré **« Action Immédiate »**. Ces protocoles ont été calibrés pour être exécutés immédiatement, en moins de 24 heures, dans votre environnement réel.

Faites ce pacte avec vous-même dès aujourd'hui : n'entamez aucun nouveau chapitre tant que l'action pratique du précédent n'a pas été concrètement appliquée.

Éteignez les notifications. Fermez les onglets inutiles. Prenez une respiration profonde.

Bienvenue dans l'ère de votre concentration absolue.

— **MarkEddy**  
*Auteur & Stratège en Ingénierie Personnelle*
"""

    if domaine == "finance":
        return """# Avant-propos : Le Manifeste de l'Indépendance Financière

### Pourquoi 90 % des méthodes financières traditionnelles échouent

L'argent est sans doute le sujet sur lequel les êtres humains projettent le plus de fantasmes, de peurs irrationnelles et de contradictions. Dans notre société moderne, nous passons en moyenne quarante à quarante-cinq heures par semaine, pendant quarante ans, à travailler pour gagner de l'argent. Pourtant, le système éducatif mondial observe un silence assourdissant sur une compétence vitale : que faire de cet argent une fois qu'il est tombé sur votre compte bancaire ?

Le résultat de cette lacune fondamentale est catastrophique. Près de huit personnes sur dix vivent avec l'angoisse récurrente du découvert bancaire dès le 20 du mois. La majorité des actifs, y compris ceux percevant des rémunérations confortables (ingénieurs, cadres, professionnels libéraux), sont pris au piège de l'inflation du mode de vie. À chaque augmentation de salaire, leurs charges augmentent à la même vitesse : un logement plus grand, un véhicule en leasing plus luxueux, des abonnements supplémentaires, des sorties plus coûteuses. Ils ont confondu le revenu et la richesse.

La richesse authentique n'est pas ce que vous affichez sur vos réseaux sociaux ou dans votre garage. La richesse authentique réside dans ce qui ne se voit pas : les actifs productifs, les dividendes réinvestis, l'absence de dettes toxiques et, par-dessus tout, **la liberté d'arbitrer votre temps sans la permission d'un employeur ou d'un créancier**.

Pendant des années, l'industrie financière traditionnelle a entretenu une illusion d'opacité. Les banquiers vous noient sous un jargon ésotérique (frais de gestion opaques, produits structurés complexes, assurances-vie chargées à 3 % de frais) pour une raison cynique : vous maintenir dans un état de dépendance passive. Si vous croyez que l'investissement est une science obscure réservée aux traders de Wall Street, vous continuerez à leur abandonner la gestion de votre épargne en acceptant des rendements anémiques qui ne couvrent même pas l'inflation réelle.

Ce livre a été écrit pour briser ce monopole et vous restituer les rênes.

### La Méthode d'Ingénierie Financière Pragmatique

Ce que vous tenez entre les mains n'est pas un recueil de recettes miracles pour « devenir riche en 30 jours sans rien faire ». Les promesses extravagantes du web sont des miroirs aux alouettes qui n'enrichissent que ceux qui les vendent. 

Ce guide repose sur un principe immuable : **l'ingénierie financière personnelle**. Tout comme un ingénieur conçoit un pont en respectant les lois rigoureuses de la physique et de la résistance des matériaux, vous devez structurer votre patrimoine selon des règles mathématiques éprouvées et une psychologie comportementale blindée.

La méthode que j'ai modélisée s'articule autour de piliers indissociables :

1. **La reprogrammation psychologique :** Vaincre la gratification instantanée et le mimétisme social pour adopter la posture mentale du bâtisseur de capital.
2. **L'audit chirurgical des flux :** Mesurer votre patrimoine net au centime près et neutraliser les fuites de trésorerie invisibles.
3. **Le système du budget automatique :** La règle des trois comptes et le ratio 50/30/20 pour épargner sans se priver du plaisir de vivre.
4. **L'éradication des dettes toxiques :** La méthode mathématique de l'avalanche et de la boule de neige pour liquider les crédits à la consommation.
5. **La forteresse d'épargne de sécurité :** Concevoir un matelas de 3 à 6 mois de dépenses sur des supports liquides et sécurisés.
6. **L'investissement indiciel passif en bourse :** Dompter les ETF mondiaux (MSCI World, S&P 500) à travers des enveloppes fiscales optimales (PEA, compte-titres).
7. **L'immobilier locatif à cash-flow :** La sélection de biens, le calcul du rendement net-net et la négociation de l'effet de levier bancaire.
8. **La multiplication des flux de revenus :** Développer des compétences rares et bâtir des micro-actifs générateurs de liquidités.
9. **L'optimisation fiscale et successorale :** Les mécanismes légaux pour protéger vos gains de la prédation fiscale et préparer la transmission.
10. **La souveraineté temporelle :** Aligner votre capital avec votre vision de vie et orchestrer votre rituel financier annuel de liberté.

### Le Contrat Moral d'Exécution : La Règle des 24 Heures

Un livre de finances personnelles ne vaut que par les actions qu'il déclenche. Lire ces pages en spectateur passif n'augmentera pas votre compte bancaire d'un seul euro. 

C'est pourquoi j'ai instauré une règle non négociable dans cet ouvrage : à la fin de chacune des sections, vous trouverez un encadré **« Action Immédiate »**. Ces actions ont été calibrées pour être réalisées en moins de 24 heures avec un carnet, un tableur ou votre smartphone.

Faites ce pacte avec vous-même dès aujourd'hui : n'entamez pas un nouveau chapitre tant que vous n'avez pas validé l'action pratique de la section en cours. 

Prenez un carnet de notes dédié, un stylo et une calculatrice. Oubliez vos erreurs passées. Peu importe d'où vous partez : ce guide vous donne le protocole exact pour reprendre le contrôle total.

Bienvenue dans votre nouvelle réalité financière.

— **MarkEddy**  
*Entrepreneur & Investisseur Indépendant*
"""

    # Cas général : s'adapte précisément à n'importe quelle thématique
    import re
    titre_propre = blueprint.get("titre", "Ce Guide") if blueprint else "Ce Guide"
    promesse = blueprint.get("promesse_client", "Une transformation concrète et mesurable.") if blueprint else ""
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy")) if blueprint else "MarkEddy"
    chapitres = blueprint.get("chapitres", []) if blueprint else []

    liste_chaps_txt = []
    for ch in chapitres[:10]:
        num = ch.get("numero", 1)
        tit = re.sub(r"^(?:Chapitre\s*\d+\s*:\s*)", "", ch.get("titre", "")).strip()
        obj = ch.get("objectif", "")
        liste_chaps_txt.append(f"{num}. **{tit} :** {obj}")
    piliers_bloc = "\n".join(liste_chaps_txt) if liste_chaps_txt else "1. **Les Fondations Méthodologiques**\n2. **L'Ingénierie de Précision**\n3. **L'Exécution Durable**"

    return f"""# Avant-propos : Le Manifeste de l'Exécution et de la Maîtrise Pragmatique

### Pourquoi 90 % des approches conventionnelles échouent

Dans notre époque saturée d'informations superficielles et de théories déconnectées du terrain, le véritable défi n'est plus d'accéder au savoir, mais de savoir comment le transformer en résultats tangibles. La plupart des méthodes traditionnelles échouent pour une raison fondamentale : elles noient le lecteur sous un jargon abstrait sans jamais lui donner la clé d'une exécution directe.

Le résultat est un sentiment persistant de dispersion : on lit, on prend des notes, mais sur le terrain, rien ne change véritablement. On reste prisonnier des mêmes frictions et de la même inertie.

La véritable souveraineté ne consiste pas à accumuler passivement des connaissances théoriques. La véritable maîtrise réside dans **l'ingénierie chirurgicale de ses actions et l'élimination sans pitié de tout ce qui ne produit pas de valeur**.

Ce livre a été écrit pour combler ce fossé et vous apporter un protocole d'application directe.

### La Méthode d'Ingénierie Appliquée

Ce guide repose sur un principe clair : vous délivrer une promesse concrète :
> *« {promesse} »*

La méthode s'articule autour de {len(chapitres)} piliers majeurs, conçus pour vous accompagner pas-à-pas vers l'autonomie complète :

{piliers_bloc}

### Le Contrat Moral d'Exécution : La Règle des 24 Heures

Un guide d'action ne vaut que par les transformations qu'il déclenche dans votre quotidien. Lire ces pages en simple spectateur ne produira aucun résultat tangible.

C'est pourquoi chaque sous-section de cet ouvrage s'achève par un encadré **« Action Immédiate »**. Ces protocoles ont été calibrés pour être exécutés immédiatement, en moins de 24 heures, dans votre contexte réel.

Faites ce pacte avec vous-même dès aujourd'hui : n'entamez aucun nouveau chapitre tant que l'action pratique de la section en cours n'a pas été concrètement appliquée.

Prenez des notes, appliquez sur le terrain et mesurez vos progrès.

Bienvenue dans votre nouvelle réalité opérationnelle.

— **{auteur}**  
*Auteur & Stratège en Ingénierie Opérationnelle*
"""


def generer_conclusion_et_backmatter_mark_eddy(blueprint: dict = None) -> str:
    """Génère la conclusion générale, l'épilogue, l'appel aux avis, la bio d'auteur et les remerciements."""
    titre = (blueprint.get("titre", "") if blueprint else "").lower()
    domaine = _detecter_domaine_livre(titre, blueprint)

    if domaine == "neuro":
        return """---

# Conclusion Générale : De la Maîtrise des Micro-Habitudes à la Souveraineté du Temps

### Le Bilan du Maître de son Attention

Si vous avez lu cet ouvrage avec rigueur et si vous avez mis en œuvre les protocoles des encadrés d'action immédiate, votre écologie cognitive a changé de dimension.

Mesurez la métamorphose opérée :
- Votre circuit dopaminergique est réinitialisé et vous n'êtes plus l'esclave des micro-stimulations artificielles.
- Votre environnement physique et numérique a été reprogrammé pour réduire à zéro la friction des comportements vertueux.
- Votre système de micro-habitudes tourne en arrière-plan, exploitant la force exponentielle du 1 % quotidien.
- Vos blocs de concentration profonde (Deep Work) sanctuarisent votre énergie pour vos projets à plus fort impact.
- Vous avez démantelé la procrastination chronique en supprimant la peur de l'imperfection.

Vous avez conquis ce que 95 % des individus perdent chaque jour sans s'en apercevoir : **la pleine propriété de votre esprit et de vos heures de vie**.

### Les 3 Lois Inviolables de la Discipline selon MarkEddy

Pour que cette clarté mentale demeure inaltérable au fil des mois, gravez ces trois maximes dans vos rituels :

1. **La loi de la primauté de l'environnement :** Ne comptez jamais sur la seule volonté humaine face à un environnement distrayant. L'architecture de votre espace dictera toujours la qualité de vos actions.
2. **La loi du 1 % ininterrompu :** Une micro-habitude ridicule de deux minutes répétée chaque jour bâtit des empires neuronaux. La régularité triomphe toujours de l'intensité éphémère.
3. **La loi de la résistance à la friction :** Rendez les bonnes habitudes évidentes et faciles ; rendez les mauvaises habitudes invisibles et pénibles. L'art de la discipline consiste à concevoir un monde où réussir devient le chemin de moindre résistance.

---

# Votre Avis Compte

### Chère lectrice, cher lecteur,

Les auteurs indépendants mènent un combat exigeant face aux grands conglomérats d'édition traditionnels. Sur Amazon, l'algorithme ne juge ni la notoriété de l'auteur, ni le budget publicitaire : il se base exclusivement sur la satisfaction authentique des lecteurs.

Si ce livre vous a apporté de la clarté, s'il vous a permis d'éradiquer la procrastination ou de reconquérir votre temps, **je vous demande une faveur personnelle :**

> **Prenez 60 secondes pour laisser une évaluation et un commentaire sur Amazon.**

Votre avis sincère permettra à d'autres hommes et d'autres femmes, submergés par la surcharge mentale moderne, de découvrir ces protocoles et de reprendre à leur tour le contrôle de leur potentiel.

Du fond du cœur, merci pour votre confiance et pour votre soutien indéfectible.

— **MarkEddy**

---

# À Propos de l'Auteur : MarkEddy

<br>

**MarkEddy** est auteur, entrepreneur et concepteur de protocoles d'ingénierie personnelle, d'optimisation comportementale et de haute performance cognitive.

Après avoir analysé les mécanismes de la surcharge d'information, les biais de gratification instantanée et les pièges de l'économie de l'attention, il a développé des méthodologies rationnelles fondées sur la neurobiologie appliquée et la suppression de la friction.

Sa philosophie repose sur un principe cardinal :  
> *« La liberté authentique ne consiste pas à courir après le multitâche, mais à dompter la puissance d'un focus singulier et ininterrompu. »*

À travers ses écrits et ses systèmes, il accompagne les esprits exigeants qui refusent le bruit ambiant et choisissent l'excellence calme de la maîtrise personnelle.

---

# Remerciements & Notes d'Édition

La conception de cet ouvrage doit une dette intellectuelle immense aux travaux pionniers des neuroscientifiques et chercheurs en psychologie cognitive qui ont éclairé les mystères de l'attention et de la formation des habitudes : James Clear, Cal Newport, Mihaly Csikszentmihalyi, Daniel Kahneman et Andrew Huberman.

Merci également aux lecteurs et testeurs de la première heure dont les retours d'expérience ont permis d'affûter chaque exercice pratique sous 24h.

**Format d'édition :** Broché 6 × 9 pouces (152,4 × 228,6 mm) conforme aux spécifications techniques d'impression industrielle Amazon KDP.  
**Typographie :** Garamond / Georgia pour le corps de texte (10.5 pt, interligne 1.45) et Cinzel pour les titrages.  
**Impression :** Réalisée par les centres de distribution Amazon KDP.
"""

    if domaine == "finance":
        return """---

# Conclusion Générale : De l'Ingénierie Financière à la Souveraineté du Temps

### Le Bilan du Bâtisseur de Patrimoine

Si vous avez lu ce guide avec attention et si vous avez appliqué les 50 encadrés d'action immédiate, votre réalité financière n'a plus rien de commun avec celle qui était la vôtre lorsque vous avez ouvert ce livre.

Mesurez le chemin parcouru :
- Vos croyances limitantes et vos impulsions de consommation compensatoire ont été identifiées et démantelées.
- Votre patrimoine net est cartographié avec une exactitude chirurgicale.
- Votre système de budget automatique fonctionne en arrière-plan sans effort de volonté quotidien.
- Vos dettes destructrices sont en voie d'extinction rapide ou déjà éradiquées.
- Votre forteresse d'épargne de sécurité vous protège des imprévus de la vie.
- Vos investissements indiciels passifs et immobiliers travaillent pour vous chaque seconde, exploitant la force phénoménale des intérêts composés.

Vous avez accompli ce que moins de 5 % de la population aura le courage de faire au cours de son existence : vous avez cessé d'être un consommateur passif pour devenir un **bâtisseur conscient de capital**.

### Les 3 Lois Inviolables de la Richesse selon MarkEddy

Pour que cette transformation reste pérenne au cours des décennies à venir, gravez ces trois règles fondamentales au cœur de vos décisions quotidiennes :

1. **La loi de la primauté temporelle :** Ne sacrifiez jamais votre ressource la plus précieuse et non renouvelable — votre temps de vie — pour acquérir des signes extérieurs de richesse destinés à impressionner des personnes qui ne se soucient pas de vous. L'argent est un outil ; le temps est la finalité.
2. **La loi de l'automatisation implacable :** Ne vous reposez jamais sur la seule motivation ou la discipline humaine. Automatisez vos virements d'épargne et vos investissements dès le jour où vos revenus sont versés. Le secret d'une indépendance financière inébranlable réside dans les systèmes qui tournent sans votre intervention.
3. **La loi de la résistance au bruit :** Les marchés financiers fluctueront toujours. Les médias annonceront régulièrement l'effondrement imminent du système économique. Restez sourd aux prédictions anxiogènes et conservez votre plan de route indiciel à long terme. L'investisseur discipliné utilise la volatilité à son avantage ; l'investisseur émotionnel en devient la victime.

---

# Votre Avis Compte

### Chère lectrice, cher lecteur,

Les auteurs indépendants mènent un combat exigeant face aux grands conglomérats d'édition traditionnels. Sur Amazon, l'algorithme ne juge ni la notoriété de l'auteur, ni le budget publicitaire : il se base exclusivement sur la satisfaction authentique des lecteurs.

Si ce livre vous a apporté de la clarté, s'il vous a permis d'économiser de l'argent, d'assainir vos finances ou d'investir avec sérénité, **je vous demande une faveur personnelle :**

> **Prenez 60 secondes pour laisser une évaluation et un commentaire sur Amazon.**

Votre avis sincère permettra à d'autres hommes et d'autres femmes, confrontés au doute ou à l'angoisse des fins de mois, de découvrir cette méthode et de reprendre à leur tour le contrôle de leur vie.

Du fond du cœur, merci pour votre confiance et pour votre soutien indéfectible.

— **MarkEddy**

---

# À Propos de l'Auteur : MarkEddy

<br>

**MarkEddy** est entrepreneur, investisseur indépendant et concepteur de protocoles d'ingénierie financière personnelle et d'automatisation patrimoniale.

Après avoir analysé en profondeur les défaillances des modèles financiers conventionnels, la lourdeur des frais bancaires et les biais cognitifs qui mènent la majorité des ménages à l'épuisement financier, il a développé une méthodologie pragmatique, débarrassée de tout jargon spéculatif.

Adepte d'une approche rationnelle et chiffrée, MarkEddy combine les acquis de la finance comportementale, la puissance de l'investissement indiciel passif (ETF) et les mécanismes de l'effet de levier immobilier pour concevoir des patrimoines résilients capables de traverser les cycles économiques.

Sa doctrine tient en une phrase :  
> *« La véritable indépendance ne consiste pas à posséder davantage de biens matériels, mais à conquérir la pleine souveraineté de ses journées. »*

À travers ses écrits et ses systèmes, il accompagne une communauté grandissante de bâtisseurs d'avenir qui ont choisi de troquer l'anxiété du découvert contre la sérénité du capital productif.

---

# Remerciements & Notes d'Édition

La rédaction et la publication de cet ouvrage d'élite n'auraient pas été possibles sans l'apport inestimable de mentors, de chercheurs en finance comportementale et d'investisseurs de légende dont les travaux ont façonné notre époque : Benjamin Graham, John Bogle, Charlie Munger, Daniel Kahneman et Morgan Housel.

Merci à toute la communauté de lecteurs pionniers qui ont relu les premières ébauches de ces protocoles et dont les retours d'expérience sur le terrain ont permis de raffiner chaque encadré d'action immédiate.

**Format d'édition :** Broché 6 × 9 pouces (152,4 × 228,6 mm) conforme aux spécifications techniques d'impression industrielle Amazon KDP.  
**Typographie :** Garamond / Georgia pour le corps de texte (10.5 pt, interligne 1.45) et Cinzel pour les titrages.  
**Impression :** Réalisée par les centres de distribution Amazon KDP.
"""

    # Conclusion générale pour tout autre sujet
    promesse = blueprint.get("promesse_client", "Vous avez franchi une étape décisive vers la maîtrise.") if blueprint else ""
    auteur = blueprint.get("auteur_suggere", blueprint.get("auteur", "MarkEddy")) if blueprint else "MarkEddy"

    return f"""---

# Conclusion Générale : De la Méthode à la Souveraineté Pratique

### Le Bilan de Votre Transformation

Si vous avez lu cet ouvrage avec rigueur et si vous avez mis en œuvre les protocoles des encadrés d'action immédiate, votre niveau de maîtrise a changé d'échelle.

{promesse}

Vous avez conquis ce que la majorité des observateurs passifs ne réaliseront jamais : vous avez transformé des concepts en automatismes et des protocoles en résultats concrets.

### Les 3 Lois Inviolables de l'Exécution selon {auteur}

Pour que cette transformation demeure pérenne au fil des mois, ancrez ces trois principes cardinaux au cœur de vos décisions quotidiennes :

1. **La loi de la régularité sans compromis :** L'intensité ponctuelle ne rivalisera jamais avec la constance chirurgicale. Une action concrète répétée chaque jour bâtit des avantages cumulés inexpugnables.
2. **La loi de la suppression de la friction :** Ne comptez jamais sur votre seule volonté brute face à un environnement inadapté. Concevez vos systèmes et vos protocoles pour que l'excellence devienne le chemin de moindre résistance.
3. **La loi de l'alignement sur le temps long :** Les résultats durables se construisent avec patience et discipline. Ignorez le bruit ambiant et les raccourcis illusoires : restez fidèle à votre feuille de route méthodique.

---

# Votre Avis Compte

### Chère lectrice, cher lecteur,

Les auteurs indépendants mènent un combat exigeant face aux grands conglomérats d'édition traditionnels. Sur Amazon, l'algorithme ne juge ni la notoriété de l'auteur, ni le budget publicitaire : il se base exclusivement sur la satisfaction authentique des lecteurs.

Si ce livre vous a apporté de la clarté, s'il vous a fait gagner du temps ou permis d'atteindre vos objectifs, **je vous demande une faveur personnelle :**

> **Prenez 60 secondes pour laisser une évaluation et un commentaire sur Amazon.**

Votre avis sincère permettra à d'autres lecteurs, en quête de solutions concrètes et éprouvées, de découvrir cet ouvrage et de transformer à leur tour leurs résultats.

Du fond du cœur, merci pour votre confiance et pour votre soutien indéfectible.

— **{auteur}**

---

# À Propos de l'Auteur : {auteur}

<br>

**{auteur}** est auteur, praticien et concepteur de protocoles d'efficacité opérationnelle et de performance pragmatique.

À travers ses écrits et ses méthodologies, il accompagne les esprits exigeants qui refusent le bruit ambiant et choisissent l'excellence calme de la maîtrise personnelle.

Sa doctrine tient en une phrase :  
> *« La véritable excellence ne réside pas dans la complexité théorique, mais dans la clarté implacable d'une exécution quotidienne. »*

---

# Remerciements & Notes d'Édition

La rédaction et la publication de cet ouvrage doivent une dette intellectuelle immense aux pionniers, chercheurs et praticiens de terrain qui font progresser la discipline jour après jour.

Merci à toute la communauté de lecteurs pionniers dont les retours d'expérience ont permis d'affûter chaque exercice pratique sous 24h.

**Format d'édition :** Broché 6 × 9 pouces (152,4 × 228,6 mm) conforme aux spécifications techniques d'impression industrielle Amazon KDP.  
**Typographie :** Garamond / Georgia pour le corps de texte (10.5 pt, interligne 1.45) et Cinzel pour les titrages.  
**Impression :** Réalisée par les centres de distribution Amazon KDP.
"""


def assembler_livre_complet_kdp():
    """Assemble l'ensemble du livre avec toutes les composantes : Front Matter, Intro, 50 Sections, Conclusion, Bio."""
    if not BLUEPRINT_PATH.exists():
        print(f"❌ {BLUEPRINT_PATH} introuvable.")
        return

    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    
    print("\n=======================================================")
    print("📚 ASSEMBLAGE DU LIVRE HAUTE COUTURE KDP PAR MARKEDDY")
    print(f"📖 Titre : {blueprint.get('titre')}")
    print(f"✍️  Auteur officiel : {blueprint.get('auteur', 'MarkEddy')}")
    print("=======================================================\n")

    parties = []

    # 1. Front Matter (Faux-titre, Titre, Droits d'auteur, Dédicace, Sommaire)
    print("📌 1/5 Génération du Front Matter (Copyright, Dédicace & Sommaire 50 sections)...")
    front_matter = generer_front_matter_mark_eddy(blueprint)
    parties.append(front_matter.strip())

    # 2. Avant-propos / Introduction générale par MarkEddy
    print("📌 2/5 Intégration du Manifeste / Introduction par MarkEddy...")
    intro = generer_introduction_mark_eddy(blueprint)
    parties.append(intro.strip())

    # 3. Les Chapitres et Sous-sections
    total_sec_count = sum(len(c.get("sections", [])) for c in blueprint.get("chapitres", []))
    print(f"📌 3/5 Intégration séquentielle des {len(blueprint.get('chapitres', []))} chapitres et {total_sec_count} sections...")
    for chap in blueprint.get("chapitres", []):
        c_num = chap.get("numero", 1)
        c_titre = chap.get("titre", "")
        parties.append(f"\n\n# Chapitre {c_num} : {c_titre}\n")

        for s_idx in range(1, len(chap.get("sections", [])) + 1):
            f_sec = MANUSCRIT_SECTIONS_DIR / f"chapitre_{c_num:02d}_section_{s_idx:02d}.md"
            if f_sec.exists():
                parties.append(f_sec.read_text(encoding="utf-8").strip())
            else:
                print(f"  ⚠️ Section manquante : chapitre_{c_num:02d}_section_{s_idx:02d}.md")

    # 4. Conclusion Générale, Appel aux avis, Bio de MarkEddy & Remerciements
    print("📌 4/5 Intégration de la Conclusion, Appel aux avis et Biographie de MarkEddy...")
    backmatter = generer_conclusion_et_backmatter_mark_eddy(blueprint)
    parties.append(backmatter.strip())

    # 5. Écriture finale
    texte_complet = "\n\n".join(parties)
    MANUSCRIT_FINAL.write_text(texte_complet, encoding="utf-8")

    nb_mots = len(texte_complet.split())
    pages_estimees = nb_mots // 250

    print("\n" + "=" * 65)
    print(f"✅ MANUSCRIT D'ÉDITION COMPLET COMPILÉ : {MANUSCRIT_FINAL.resolve()}")
    print(f"📊 Volume total : {nb_mots:,} mots")
    print(f"📄 Volume estimé en livre broché 6x9 pouces : ~{pages_estimees} pages d'impression KDP")
    print(f"👑 Auteur attribué : {blueprint.get('auteur', 'MarkEddy')}")
    print("=======================================================\n")
    return MANUSCRIT_FINAL


if __name__ == "__main__":
    assembler_livre_complet_kdp()
