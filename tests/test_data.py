import pandas as pd

from utils.data import filter_data, safe_rate


def sample_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    accidents = pd.DataFrame(
        {
            "accident_id": [1, 2, 3],
            "year": [2022, 2023, 2024],
            "department": ["75", "75", "69"],
            "environment": ["En agglomération", "Hors agglomération", "En agglomération"],
        }
    )
    users = pd.DataFrame(
        {
            "accident_id": [1, 1, 2, 3],
            "user_type": ["Conducteur", "Passager", "Piéton", "Conducteur"],
            "is_serious": [True, False, True, False],
            "is_killed": [True, False, False, False],
        }
    )
    return accidents, users


def test_filter_data_combines_filters_without_double_counting() -> None:
    accidents, users = sample_frames()
    filtered_accidents, filtered_users = filter_data(
        accidents,
        users,
        (2022, 2024),
        ["75"],
        ["En agglomération"],
        ["Passager"],
    )
    assert filtered_accidents["accident_id"].tolist() == [1]
    assert filtered_users["user_type"].tolist() == ["Passager"]


def test_safe_rate_handles_zero_denominator() -> None:
    assert safe_rate(4, 8) == 50
    assert safe_rate(1, 0) == 0


def test_user_filter_recalculates_map_severity_from_selected_victims() -> None:
    accidents, users = sample_frames()
    selected, victims = filter_data(
        accidents, users, (2022, 2024), [], ["En agglomération"], ["Passager"]
    )
    assert len(victims) == 1
    assert selected["accident_severity"].tolist() == ["Blessé léger"]
    assert selected["killed"].sum() == 0
    assert selected["serious"].sum() == 0
    assert selected["victims"].sum() == 1


def test_clearing_user_or_environment_filter_selects_nothing() -> None:
    accidents, users = sample_frames()
    for environments, categories in [([], ["Passager"]), (["En agglomération"], [])]:
        selected, victims = filter_data(accidents, users, (2022, 2024), [], environments, categories)
        assert selected.empty
        assert victims.empty

