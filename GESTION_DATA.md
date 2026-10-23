# Comprendre et expliquer la gestion des données

## À dire en 30 secondes

« J’utilise les fichiers publics BAAC de 2021 à 2024, produits par le ministère de l’Intérieur et diffusés sur data.gouv.fr. Je nettoie et relie quatre tables avec pandas. Je produis une table par accident et une table par victime pour éviter les doubles comptages. Je les enregistre en Parquet, puis Streamlit les charge avec un cache. L’analyse reste descriptive : elle aide à préparer la prévention, sans mesurer le risque individuel ni démontrer une cause. »

## Le parcours des données

1. **Acquisition** : `scripts/prepare_data.py` télécharge les CSV officiels dans `data/raw/<année>/`. Il réutilise les fichiers déjà présents et non vides. Les URL sont dans `utils/constants.py`.
2. **Nettoyage** : lecture en UTF-8 avec séparateur `;`, harmonisation des noms d’identifiants, construction des dates, extraction de l’heure, conversion des coordonnées et normalisation des codes départementaux. Les codes de gravité, météo et catégories sont transformés en libellés.
3. **Enrichissement** : calcul du jour de semaine, de l’âge approximatif (année de l’accident moins année de naissance), des tranches d’âge et des indicateurs victime, hospitalisé ou tué.
4. **Jointures** : caractéristiques + lieux par identifiant d’accident ; usagers + véhicules par identifiants d’accident et de véhicule disponibles ; ajout du contexte de l’accident aux usagers. Les types de routes sont regroupés par accident avant la jointure. Les jointures vérifient les relations un-à-un ou plusieurs-à-un.
5. **Sortie** : concaténation des quatre années et écriture compressée dans `data/processed/`. `accidents.parquet` contient une ligne par accident ; `users.parquet`, une ligne par victime, après exclusion des indemnes. `quality.json` résume les contrôles.

## Les questions probables du professeur

**Pourquoi séparer accidents et victimes ?** Un accident avec trois victimes compte pour un accident et trois victimes. Compter les lignes d’une grande table fusionnée gonflerait le nombre d’accidents.

**Comment définis-tu une victime et la gravité ?** Victime = code BAAC 2 (tué), 3 (blessé hospitalisé) ou 4 (blessé léger). La proportion « tués ou hospitalisés » vaut `(codes 2 + 3) / victimes × 100`. Ce regroupement n’est pas la définition médicale des blessés graves MAIS3+ utilisée dans certaines estimations ONISR.

**Comment gères-tu les valeurs manquantes ?** Les conversions impossibles deviennent manquantes. Les âges hors de 0–110 ans et les coordonnées hors des bornes configurées sont écartés du champ concerné, sans supprimer automatiquement l’accident. Sans coordonnées, l’accident reste dans les indicateurs mais n’apparaît pas sur la carte. Certains codes inconnus reçoivent un libellé de remplacement. Attention : une heure non convertible est actuellement remplacée par 0 h, choix perfectible à signaler.

**Comment vérifies-tu la qualité ?** Le rapport actuel indique **221 044 accidents**, **291 375 victimes**, aucun doublon d’identifiant accident ou victime et **99,24 %** de coordonnées disponibles. Les dates et les codes de gravité des victimes sont contrôlés. Les bornes géographiques restent un contrôle grossier, pas une validation cartographique exacte. Une valeur non manquante ou un libellé de remplacement ne garantit pas une information parfaite.

**Les filtres changent-ils les calculs ?** Oui : période, départements, environnement et catégories sélectionnent les victimes et les accidents correspondants. Les nombres et la gravité de chaque accident sont recalculés parmi ces victimes : en filtrant les piétons, un conducteur tué ne rend pas mortelle la couleur d’un accident où le piéton est légèrement blessé. Les contrôles qualité affichés concernent toutefois le jeu complet.

**Pourquoi Parquet, cache et échantillonnage ?** Parquet conserve les types et compresse les données ; `st.cache_data` évite de relire les fichiers à chaque interaction. Seule la carte est limitée à 7 000 points, avec une graine fixe pour reproduire l’échantillon. Les indicateurs utilisent toute la sélection ; la carte échantillonnée n’est pas un inventaire exhaustif des lieux.

**Peux-tu dire où le risque est le plus élevé ?** Je peux comparer les volumes et les proportions parmi les victimes enregistrées. Sans trafic, distances ou temps de déplacement, je ne peux pas mesurer un risque individuel. Le minimum de 30 victimes du classement est un seuil de lecture configurable, pas une garantie statistique.

**Pourquoi tes chiffres peuvent-ils différer d’un bilan officiel ?** Il faut vérifier l’année, métropole ou outre-mer, bilan provisoire ou définitif, et comptages BAAC ou estimations médicales. Les données couvrent les accidents corporels connus des forces de l’ordre, pas tous les accidents ni tous les blessés.

**Comment reproduire et vérifier le travail ?** Exécuter `python scripts/prepare_data.py`, puis `python -m pytest` et `streamlit run app.py` dans l’environnement du projet. Les sept tests couvrent notamment les filtres, la cohérence de gravité, les proportions et la heatmap. Les URL et dépendances sont déclarées ; leur fixation plus stricte et des empreintes des CSV amélioreraient encore la reproductibilité.

## Ce qu’il reste à clarifier avec le professeur

- L’analyse descriptive suffit-elle, ou faut-il des tests statistiques / données d’exposition ?
- Faut-il un déploiement public, et où déposer la vidéo ?
- Pour aller plus loin : mesurer les défauts de jointure et les codes inconnus, mieux traiter les heures manquantes et évaluer une action avec un protocole avant/après et un groupe de comparaison.

La finalité : **constat → diagnostic local → piste de prévention → suivi**, en distinguant les calculs du projet des conseils nationaux.
