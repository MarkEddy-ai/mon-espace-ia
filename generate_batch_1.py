# -*- coding: utf-8 -*-
"""
generate_batch_1.py - Génération Haute Couture des Chapitres 1 à 3 (Sections 1.1 à 3.5)
L'ARCHITECTE FINANCIER par MarkEddy
"""

import os
from pathlib import Path

OUTPUT_DIR = Path("livre_sections")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SECTIONS_CHAP_1_TO_3 = {
    "chapitre_01_section_01.md": """### 1.1 Le mythe des revenus élevés et la réalité du reste à vivre

La majorité des gens sont persuadés qu'un salaire élevé constitue la clé universelle de la sérénité financière. C'est une illusion d'optique coûteuse. Si la richesse n'était qu'une simple corrélation avec le montant brut figurant sur votre fiche de paie, les cadres supérieurs, médecins spécialistes et consultants parisiens ne passeraient jamais leurs dimanches soirs angoissés devant l'application de leur banque. Dans la réalité de l'économie moderne, votre sécurité financière n'est pas déterminée par ce que vous gagnez chaque mois, mais par la structure mathématique de ce qui reste sur vos comptes après l'impact des charges fixes et des obligations sociales.

Le revenu brut est une vanité ; le revenu net n'est qu'un indicateur de transit ; seul le **Reste à Vivre Disponible Réel (RVDR)** définit votre degré d'indépendance. La plupart des ménages commettent l'erreur de confondre leur niveau de vie apparent avec leur santé bilancielle. Dès que le revenu augmente de 15 %, les mensualités de crédit grimpent de 20 %, le standing du logement est réajusté à la hausse et les sorties s'alignent sur les codes du nouveau cercle relationnel. C'est le piège de la cage dorée : les barreaux sont plus brillants, mais la captivité économique demeure absolue.

#### Étude de Cas Chiffrée : Thomas (4 200 € / mois) vs Sarah (2 100 € / mois)

Pour appréhender ce différentiel de structure, analysons le quotidien financier réel de deux profils trentenaires suivis sur 36 mois :

* **Thomas, 34 ans, directeur de clientèle :** Perçoit **4 200 € net par mois**. Son train de vie comprend un loyer en centre-ville de 1 650 €, un véhicule en LOA à 520 €/mois, des assurances et abonnements premium pour 310 €, des frais de représentation et restaurants pour 1 200 €, et 350 € de remboursements de crédit renouvelable contracté pour un voyage. Il termine chaque mois avec un découvert oscillant entre -200 € et -800 €. Son patrimoine net après 8 ans de carrière est de **-4 200 €**.
* **Sarah, 31 ans, technicienne hospitalière :** Perçoit **2 100 € net par mois**. Elle vit dans un logement périphérique agréable de 720 € de charge mensuelle, roule dans une citadine payée comptant (frais d'entretien mensualisés à 85 €), optimise son alimentation à 350 € et préserve 250 € pour ses sorties. Grâce à son architecture de virements, elle épargne et investit **450 € chaque mois** dès le versement de son traitement. Son patrimoine net après 6 ans s'élève à **38 400 €**.

| Paramètre Financier | Thomas (Cadre) | Sarah (Technicienne) |
| :--- | :--- | :--- |
| **Revenu net perçu** | 4 200 € | 2 100 € |
| **Charges incompressibles** | 2 480 € (59 %) | 1 055 € (50,2 %) |
| **Dépenses de statut & style de vie** | 1 550 € (36,9 %) | 595 € (28,3 %) |
| **Dettes toxiques actives** | 5 400 € à 16,8 % | 0 € |
| **Épargne & investissement mensuel** | 0 € (découvert récurrent) | **450 € (21,4 %)** |
| **Autonomie financière en cas d'arrêt** | **18 jours** | **2,8 années de charges** |

Le constat est sans appel : avec des revenus deux fois moindres, Sarah possède une solidité patrimoniale infiniment supérieure. Thomas vit en sursis permanent ; un retard de salaire d'une semaine suffit à déclencher des rejets de prélèvements et des frais d'intervention bancaires.

#### Le Piège Fréquent & La Parade

> ❌ **Le piège classique :** Croire qu'une augmentation de salaire future réglera vos difficultés actuelles de trésorerie. C'est faux dans 95 % des cas en raison de l'inflation réflexe du mode de vie.  
>  
> ✅ **La contre-mesure de l'Architecte :** Bloquer contractuellement votre niveau de charges fixes. Lors de chaque future augmentation ou rentrée exceptionnelle, appliquez la règle des deux tiers : consacrez 66 % du surplus à l'investissement et seulement 34 % à l'élévation de votre confort quotidien.

---

> ⚡ **Action Immédiate (Moins de 24 Heures) :**
>
> 1. Munissez-vous de votre dernière fiche de paie ou de votre relevé de compte principal.
> 2. Calculez votre **Taux de Reste à Vivre Disponible (TRVD)** selon la formule :
>    $$\text{TRVD} = \frac{\text{Revenu Net Total} - \text{Charges Fixes Incompressibles}}{\text{Revenu Net Total}} \times 100$$
> 3. Si votre TRVD est inférieur à 35 %, votre architecture financière est en zone rouge. Consignez ce pourcentage pour mesurer vos progrès au fil des chapitres.
""",

    "chapitre_01_section_02.md": """### 1.2 La cartographie chirurgicale des flux d'argent sur 90 jours

La plupart des diagnostics budgétaires échouent lamentablement parce qu'ils se basent sur l'analyse d'un seul mois isolé. Or, un mois calendaire ne représente jamais fidèlement la réalité économique d'une vie humaine. Entre les régularisations de charges d'énergie, les primes semestrielles, les cadeaux d'anniversaire, les révisions de véhicule et les trimestres d'assurance, un budget évalué sur 30 jours est condamné à être faussé par les anomalies temporelles. Pour construire un système inébranlable, nous devons adopter la rigueur d'un expert-comptable menant un audit médico-légal sur un trimestre complet : 90 jours consécutifs.

Cette autopsie sur 90 jours permet de lisser les à-coups et de révéler ce que les psychologues appellent les « angles morts financiers ». Lorsque vous interrogez une personne sur ce qu'elle dépense au supermarché ou en cafés, elle sous-estime systématiquement le chiffre réel de 30 % à 50 %. Les souvenirs humains filtrent les micro-transactions ; les relevés bancaires, eux, ne mentent jamais.

#### Protocole d'Extraction et Classification en 4 Compartiments

Téléchargez au format CSV ou PDF les 3 derniers relevés de l'ensemble de vos comptes bancaires et cartes à débit différé. Munissez-vous de 4 surligneurs ou utilisez un tableur en créant 4 colonnes strictes :

1. **Compartiment A - Survie & Obligations Fixes :** Loyer ou mensualité de crédit immobilier, taxes, électricité, eau, box internet, forfaits téléphoniques de base, mutuelle et assurances indispensables.
2. **Compartiment B - Consommation Courante Variable :** Alimentation au supermarché, carburant, passes de transport en commun, produits d'hygiène et d'entretien ménager.
3. **Compartiment C - Plaisir & Vie Sociale :** Restaurants, bars, livraisons de repas à domicile, loisirs, vêtements non indispensables, sorties culturelles, week-ends.
4. **Compartiment D - Friction & Furtivité :** Frais de tenue de compte, agios de découvert, commissions de rejet, abonnements numériques oubliés, achats impulsifs sur smartphone, pourboires automatiques d'applications.

#### Étude de Cas Chiffrée : L'Audit Révélateur de Maxime et Julie (32 et 35 ans)

Maxime et Julie affirmaient « ne pas pouvoir mettre un centime de côté » malgré un revenu de foyer de 3 850 € nets par mois. L'autopsie chirurgicale sur les mois d'octobre, novembre et décembre a produit le bilan suivant :

* **Moyenne mensuelle du Compartiment A (Fixe) :** 1 920 € (conforme à leurs estimations).
* **Moyenne mensuelle du Compartiment B (Courant) :** 780 € (environ 15 % plus élevé que prévu).
* **Moyenne mensuelle du Compartiment C (Plaisir) :** 890 € (estimé par le couple à 400 €).
* **Moyenne mensuelle du Compartiment D (Friction) :** **260 €** de pure déperdition invisible (frais bancaires pour dépassement temporaire : 38 €/mois ; abonnements à 4 plateformes de streaming cumulées et applications inutilisées : 72 €/mois ; 15 livraisons de repas avec frais annexes : 150 €/mois).

| Compartiment | Dépense déclarée | Dépense réelle (90j) | Écart mensuel constaté |
| :--- | :--- | :--- | :--- |
| **A - Fixe** | 1 900 € | 1 920 € | +20 € (+1 %) |
| **B - Courant** | 650 € | 780 € | +130 € (+20 %) |
| **C - Plaisir** | 400 € | 890 € | **+490 € (+122 %)** |
| **D - Friction** | 0 € (ignoré) | 260 € | **+260 € (inconnu)** |
| **Total mensuel** | 2 950 € | 3 850 € | **+900 € de fuite réelle** |

L'exercice a mis en lumière que le couple disposait en vérité d'une capacité d'épargne dormante de près de **900 € par mois**, engloutie dans des frottements et une distorsion cognitive de leurs dépenses de loisir.

#### Le Piège Fréquent & La Parade

> ❌ **Le piège classique :** Tenter de mémoriser ses dépenses au fil de l'eau sur une application mobile. Vous abandonnerez au bout de 9 jours en raison de la fatigue mentale.  
>  
> ✅ **La contre-mesure de l'Architecte :** Pratiquer une analyse rétrospective passive. Laissez les relevés bancaires collecter la donnée sans effort, puis effectuez un audit unique de 45 minutes par trimestre pour calibrer vos tuyaux.

---

> ⚡ **Action Immédiate (Moins de 24 Heures) :**
>
> 1. Connectez-vous à votre espace bancaire et exportez les relevés des 3 derniers mois au format PDF ou CSV.
> 2. Isolez la ligne totale des débits de chaque mois et calculez la moyenne arithmétique :
>    $$\text{Dépense Moyenne Mensuelle} = \frac{\text{Total M1} + \text{Total M2} + \text{Total M3}}{3}$$
> 3. Notez ce chiffre sur la première page de votre carnet de bord financier. C'est votre coût réel d'existence.
""",

    "chapitre_01_section_03.md": """### 1.3 Identifier et colmater les 7 micro-fuites invisibles

L'analogie maritime est ici d'une rigueur absolue : un navire coule rarement à cause d'une brèche gigantesque et visible à l'œil nu ; il sombre le plus souvent à cause de micro-fissures sous la ligne de flottaison que personne ne prend la peine d'inspecter. Dans votre budget, ces micro-fissures s'appellent les **micro-fuites récurrentes**. Prises isolément, elles semblent ridicules : 4,99 € ici pour un stockage cloud souscrit il y a deux ans, 12,99 € là pour une salle de sport où vous ne mettez plus les pieds depuis l'hiver dernier, ou 8,50 € de frais de tenue de compte prélevés dans l'indifférence générale.

Cependant, la loi mathématique de la récurrence transforme ces sommes minuscules en hémorragies de capital considérables. Une dépense silencieuse de 10 € par jour représente 3 650 € par an. Si vous placez cette somme pendant 15 ans à un taux d'intérêt moyen conservateur de 7 %, ce montant ne représente pas 54 750 €, mais **91 720 €** envolés en fumée en raison de la perte des intérêts composés.

#### Le Catalogue des 7 Micro-Fuites Toxiques

1. **Les abonnements fantômes à tacite reconduction :** Services de streaming vidéo ou musical en double, applications d'entraînement, journaux numériques non lus.
2. **Les frais bancaires d'un autre siècle :** Cotisation de carte bancaire premium inutile (140 à 250 €/an), commissions de compte, alertes SMS facturées 2 €/mois.
3. **Les assurances doublons et garanties inutiles :** Assurance des moyens de paiement déjà couverte par la loi, extensions de garantie pour électroménager, double assurance scolaire.
4. **Les frais de commodité et de livraison :** Frais de service et pourboires automatiques récurrents sur les commandes de repas ou de courses express (+15 à +25 % de surcoût par commande).
5. **Les pénalités de retard et d'imprévoyance :** Majoration de PV, frais d'envoi de rappel de facture, intérêts de découvert à 16 %.
6. **L'illusion du petit déjeuner et de la collation extérieure :** Le sandwich triangle et le café latte pris chaque matin sur le trajet du travail (moyenne : 6,80 €/jour ouvré = 1 496 €/an).
7. **La sous-optimisation énergétique et télécoms :** Conserver le même contrat d'électricité ou forfait box pendant 4 ans sans jamais renégocier les tarifs de bienvenue.

#### Étude de Cas Chiffrée : L'Opération Colmatage de Caroline (29 ans)

Caroline a appliqué le protocole chirurgical de colmatage en un samedi après-midi. Voici le détail certifié des économies annuelles générées sans altérer son confort de vie :

| Poste Colmaté | Coût initial mensuel | Nouvelle solution adoptée | Gain annuel net |
| :--- | :--- | :--- | :--- |
| **Banque traditionnelle** | 18,50 €/mois (carte + frais) | Transfert vers banque en ligne (carte gratuite) | **222,00 €** |
| **Abonnements multimédias** | 44,97 €/mois (3 plateformes) | Conservation de 1 seule plateforme en rotation | **359,64 €** |
| **Assurance habitation & auto** | 98,00 €/mois | Renégociation via comparateur indépendant | **280,00 €** |
| **Forfait mobile & box** | 65,98 €/mois | Changement d'opérateur sans engagement | **372,00 €** |
| **Café & snacking de bureau** | 136,00 €/mois (6,80 €/j) | Thermos isotherme et café de spécialité maison | **1 128,00 €** |
| **Total des gains récupérés** | **363,45 € / mois** | **Trésorerie nette réinjectée dans l'épargne** | **2 361,64 € / an** |

En 4 heures d'efforts administratifs ciblés, Caroline a augmenté son pouvoir d'achat net de **196 € par mois** sans renoncer à aucun plaisir fondamental.

#### Le Piège Fréquent & La Parade

> ❌ **Le piège classique :** Résilier puis réactiver compulsivement des abonnements sous prétexte d'offres promotionnelles à 0,99 € le premier mois. Vous oublierez systématiquement de désactiver le renouvellement automatique.  
>  
> ✅ **La contre-mesure de l'Architecte :** La règle de la carte virtuelle jetable ou la résiliation immédiate dès la souscription d'une période d'essai (vos droits restent valables jusqu'au terme des 30 jours sans risque de reconduction).

---

> ⚡ **Action Immédiate (Moins de 24 Heures) :**
>
> 1. Ouvrez les réglages de votre smartphone : rubrique « Identifiant Apple » ou « Compte Google », puis « Abonnements ».
> 2. Identifiez au moins 2 abonnements ou options que vous n'avez pas utilisés au cours des 30 derniers jours et cliquez immédiatement sur « Résilier ».
> 3. Multipliez le montant mensuel économisé par 12 et notez ce gain net dans votre plan d'action.
""",

    "chapitre_01_section_04.md": """### 1.4 Mesurer sa valeur nette réelle sans illusion

Dans la société du paraître, la majorité des individus jaugent la réussite matérielle aux symboles visibles : la marque d'une montre, l'année d'immatriculation d'un SUV ou le quartier de résidence. Pourtant, ces marqueurs extérieurs sont très souvent les symptômes directs d'un endettement massif et d'un patrimoine net négatif. La seule boussole qui vaille en ingénierie financière est la **Valeur Nette Réelle (VNR)**. Elle constitue l'exact équivalent du bilan comptable d'une entreprise appliqué à votre foyer.

La formule de la Valeur Nette est impitoyablement simple, mais sa mise en œuvre exige une honnêteté intellectuelle sans faille :
$$\text{Valeur Nette} = \sum \text{Actifs Réels Liquidables} - \sum \text{Passifs et Dettes Totales}$$

Un actif est un élément de propriété qui met de l'argent dans votre poche ou qui conserve une valeur de marché vérifiable et immédiatement convertible en liquidités (comptes bancaires, livrets d'épargne, portefeuille d'actions, biens immobiliers nets de crédit). Un passif est tout ce qui draine de l'argent de votre poche (emprunts immobiliers restants dus, crédits à la consommation, dettes fiscales, soldes de cartes de crédit).

#### Le Grand Malentendu du Patrimoine Domestique

La plus grande illusion réside dans la valorisation des biens de consommation courante. Votre véhicule neuf acheté 32 000 € perd 20 % de sa valeur à la seconde exacte où ses roues quittent la concession, et continue de se déprécier de 10 % à 15 % chaque année tout en exigeant du carburant, de l'assurance et des réparations. Vos meubles design, vos téléviseurs et vos vêtements de marque ont une valeur de revente sur le marché d'occasion qui ne dépasse pas 10 % à 25 % de leur prix d'acquisition. Les comptabiliser comme des actifs est une faute méthodologique grave.

#### Étude de Cas Chiffrée : L'Autopsie Patrimoniale de Pierre et d'Amandine (38 ans)

Comparons le bilan patrimonial de deux profils aux apparences sociales trompeuses :

* **Pierre :** Propriétaire d'un pavillon valorisé à 380 000 € (crédit restant dû de 345 000 €), deux voitures haut de gamme en leasing (mensualité cumulée de 890 €), 3 200 € sur son compte courant et 18 000 € de crédits à la consommation divers (cuisine équipée, vacances).
* **Amandine :** Locataire de son appartement (loyer modéré de 750 €/mois), se déplace en transports et autopartage, détient 15 000 € sur ses livrets réglementés, 42 000 € sur un Plan d'Épargne en Actions (PEA) investi en indices mondiaux et zéro dette active.

| Poste de Bilan | Bilan de Pierre (Apparence riche) | Bilan d'Amandine (Discrétion financière) |
| :--- | :--- | :--- |
| **Actifs financiers liquides** | 3 200 € | 15 000 € (Livret A / LDDS) |
| **Actifs financiers investis** | 0 € | 42 000 € (Actions & ETF) |
| **Actifs immobiliers (valeur vénale)** | 380 000 € | 0 € (Locataire) |
| **Total Actifs Bruts** | 383 200 € | **57 000 €** |
| **Dettes immobilières (capital restant)** | 345 000 € | 0 € |
| **Dettes à la consommation** | 18 000 € | 0 € |
| **Total Passifs** | 363 000 € | **0 €** |
| **VALEUR NETTE RÉELLE** | **+20 200 €** (très vulnérable) | **+57 000 € (100 % liquide et résilient)** |

Pierre donne l'impression d'un notable fortuné, mais sa valeur nette réelle ne s'élève qu'à 20 200 €, grevée par un risque d'insolvabilité aigu au moindre accident de carrière. Amandine possède près de trois fois plus de richesse nette réelle, sans aucune charge de dette pesant sur son sommeil.

#### Le Piège Fréquent & La Parade

> ❌ **Le piège classique :** Surestimer la valeur de ses biens personnels (voiture, bijoux, matériel hi-fi) pour gonfler artificiellement sa valeur nette et se rassurer.  
>  
> ✅ **La contre-mesure de l'Architecte :** Appliquer une décote de liquidité immédiate. Pour tout bien matériel autre que l'immobilier ou les actifs financiers cotés, n'inscrivez dans votre bilan que la valeur cash nette que vous obtiendriez en le vendant en 48 heures sur une plateforme d'occasion (soit environ 20 % de la valeur à neuf).

---

> ⚡ **Action Immédiate (Moins de 24 Heures) :**
>
> 1. Prenez une feuille blanche et tracez deux colonnes : à gauche « Ce que je possède réellement », à droite « Ce que je dois à des tiers ».
> 2. Relevez le solde exact de vos comptes bancaires et le capital restant dû de chacun de vos emprunts.
> 3. Soustrayez la colonne de droite de celle de gauche pour obtenir votre **Score de Valeur Nette Actuel**. Si le résultat est négatif, pas de panique : vous venez de fixer le point de départ de votre reconstruction.
""",

    "chapitre_01_section_05.md": """### 1.5 Établir son point zéro et reprogrammer ses réflexes monétaires

Toute transformation pérenne commence par un acte d'acceptation lucide et dénué de jugement : la fixation de votre **Point Zéro**. La plupart des individus reportent indéfiniment la reprise en main de leurs finances personnelles parce qu'ils appréhendent la confrontation avec leurs erreurs passées : ce crédit à la consommation absurde souscrit pour un téléviseur, ces vacances financées par un découvert bancaire ou ces années de salaire volatilisées sans épargne. Cette culpabilité stérile est le meilleur allié du système bancaire prédateur.

En ingénierie patrimoniale, le passé est une charge amortie non récupérable (*sunk cost*). Ce qui s'est produit jusqu'à aujourd'hui appartient à l'histoire ; seule compte la trajectoire vectorielle que vous imprimez à partir de cet instant précis. Votre Point Zéro n'est pas un certificat d'échec, c'est l'étalonnage indispensable des capteurs de votre nouveau système de pilotage.

#### La Reprogrammation des 3 Réflexes Monétaires

Pour que l'architecture technique fonctionne, vous devez remplacer les réflexes primaires de consommation par trois lois d'ingénierie financière :

1. **Loi n° 1 : L'Inversion du Flux d'Épargne.** La formule de faillite est : `Revenu - Dépenses = Épargne (s'il reste quelque chose)`. La formule de l'Architecte est : `Revenu - Épargne Automatique = Ce que vous êtes autorisé à dépenser l'esprit tranquille`.
2. **Loi n° 2 : La Dissociation de l'Argent et de l'Humeur.** Ne prenez jamais une décision de dépense supérieure à 50 € dans un état émotionnel altéré (fatigue intense le vendredi soir, euphorie après une bonne nouvelle, déception professionnelle).
3. **Loi n° 3 : La Focalisation sur les Pourcentages plutôt que sur les Sommes Brutes.** Raisonner en montants absolus induit en erreur. Épargner 200 € sur 1 000 € de revenu est un exploit monumental (20 %) ; épargner 200 € sur 5 000 € est une anomalie structurelle (4 %).

#### Étude de Cas Chiffrée : La Bascule de Trajectoire de Kevin (26 ans)

Kevin a établi son Point Zéro au 1er janvier avec une situation classique de jeune actif : découvert autorisé utilisé en permanence (-650 €), un prêt étudiant en cours (8 400 € restants à 2,1 %) et zéro épargne. Il a signé son « Contrat d'Étalonnage » en s'engageant à sanctuariser un taux d'épargne plancher de 12 % sur son salaire net de 1 850 € (soit 222 €/mois).

Voici la projection de son redressement exécuté mois par mois :

* **Mois 1 à 3 :** Absorption définitive du découvert bancaire grâce à la récupération de 220 €/mois de micro-fuites. Solde du compte courant ramené à +300 € au 31 mars.
* **Mois 4 à 8 :** Constitution d'un coussin de sécurité de 1 100 € sur un livret d'urgence. Disparition totale des agios (gain de 18 €/mois).
* **Mois 9 à 24 :** Accélération du remboursement de son prêt étudiant avec un apport complémentaire de 150 €/mois tout en initiant un premier versement automatique de 75 €/mois sur un PEA indiciel.

| Étape de la Trajectoire | Situation au Point Zéro | Situation à 12 Mois | Situation à 24 Mois |
| :--- | :--- | :--- | :--- |
| **Solde bancaire moyen** | -650 € (Découvert) | +500 € (Tampon de sécurité) | +1 000 € (Tampon sanctuarisé) |
| **Épargne d'urgence disponible** | 0 € | 2 200 € | 3 800 € |
| **Dettes restantes** | 8 400 € | 5 950 € | 3 100 € |
| **Investissement indiciel actif** | 0 € | 450 € | 1 950 € |
| **Valeur Nette Totale** | **-9 050 €** | **-2 800 €** | **+3 650 € (Bascule positive)** |

En 24 mois d'application disciplinée, Kevin a opéré un redressement patrimonial net de **+12 700 €**, sans jamais avoir changé de salaire.

#### Le Piège Fréquent & La Parade

> ❌ **Le piège classique :** Vouloir aller trop vite et s'imposer un taux d'épargne insoutenable de 40 % dès le premier mois. Vous tiendrez 3 semaines avant de craquer dans un accès de frustration compensatoire.  
>  
> ✅ **La contre-mesure de l'Architecte :** La montée en charge progressive. Démarrez à 10 % de vos revenus nets lors du mois 1, puis augmentez ce curseur de 1 % chaque mois jusqu'à atteindre votre rythme de croisière optimal (entre 15 % et 25 %).

---

> ⚡ **Action Immédiate (Moins de 24 Heures) :**
>
> 1. Écrivez sur une fiche la date d'aujourd'hui, votre solde de compte courant exact et le montant de vos dettes. C'est votre Point Zéro officiel.
> 2. Définissez votre **Taux d'Épargne Initial Garanti** pour le mois prochain (fixez un objectif réaliste de 10 % de vos revenus).
> 3. Rangez cette fiche dans votre dossier financier : elle servira de référence pour mesurer votre progression trimestrielle.
"""
}

for nom_fichier, contenu in SECTIONS_CHAP_1_TO_3.items():
    p = OUTPUT_DIR / nom_fichier
    p.write_text(contenu.strip() + "\n", encoding="utf-8")
    print(f"✅ Section rédigée : {nom_fichier} ({len(contenu.split())} mots)")

print("\n🎉 Chapitre 1 complet généré avec succès dans livre_sections/ !")
