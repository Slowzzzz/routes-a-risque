from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ACCIDENTS_PATH = PROCESSED_DIR / "accidents.parquet"
USERS_PATH = PROCESSED_DIR / "users.parquet"
QUALITY_PATH = PROCESSED_DIR / "quality.json"

DATASET_PAGE = (
    "https://www.data.gouv.fr/datasets/"
    "bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-"
    "routiere-annees-de-2005-a-2024"
)

YEARS = (2021, 2022, 2023, 2024)

RESOURCE_URLS = {
    2021: {
        "characteristics": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2020/20221024-113743/carcteristiques-2021.csv",
        "locations": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2020/20221024-113901/lieux-2021.csv",
        "vehicles": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2020/20221024-113925/vehicules-2021.csv",
        "users": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2022/20231009-140337/usagers-2021.csv",
    },
    2022: {
        "characteristics": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-093927/carcteristiques-2022.csv",
        "locations": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-094112/lieux-2022.csv",
        "vehicles": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-094147/vehicules-2022.csv",
        "users": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2021/20231005-094229/usagers-2022.csv",
    },
    2023: {
        "characteristics": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20241028-103125/caract-2023.csv",
        "locations": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20241023-153219/lieux-2023.csv",
        "vehicles": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20241023-153253/vehicules-2023.csv",
        "users": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2023/20241023-153328/usagers-2023.csv",
    },
    2024: {
        "characteristics": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251021-115900/caract-2024.csv",
        "locations": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251021-115812/lieux-2024.csv",
        "vehicles": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251107-100240/vehicules-2024.csv",
        "users": "https://static.data.gouv.fr/resources/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2024/20251021-115506/usagers-2024.csv",
    },
}

GRAVITY_LABELS = {
    1: "Indemne",
    2: "Tué",
    3: "Blessé hospitalisé",
    4: "Blessé léger",
}

USER_LABELS = {
    1: "Conducteur",
    2: "Passager",
    3: "Piéton",
}

VEHICLE_LABELS = {
    0: "Indéterminable",
    1: "Vélo",
    2: "Cyclomoteur",
    3: "Voiturette",
    7: "Voiture",
    10: "Véhicule utilitaire",
    13: "Poids lourd",
    14: "Poids lourd",
    15: "Poids lourd",
    16: "Tracteur routier",
    17: "Tracteur routier",
    30: "Scooter",
    31: "Moto",
    32: "Scooter",
    33: "Moto",
    34: "Moto",
    35: "Quad",
    36: "Poids lourd",
    37: "Autobus / autocar",
    38: "Autobus / autocar",
    39: "Train",
    40: "Tramway",
    41: "Trottinette / EDPM",
    42: "Trottinette / EDPM",
    43: "Deux-roues motorisé",
    50: "Engin spécial",
    60: "Engin spécial",
    80: "VAE",
    99: "Autre véhicule",
}

LIGHT_LABELS = {
    1: "Plein jour",
    2: "Aube ou crépuscule",
    3: "Nuit sans éclairage",
    4: "Nuit, éclairage éteint",
    5: "Nuit, éclairage allumé",
}

WEATHER_LABELS = {
    1: "Normale",
    2: "Pluie légère",
    3: "Pluie forte",
    4: "Neige / grêle",
    5: "Brouillard / fumée",
    6: "Vent fort / tempête",
    7: "Éblouissante",
    8: "Couverte",
    9: "Autre",
}

ROAD_LABELS = {
    1: "Autoroute",
    2: "Route nationale",
    3: "Route départementale",
    4: "Voie communale",
    5: "Hors réseau public",
    6: "Parc de stationnement",
    7: "Route de métropole",
    9: "Autre",
}

SEVERITY_ORDER = ["Tué", "Blessé hospitalisé", "Blessé léger", "Indemne"]
SEVERITY_COLORS = {
    "Tué": "#7F0000",
    "Blessé hospitalisé": "#D1495B",
    "Blessé léger": "#F4A261",
    "Indemne": "#8DA9C4",
}

