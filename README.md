# Routes à risque — Dashboard BAAC 2021–2024

Projet individuel de **Gabriel Geniez (20231128)** pour le module Data Analysis & Visualization.

Cette application Streamlit analyse les accidents corporels enregistrés en France entre 2021 et 2024. Elle aide les collectivités et acteurs de la sécurité routière à repérer les périodes, territoires et catégories d'usagers associés aux situations les plus graves.

## Questions traitées

1. Comment le nombre de victimes évolue-t-il dans le temps ?
2. Où les accidents et les victimes se concentrent-ils ?
3. Quels jours et horaires concentrent les accidents, notamment ceux avec tué ou hospitalisé ?
4. Quelle part des victimes est tuée ou hospitalisée dans chaque catégorie ?
5. Quels diagnostics et quelles pistes de prévention ces observations permettent-elles de préparer ?

## Storytelling et prévention

Le parcours suit les conséquences humaines, les territoires, les créneaux et les catégories de victimes, puis relie les constats à des diagnostics, pistes de prévention et indicateurs de suivi. Les repères officiels fixes sont séparés des résultats recalculés avec les filtres.

- [ONISR : bilan définitif 2024](https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere).
- [Cerema : chiffres clés nationaux et objectif 2030](https://www.cerema.fr/fr/activites/mobilites/chiffres-cles).
- [Ministère de l’Intérieur : conseils de conduite](https://www.masecurite.interieur.gouv.fr/fr/fiches-pratiques/securite-routiere-et-transport/regles-bonne-conduite-route).

Sources consultées le 23 octobre 2026. Le dashboard ne démontre ni les causes des accidents ni l’efficacité des actions proposées.

Pour préparer les réponses au professeur sur les données : [fiche méthode et questions fréquentes](GESTION_DATA.md).

## Lecture des interactions

- Le classement départemental propose volumes et proportions, avec un minimum de victimes configurable pour la seconde lecture (30 par défaut, seuil descriptif sans garantie statistique).
- La heatmap distingue tous les accidents, ceux avec tué ou hospitalisé, et ceux avec tué.
- Les catégories d’usagers peuvent être comparées en proportions ou en effectifs. Il s’agit des rôles conducteur/passager/piéton, distincts des modes de déplacement.
- Les conséquences de chaque accident sont recalculées parmi les victimes sélectionnées : carte, heatmap et KPIs partagent le même périmètre.
- Une sélection vide des catégories ou des environnements donne un résultat vide ; une sélection vide des départements conserve toute la France.
- Les territoires ultramarins restent inclus. Les indicateurs de qualité décrivent le jeu complet avant les filtres.
- « Tués ou hospitalisés » désigne les codes BAAC 2 et 3 parmi les victimes. Ce regroupement n’est pas équivalent aux blessés graves médicaux MAIS3+ estimés dans les bilans ONISR.

## Source

- Producteur : Ministère de l'Intérieur — ONISR.
- Portail : [data.gouv.fr — Bases annuelles BAAC 2005–2024](https://www.data.gouv.fr/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024)
- Période utilisée : 2021–2024.
- Tables utilisées : caractéristiques, lieux, véhicules et usagers.
- Licence : Licence Ouverte / Open Licence 2.0.

## Installation et lancement

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/prepare_data.py
streamlit run app.py
```

Les fichiers préparés sont inclus dans `data/processed` pour garantir un démarrage rapide du déploiement. Le script reste disponible pour reconstruire intégralement ces fichiers depuis les URL officielles.

## Méthode

Le pipeline normalise les schémas annuels, convertit les dates et coordonnées, décode les principales variables puis joint les tables avec les identifiants BAAC. Deux tables sont produites :

- `accidents.parquet` : exactement une ligne par accident, utilisée pour les comptages et la carte ;
- `users.parquet` : une ligne par victime, utilisée pour les analyses de gravité et de profil.

Cette séparation évite de compter plusieurs fois un accident comportant plusieurs usagers. Des contrôles vérifient l'unicité des accidents, les dates, les gravités et la couverture géographique.

## Limites et éthique

- Les données couvrent les accidents corporels connus des forces de l'ordre, pas tous les incidents routiers.
- Les volumes ne sont pas des taux de risque : aucune donnée d'exposition ou de trafic n'est disponible ici.
- Les relations observées sont descriptives et ne prouvent pas de causalité.
- La carte n'affiche aucune donnée directement identifiante et limite le nombre de points pour préserver les performances.
- Les changements de processus de saisie peuvent affecter certaines comparaisons historiques.

## Structure

```text
app.py                    Interface et narration Streamlit
scripts/prepare_data.py   Téléchargement, nettoyage et validation
utils/data.py             Chargement, cache et filtres
utils/viz.py              Visualisations Plotly cohérentes
utils/constants.py        Libellés, chemins et URL officielles
tests/test_data.py        Tests des filtres et indicateurs
data/processed/           Données optimisées pour le déploiement
```

## Reproductibilité

Le dashboard utilise `st.cache_data`, des fichiers Parquet compressés et un échantillonnage déterministe de la carte. Les dépendances nécessaires sont déclarées dans `requirements.txt` et les contrôles automatiques peuvent être lancés avec :

```powershell
python -m pytest
```

