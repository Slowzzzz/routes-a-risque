import pandas as pd

from utils.viz import monthly_trend, severity_by_user, weekday_hour_heatmap


def test_heatmap_fills_days_absent_from_selection():
    accidents = pd.DataFrame({"weekday": ["Lundi", "Lundi"], "hour": [8, 8]})
    figure = weekday_hour_heatmap(accidents)
    values = figure.data[0].z
    assert values.shape == (7, 24)
    assert values[0, 8] == 2
    assert pd.notna(values).all()
    assert values.sum() == 2


def test_severe_heatmap_counts_accidents_once_and_handles_no_deaths():
    accidents = pd.DataFrame({
        "weekday": ["Lundi", "Mardi"], "hour": [8, 9],
        "serious": [3, 0], "killed": [0, 0],
    })
    severe = weekday_hour_heatmap(accidents, "Avec tué ou hospitalisé").data[0].z
    assert severe.sum() == 1
    assert severe[0, 8] == 1
    fatal = weekday_hour_heatmap(accidents, "Avec tué").data[0].z
    assert fatal.shape == (7, 24)
    assert fatal.sum() == 0


def test_user_proportions_sum_to_100_despite_different_group_sizes():
    users = pd.DataFrame({
        "user_type": ["Conducteur"] * 3 + ["Piéton"],
        "gravity": ["Tué", "Blessé léger", "Blessé léger", "Blessé hospitalisé"],
    })
    figure = severity_by_user(users)
    totals = {}
    for trace in figure.data:
        for category, value in zip(trace.x, trace.y):
            totals[category] = totals.get(category, 0) + value
    assert all(abs(value - 100) < 0.00001 for value in totals.values())
    assert sum(sum(trace.y) for trace in severity_by_user(users, False).data) == 4


def test_monthly_trend_preserves_zero_months_and_selected_years():
    users = pd.DataFrame({
        "date": pd.to_datetime(["2024-02-01", "2024-04-01"]),
        "user_id": [1, 2], "is_serious": [True, False],
    })
    figure = monthly_trend(users, (2023, 2024))
    victims = figure.data[0]
    assert len(victims.x) == 24
    assert sum(victims.y) == 2
    assert victims.y[12] == 0
    assert victims.y[13] == 1
    assert victims.y[14] == 0


def test_heatmap_excludes_unknown_hours_instead_of_counting_midnight():
    accidents = pd.DataFrame({"weekday": ["Lundi", "Lundi"], "hour": pd.Series([0, None], dtype="Int8")})
    values = weekday_hour_heatmap(accidents).data[0].z
    assert values[0, 0] == 1
    assert values.sum() == 1
