# Routes à risque — Comprendre les accidents pour mieux prévenir

Projet individuel de **Gabriel Geniez · 20231128 · Data Engineering DE1**, module **Data Analysis & Visualization**, proposé par le professeur Mano Mathew, EFREI, 2026–2027.

- [Application Streamlit](https://routes-a-risque-slowzzzz.streamlit.app/)
- [Dépôt GitHub](https://github.com/Slowzzzz/routes-a-risque)
- [Storyboard du parcours](STORYBOARD.md)

## Problématique et public

**Où agir, quand sensibiliser et qui protéger ?** Le dashboard aide les collectivités et acteurs de la sécurité routière à préparer un diagnostic local à partir des accidents corporels enregistrés en France entre 2021 et 2024, métropole et outre-mer. Le parcours suit les conséquences humaines, les territoires, les créneaux et les catégories de victimes, puis propose des pistes de prévention et de suivi.

## Données et sources

Le projet utilise les quatre tables annuelles **caractéristiques, lieux, véhicules et usagers** du fichier BAAC, produites par le **ministère de l’Intérieur / ONISR**, diffusées sur [data.gouv.fr](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024), sous **Licence Ouverte / Open Licence 2.0**. Les 16 URL de téléchargement sont conservées dans `utils/constants.py`.

Les fichiers Parquet inclus permettent de lancer l’application sans télécharger les CSV bruts. Le script de préparation permet de les reconstruire depuis les sources officielles et réutilise les téléchargements déjà présents.

Les repères nationaux et conseils sont attribués à leurs sources : [bilan définitif ONISR 2024](https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere), [Cerema, chiffres clés et objectif 2030](https://www.cerema.fr/fr/activites/mobilites/chiffres-cles) et [ministère de l’Intérieur, conseils de conduite](https://www.masecurite.interieur.gouv.fr/fr/fiches-pratiques/securite-routiere-et-transport/regles-bonne-conduite-route). Liens vérifiés le 24 octobre 2026. Les repères officiels 2024 restent fixes lorsque les filtres changent.

Logo EFREI : [site officiel de l’école](https://www.efrei.fr/wp-content/uploads/2025/09/Logo-Efrei-CMJN-768x384.png), conservé dans `assets/` pour l’affichage local.

## Installation et lancement

Environnement de référence : **Python 3.13**. Depuis la racine du projet sous Windows :

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Sous macOS/Linux, utiliser `python3.13 -m venv .venv`, puis `.venv/bin/python` à la place de `.\.venv\Scripts\python.exe`.

Les dépendances directes et transitives sont figées dans `requirements.txt`. Le déploiement Streamlit Community Cloud utilise `main`, `app.py` et Python 3.13.

Pour reconstruire les données et lancer les vérifications :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe -m pytest -q
```

La reconstruction demande une connexion Internet et environ 132 Mo pour les CSV bruts, placés dans `data/raw/`, exclus de Git. Les données préparées occupent environ 14 Mo. La carte charge un fond cartographique en ligne.

## Lecture du dashboard

| Vue | Ce qu’elle montre | Intérêt pour la prévention |
| --- | --- | --- |
| Quatre indicateurs | Accidents, victimes, tués et proportion de tués ou hospitalisés | Situer l’ampleur du bilan sur le périmètre filtré |
| Courbes mensuelles | Toutes les victimes et, parmi elles, les tués ou hospitalisés ; mois à zéro conservés | Repérer les périodes à examiner et distinguer volume et conséquences |
| Carte | Un point par accident géolocalisé ; couleur selon la conséquence maximale parmi les victimes sélectionnées | Situer les lieux à approfondir sur le terrain |
| Classement départemental | Jusqu’à 12 départements, par nombre de victimes ou proportion de tués/hospitalisés | Comparer concentration et conséquences ; seuil de 30 victimes par défaut pour les proportions |
| Tableau par milieu | Effectifs et proportions en agglomération et hors agglomération | Adapter les diagnostics aux contextes de circulation |
| Carte de chaleur jour/heure | Nombre d’accidents cumulé par jour de semaine et tranche d’une heure, selon la gravité choisie | Repérer les moments où mener observations et sensibilisation |
| Barres par catégorie | Répartition des victimes par gravité, en pourcentages ou effectifs | Comparer les conséquences entre groupes puis dimensionner les actions |
| Tableau de prévention | Constat filtré, diagnostic, piste d’action et indicateur de suivi | Traduire l’analyse descriptive en questions opérationnelles |

Chaque visualisation est accompagnée d’un commentaire de lecture et d’une explication de son utilité. Les survols indiquent les valeurs ; les textes de constat sont recalculés avec les filtres.

Les filtres portent sur la période, les départements, le milieu et le rôle des usagers. **Départements vide = France entière ; milieu ou catégories vide = aucune donnée.** Un filtre piétons recalcule aussi les conséquences de chaque accident à partir des seules victimes piétonnes. Les contrôles de qualité décrivent toujours le jeu complet avant filtrage.

## Résultats et implications

Le jeu préparé contient **221 044 accidents** et **291 375 victimes** entre 2021 et 2024. Entre 2023 et 2024, les victimes passent de **72 272 à 72 267**, tandis que les personnes tuées passent de **3 398 à 3 432** : un volume stable peut masquer une dégradation du bilan mortel.

Sur les quatre années, la proportion de tués ou hospitalisés est d’environ **33,4 % pour les piétons**, **31,8 % pour les conducteurs** et **26,6 % pour les passagers**. Cela justifie d’examiner les circonstances et les besoins propres à chaque public ; ces valeurs ne mesurent pas le risque individuel de marcher, conduire ou voyager comme passager.

Les priorités proposées sont des **pistes à discuter avec les acteurs locaux**. Avant une action, compléter par des observations de terrain et des données de trafic. Son évaluation exige des périodes comparables et un protocole permettant de distinguer son effet d’autres évolutions.

## Méthode et qualité

1. Normaliser les colonnes et identifiants annuels ; construire les dates ; décoder les catégories BAAC.
2. Convertir les coordonnées décimales, contrôler leurs bornes terrestres et exclure le couple `(0, 0)` de la carte. Conserver les collectivités du Pacifique. Ce contrôle ne valide pas la position exacte sur une route.
3. Conserver les heures absentes ou invalides comme valeurs manquantes : elles restent dans les indicateurs et sont exclues de la carte de chaleur, sans être assimilées à minuit.
4. Regrouper les types de voies par accident avant de joindre caractéristiques et lieux ; rattacher les véhicules aux usagers avec les identifiants disponibles. Vérifier les relations un-à-un ou plusieurs-à-un lors des jointures.
5. Calculer l’âge approximatif (année de l’accident moins année de naissance) et les tranches d’âge. Les âges hors de 0–110 ans deviennent manquants.
6. Produire une table à une ligne par accident et une table à une ligne par victime, hors indemnes. Vérifier l’unicité des identifiants, les dates et les codes de gravité avant l’écriture.

`data/processed/quality.json` documente les effectifs, doublons, données manquantes et validations. Les coordonnées absentes excluent uniquement les points de la carte. L’échantillon cartographique est limité à **7 000 accidents**, avec la graine **42** ; tous les indicateurs utilisent la sélection complète. `st.cache_data` évite les relectures à chaque interaction.

Les tests couvrent les filtres combinés, l’absence de double comptage, la gravité recalculée, les sélections vides, les proportions, les heures inconnues, les mois à zéro et un parcours Streamlit avec les données livrées.

## Dictionnaire des principales variables

| Variable | Définition / unité |
| --- | --- |
| `accident_id`, `user_id` | Identifiants techniques des accidents et personnes ; aucune identité civile |
| `date`, `year`, `weekday`, `hour` | Date, année, jour et heure de l’accident ; heure de 0 à 23 ou manquante |
| `department`, `environment` | Code département/territoire et milieu en/hors agglomération |
| `latitude`, `longitude` | Coordonnées en degrés décimaux, ou valeurs manquantes |
| `user_type` | Rôle : conducteur, passager, piéton ; distinct du mode de déplacement |
| `gravity_code`, `gravity` | BAAC : 2 = tué, 3 = blessé hospitalisé, 4 = blessé léger ; indemnes exclus |
| `is_serious`, `is_killed` | Indicateurs booléens des codes 2/3 et du code 2 |
| `victims`, `serious`, `killed` | Effectifs par accident, recalculés selon les victimes sélectionnées |
| `age`, `age_group` | Âge approximatif en années et tranche d’âge ; valeurs inconnues conservées |
| `vehicle_type`, `road_type`, `weather`, `light` | Libellés regroupés du véhicule, de la voie, de la météo et de la luminosité |

La proportion de tués ou hospitalisés vaut **100 × (codes 2 + 3) / victimes**. Ce regroupement ne correspond pas aux blessés graves médicaux **MAIS3+** estimés dans les bilans ONISR.

## Limites et transparence

- Le BAAC couvre les accidents corporels connus des forces de l’ordre ; il ne recense pas tous les accidents ni tous les blessés.
- Sans trafic, distances ou temps de déplacement, les volumes et proportions ne sont pas des taux de risque individuel.
- Les associations observées ne prouvent aucune cause et ne mesurent pas l’efficacité d’une action.
- Les petits effectifs donnent des proportions instables ; le seuil configurable du classement n’est pas une garantie statistique.
- Une variation mensuelle ne prouve pas une saisonnalité. Le contexte sanitaire de 2021 affecte aussi la comparaison.
- Les bilans officiels peuvent porter sur la seule métropole ou utiliser des estimations médicales ; vérifier le périmètre avant comparaison.
- La carte représente un échantillon et des coordonnées déclarées ; elle ne permet pas de désigner à elle seule un point noir routier. Aucun nom ni adresse personnelle n’est affiché.

## Contenu du rendu

```text
app.py                    Interface, commentaires et narration
utils/                    Chargement, filtres, constantes et graphiques
scripts/prepare_data.py   Téléchargement, nettoyage et validation
data/processed/           Deux tables Parquet et rapport qualité
assets/efrei-logo.png     Logo affiché dans la barre latérale
.streamlit/config.toml    Configuration visuelle
tests/                    Vérifications des calculs et interactions
requirements.txt          Dépendances figées de l’application
requirements-dev.txt      Dépendances figées des tests
README.md                 Rapport, sources et instructions
STORYBOARD.md             Parcours narratif demandé
```

Archive de remise : **`StApp26_20231128_GENIEZ_DE1.zip`**. Elle contient les livrables ci-dessus et exclut Git, environnements virtuels, caches, CSV bruts et notes de travail. La vidéo de démonstration de **2 à 4 minutes** est réalisée et ajoutée à la remise séparément par Gabriel.
