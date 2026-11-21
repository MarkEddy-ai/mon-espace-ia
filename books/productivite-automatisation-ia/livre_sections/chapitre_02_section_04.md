
### 2.4 2.4 Context Window et mémoire persistante

### 2.4 Context Window et mémoire persistante

Un Large Language Model (LLM) ne dispose pas d'une conscience continue, mais d'une fenêtre de contexte (*context window*). Cette limite technique détermine le volume maximal de texte – instructions, historique et documents joints – qu'un modèle peut traiter et retenir simultanément au cours d'une session. Dépasser ce seuil provoque un phénomène d'amnésie sélective : les premières consignes fournies se dissolvent dans le flux des nouveaux échanges, diluant la précision des réponses et altérant la cohérence stylistique. Pour le solopreneur, subir cette contrainte, c'est accepter de réexpliquer son métier, ses offres et son positionnement à chaque nouvelle session de travail.

L'architecture de l'information moderne repose sur l'externalisation de la mémoire vers des espaces persistants : les Custom GPTs sur l'écosystème OpenAI et les Projets sur l'interface Claude. Ces environnements permettent d'injecter une base documentaire immuable et des instructions permanentes. 

#### Étude de cas : Le cabinet de conseil en stratégie de Sarah

Sarah, consultante indépendante en transformation digitale, perdait en moyenne 45 minutes par jour à recadrer ses assistants textuels sur son ton, sa méthodologie et ses grilles tarifaires. Ses prompts initiaux étaient systématiquement oubliés dès que la conversation dépassait 10 000 jetons (*tokens*).

En structurant un **Projet Claude** dédié, elle a centralisé sa mémoire externe :
1. **Un document de positionnement de 3 pages** détaillant sa voix éditoriale (factuelle, directe, sans jargon).
2. **Trois études de cas clients anonymisées** servant de référence structurelle pour ses propositions commerciales.
3. **Une grille tarifaire et un catalogue de prestations** mis à jour trimestriellement.

Résultat : le taux de rejet de ses propositions commerciales par ses prospects est passé de 35 % à 8 %, les documents générés intégrant instantanément sa syntaxe exacte et ses conditions de vente, sans qu'il soit nécessaire de les repréciser.

| Composant de la Mémoire Persistante | Rôle Stratégique | Format Recommandé | Fréquence de Mise à Jour |
| :--- | :--- | :--- | :--- |
| **Instructions Globales** | Fixer le rôle, les limites et les interdits comportementaux | Markdown structuré (< 500 mots) | Mensuelle |
| **Base Documentaire** | Fournir les faits, les chiffres et les références métier | PDF ou .txt brut (< 20 Mo) | Trimestrielle |
| **Historique Dynamique** | Maintenir le fil de la réflexion en cours | Session active de chat | Continue |

#### Méthode pas-à-pas pour nourrir son IA de manière pérenne

L'alimentation d'un espace de travail persistant ne s'improvise pas par un simple glisser-déposer de fichiers en vrac. Une architecture d'information propre garantit des réponses affûtées.

1. **L'audit des actifs textuels :** Rassemblez vos 5 meilleurs textes (articles, e-mails, posts) et vos 3 pires (ceux qui ne vous ressemblent pas). L'IA apprend autant par le contre-exemple que par le modèle.
2. **La distillation sémantique :** Rédigez un fichier unique nommé `SYSTEM_PROMPT_METIER.md`. Divisez-le en trois sections strictes : 
   - *Identité* (Qui vous êtes, votre cible).
   - *Style* (Longueur des phrases, niveau de langue, termes à bannir).
   - *Méthodologie* (Vos étapes de résolution de problèmes).
3. **L'injection ciblée :** Uploadez ces documents dans les paramètres système de votre Custom GPT ou de votre Projet Claude, et non dans le fil de discussion général.
4. **Le test de résistance (Stress Test) :** Soumettez une question piège nécessitant une donnée précise issue de votre base documentaire. Si l'IA hallucine ou omet la référence, simplifiez la structure du document source en utilisant des listes à puces plutôt que des paragraphes denses.

> « Une IA sans mémoire persistante est un employé brillant mais atteint d'amnésie antérograde : chaque matin, vous devez lui réapprendre son métier. »

> ### Action Immédiate
> Ouvrez votre outil d'IA favori et créez dès aujourd'hui un espace dédié (Projet ou GPT personnalisé). 
> 1. Rédigez un fichier texte de 200 mots définissant précisément votre ton (ex: "Direct, pragmatique, sans métaphore excessive, orienté ROI").
> 2. Ajoutez-y votre biographie professionnelle ou la description de votre offre principale.
> 3. Testez-le en lui demandant de rédiger un post court pour vos réseaux sociaux : si le résultat nécessite plus d'une correction mineure, affinez vos consignes de style dans le fichier de base.
