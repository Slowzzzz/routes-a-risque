"""Vérifier le parcours Streamlit avec les données réellement livrées."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_filters_and_comparison_views():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=45).run()
    assert not app.exception
    assert app.metric[0].value == "221 044"
    assert app.metric[1].value == "291 375"

    app.radio(key="ranking_mode").set_value("Part de tués ou hospitalisés")
    app.radio(key="time_measure").set_value("Avec tué")
    app.multiselect[0].set_value(["75"])
    app.multiselect[2].set_value(["Piéton"])
    app.run()
    assert not app.exception
    assert 0 < int(app.metric[1].value.replace(" ", "")) < 291375

    app.multiselect[2].set_value([]).run()
    assert not app.exception
    assert any("Aucune donnée" in warning.value for warning in app.warning)
