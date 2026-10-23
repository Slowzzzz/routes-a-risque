from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.constants import (  # noqa: E402
    ACCIDENTS_PATH,
    GRAVITY_LABELS,
    LIGHT_LABELS,
    PROCESSED_DIR,
    QUALITY_PATH,
    RESOURCE_URLS,
    ROAD_LABELS,
    USERS_PATH,
    USER_LABELS,
    VEHICLE_LABELS,
    WEATHER_LABELS,
    YEARS,
)

RAW_DIR = PROJECT_ROOT / "data" / "raw"
WEEKDAYS = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}


def download_file(url: str, destination: Path) -> None:
    if destination.exists() and destination.stat().st_size > 0:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=120, stream=True) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                output.write(chunk)


def read_baac(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)


def clean_coordinates(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.replace(",", ".", regex=False)
    return pd.to_numeric(text, errors="coerce")


def normalize_department(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip().str.upper()
    text = text.str.replace(r"\.0$", "", regex=True)
    return text.str.zfill(2)


def age_group(age: pd.Series) -> pd.Categorical:
    return pd.cut(
        age,
        bins=[-1, 13, 17, 24, 44, 64, 200],
        labels=["0–13 ans", "14–17 ans", "18–24 ans", "25–44 ans", "45–64 ans", "65 ans et +"],
    )


def load_year(year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = {}
    for table, url in RESOURCE_URLS[year].items():
        path = RAW_DIR / str(year) / f"{table}.csv"
        download_file(url, path)
        paths[table] = path

    characteristics = read_baac(paths["characteristics"])
    locations = read_baac(paths["locations"])
    vehicles = read_baac(paths["vehicles"])
    users = read_baac(paths["users"])

    for frame in (characteristics, locations, vehicles, users):
        frame.columns = frame.columns.str.strip()
        frame.rename(columns={"Num_Acc": "accident_id", "Accident_Id": "accident_id"}, inplace=True)

    characteristics["year"] = year
    characteristics["date"] = pd.to_datetime(
        {
            "year": year,
            "month": pd.to_numeric(characteristics["mois"], errors="coerce"),
            "day": pd.to_numeric(characteristics["jour"], errors="coerce"),
        },
        errors="coerce",
    )
    time_text = characteristics["hrmn"].astype("string").str.replace(":", "", regex=False).str.zfill(4)
    characteristics["hour"] = pd.to_numeric(time_text.str[:2], errors="coerce").fillna(0).astype("int8")
    characteristics["latitude"] = clean_coordinates(characteristics["lat"])
    characteristics["longitude"] = clean_coordinates(characteristics["long"])
    characteristics.loc[~characteristics["latitude"].between(-25, 55), "latitude"] = pd.NA
    characteristics.loc[~characteristics["longitude"].between(-65, 60), "longitude"] = pd.NA
    characteristics["department"] = normalize_department(characteristics["dep"])
    characteristics["environment"] = characteristics["agg"].map({1: "Hors agglomération", 2: "En agglomération"}).fillna("Non renseigné")
    characteristics["light"] = characteristics["lum"].map(LIGHT_LABELS).fillna("Non renseigné")
    characteristics["weather"] = characteristics["atm"].map(WEATHER_LABELS).fillna("Non renseigné")
    characteristics["weekday"] = characteristics["date"].dt.dayofweek.map(WEEKDAYS)

    locations["road_type"] = locations["catr"].map(ROAD_LABELS).fillna("Non renseigné")
    # Un accident peut concerner plusieurs voies, notamment aux intersections.
    locations = locations.groupby("accident_id", as_index=False).agg(
        road_type=("road_type", lambda values: " / ".join(sorted(set(values))))
    )
    accident_base = characteristics[
        [
            "accident_id",
            "year",
            "date",
            "hour",
            "weekday",
            "department",
            "environment",
            "light",
            "weather",
            "latitude",
            "longitude",
        ]
    ].merge(locations[["accident_id", "road_type"]], on="accident_id", how="left", validate="one_to_one")

    vehicle_columns = ["accident_id", "id_vehicule", "num_veh", "catv"]
    vehicles = vehicles[[column for column in vehicle_columns if column in vehicles.columns]].copy()
    vehicles["vehicle_type"] = vehicles["catv"].map(VEHICLE_LABELS).fillna("Autre véhicule")

    user_columns = ["accident_id", "id_usager", "id_vehicule", "num_veh", "catu", "grav", "sexe", "an_nais"]
    users = users[[column for column in user_columns if column in users.columns]].copy()
    if "id_usager" not in users:
        users["id_usager"] = users.index.astype(str) + f"-{year}"
    join_keys = [key for key in ["accident_id", "id_vehicule", "num_veh"] if key in users and key in vehicles]
    users = users.merge(
        vehicles[join_keys + ["vehicle_type"]].drop_duplicates(join_keys),
        on=join_keys,
        how="left",
        validate="many_to_one",
    )
    users = users.merge(accident_base, on="accident_id", how="left", validate="many_to_one")
    users.rename(columns={"id_usager": "user_id"}, inplace=True)
    users["gravity_code"] = pd.to_numeric(users["grav"], errors="coerce").astype("Int8")
    users["gravity"] = users["gravity_code"].map(GRAVITY_LABELS).fillna("Non renseigné")
    users["user_type"] = users["catu"].map(USER_LABELS).fillna("Autre")
    users["sex"] = users["sexe"].map({1: "Homme", 2: "Femme"}).fillna("Non renseigné")
    users["age"] = year - pd.to_numeric(users["an_nais"], errors="coerce")
    users.loc[~users["age"].between(0, 110), "age"] = pd.NA
    users["age_group"] = age_group(users["age"])
    users["is_victim"] = users["gravity_code"].isin([2, 3, 4])
    users["is_serious"] = users["gravity_code"].isin([2, 3])
    users["is_killed"] = users["gravity_code"].eq(2)

    severity = (
        users.groupby("accident_id", as_index=False)
        .agg(
            people=("user_id", "count"),
            victims=("is_victim", "sum"),
            serious=("is_serious", "sum"),
            killed=("is_killed", "sum"),
        )
    )
    severity["accident_severity"] = "Blessé léger"
    severity.loc[severity["serious"] > 0, "accident_severity"] = "Blessé hospitalisé"
    severity.loc[severity["killed"] > 0, "accident_severity"] = "Tué"
    accidents = accident_base.merge(severity, on="accident_id", how="left", validate="one_to_one")

    users = users[users["is_victim"]].copy()
    return accidents, users


def build_quality(accidents: pd.DataFrame, users: pd.DataFrame) -> dict:
    return {
        "years": [int(accidents["year"].min()), int(accidents["year"].max())],
        "accidents": int(len(accidents)),
        "victims": int(len(users)),
        "duplicate_accident_ids": int(accidents["accident_id"].duplicated().sum()),
        "duplicate_user_ids": int(users["user_id"].duplicated().sum()),
        "coordinate_coverage_pct": round(100 * accidents[["latitude", "longitude"]].notna().all(axis=1).mean(), 2),
        "missing_age_pct": round(100 * users["age"].isna().mean(), 2),
        "missing_vehicle_pct": round(100 * users["vehicle_type"].isna().mean(), 2),
        "validation": {
            "one_row_per_accident": bool(accidents["accident_id"].is_unique),
            "valid_dates": bool(accidents["date"].notna().all()),
            "valid_gravity": bool(users["gravity_code"].isin([2, 3, 4]).all()),
        },
    }


def main() -> None:
    yearly = [load_year(year) for year in YEARS]
    accidents = pd.concat([item[0] for item in yearly], ignore_index=True)
    users = pd.concat([item[1] for item in yearly], ignore_index=True)

    if not accidents["accident_id"].is_unique:
        raise ValueError("Les identifiants d'accident ne sont pas uniques.")
    if not users["gravity_code"].isin([2, 3, 4]).all():
        raise ValueError("Une gravité inattendue est présente parmi les victimes.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    accidents.to_parquet(ACCIDENTS_PATH, index=False, compression="zstd")
    users.to_parquet(USERS_PATH, index=False, compression="zstd")
    QUALITY_PATH.write_text(
        json.dumps(build_quality(accidents, users), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"{len(accidents):,} accidents et {len(users):,} victimes préparés.")


if __name__ == "__main__":
    main()

