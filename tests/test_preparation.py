import pandas as pd

from scripts.prepare_data import clean_hours
from utils.constants import ACCIDENTS_PATH


def test_clean_hours_keeps_unknown_or_invalid_times_missing():
    times = pd.Series(["00:00", "23:59", "8:30", None, "", "24:00", "12:60", "inconnu"])
    hours = clean_hours(times)
    assert hours.iloc[:3].tolist() == [0, 23, 8]
    assert hours.iloc[3:].isna().all()


def test_delivered_coordinates_preserve_pacific_territories():
    accidents = pd.read_parquet(ACCIDENTS_PATH)
    pacific = accidents[accidents["department"].isin(["986", "987", "988"])]
    assert len(pacific) == 1685
    assert pacific[["latitude", "longitude"]].notna().all().all()
    assert pacific.groupby("department")["longitude"].median().abs().gt(130).all()
