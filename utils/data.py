import json

import pandas as pd
import streamlit as st

from utils.constants import ACCIDENTS_PATH, QUALITY_PATH, USERS_PATH


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    if not ACCIDENTS_PATH.exists() or not USERS_PATH.exists():
        raise FileNotFoundError(
            "Les données préparées sont absentes. Exécutez "
            "`python scripts/prepare_data.py`."
        )

    accidents = pd.read_parquet(ACCIDENTS_PATH)
    users = pd.read_parquet(USERS_PATH)
    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    accidents["date"] = pd.to_datetime(accidents["date"])
    users["date"] = pd.to_datetime(users["date"])
    return accidents, users, quality


def filter_data(
    accidents: pd.DataFrame,
    users: pd.DataFrame,
    years: tuple[int, int],
    departments: list[str],
    environments: list[str],
    user_types: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    accident_mask = accidents["year"].between(years[0], years[1])
    if departments:
        accident_mask &= accidents["department"].isin(departments)
    accident_mask &= accidents["environment"].isin(environments)

    filtered_accidents = accidents.loc[accident_mask].copy()
    filtered_users = users[users["accident_id"].isin(filtered_accidents["accident_id"])]
    filtered_users = filtered_users[filtered_users["user_type"].isin(user_types)]
    filtered_accidents = filtered_accidents[
        filtered_accidents["accident_id"].isin(filtered_users["accident_id"])
    ].copy()
    # La carte et les indicateurs doivent décrire les mêmes victimes sélectionnées.
    outcomes = filtered_users.groupby("accident_id").agg(
        victims=("user_type", "size"),
        serious=("is_serious", "sum"),
        killed=("is_killed", "sum"),
    )
    for column in ("victims", "serious", "killed"):
        filtered_accidents[column] = filtered_accidents["accident_id"].map(outcomes[column])
    filtered_accidents["accident_severity"] = "Blessé léger"
    filtered_accidents.loc[filtered_accidents["serious"] > 0, "accident_severity"] = "Blessé hospitalisé"
    filtered_accidents.loc[filtered_accidents["killed"] > 0, "accident_severity"] = "Tué"
    return filtered_accidents, filtered_users.copy()


def safe_rate(numerator: int | float, denominator: int | float) -> float:
    return 100 * numerator / denominator if denominator else 0.0

