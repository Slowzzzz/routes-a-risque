import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import SEVERITY_COLORS, SEVERITY_ORDER

PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "responsive": True,
}


def apply_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        font=dict(family="Arial, sans-serif", color="#152536"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="white", font_size=13),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#DFE7EC", zeroline=False)
    return fig


def monthly_trend(users: pd.DataFrame, years: tuple[int, int] | None = None) -> go.Figure:
    # Garder les mois à zéro : les supprimer relierait artificiellement deux pics.
    monthly = (
        users.assign(month=users["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")
        .agg(victims=("user_id", "count"), serious=("is_serious", "sum"))
    )
    start = pd.Timestamp(years[0], 1, 1) if years else monthly.index.min()
    end = pd.Timestamp(years[1], 12, 1) if years else monthly.index.max()
    monthly = monthly.reindex(pd.date_range(start, end, freq="MS"), fill_value=0)
    monthly = monthly.rename_axis("month").reset_index()
    long_data = monthly.melt(
        "month",
        value_vars=["victims", "serious"],
        var_name="series",
        value_name="count",
    )
    long_data["series"] = long_data["series"].map(
        {"victims": "Toutes les victimes", "serious": "Tués et hospitalisés"}
    )
    fig = px.line(
        long_data,
        x="month",
        y="count",
        color="series",
        markers=True,
        color_discrete_map={
            "Toutes les victimes": "#277DA1",
            "Tués et hospitalisés": "#D1495B",
        },
        labels={"month": "Mois", "count": "Nombre de personnes", "series": ""},
        title="Évolution mensuelle des victimes",
    )
    fig.update_traces(hovertemplate="%{x|%m/%Y}<br>%{y:,.0f} personnes<extra>%{fullData.name}</extra>")
    fig.update_yaxes(rangemode="tozero")
    return apply_layout(fig)


def accident_map(accidents: pd.DataFrame, max_points: int = 7000) -> go.Figure:
    mapped = accidents.dropna(subset=["latitude", "longitude"]).copy()
    if len(mapped) > max_points:
        mapped = mapped.sample(max_points, random_state=42)

    fig = px.scatter_map(
        mapped,
        lat="latitude",
        lon="longitude",
        color="accident_severity",
        category_orders={"accident_severity": SEVERITY_ORDER},
        color_discrete_map=SEVERITY_COLORS,
        hover_name="department",
        hover_data={
            "date": "|%d/%m/%Y",
            "hour": True,
            "road_type": True,
            "weather": True,
            "latitude": False,
            "longitude": False,
        },
        labels={
            "department": "Département",
            "accident_severity": "Gravité maximale",
            "date": "Date",
            "hour": "Heure",
            "road_type": "Route",
            "weather": "Météo",
        },
        zoom=4.2,
        center={"lat": 46.6, "lon": 2.4},
        title="Localisation des accidents filtrés",
    )
    # Centrer sur la sélection, y compris un département ultramarin isolé.
    if not mapped.empty:
        lat_span = mapped["latitude"].max() - mapped["latitude"].min()
        lon_span = mapped["longitude"].max() - mapped["longitude"].min()
        span = max(lat_span, lon_span)
        zoom = max(0, min(10, math.log2(360 / max(span, 0.1)) - 0.8))
        fig.update_layout(map_center={
            "lat": float((mapped["latitude"].min() + mapped["latitude"].max()) / 2),
            "lon": float((mapped["longitude"].min() + mapped["longitude"].max()) / 2),
        }, map_zoom=zoom)
    fig.update_layout(map_style="carto-positron", legend=dict(orientation="h", y=-0.05, x=0))
    return apply_layout(fig, height=560)


def weekday_hour_heatmap(accidents: pd.DataFrame, measure: str = "Tous les accidents") -> go.Figure:
    if measure == "Avec tué ou hospitalisé":
        accidents = accidents[accidents["serious"] > 0]
    elif measure == "Avec tué":
        accidents = accidents[accidents["killed"] > 0]
    day_order = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    table = (
        accidents.groupby(["weekday", "hour"], observed=False)
        .size()
        .unstack(fill_value=0)
        .reindex(day_order, fill_value=0)
        .reindex(columns=range(24), fill_value=0)
    )
    fig = px.imshow(
        table,
        aspect="auto",
        color_continuous_scale=[[0, "#F3F6F8"], [0.45, "#F4A261"], [1, "#7F0000"]],
        labels={"x": "Heure", "y": "Jour", "color": "Accidents"},
        title=f"Jour et heure · {measure.lower()}",
    )
    fig.update_traces(hovertemplate="%{y}, %{x} h<br>%{z:,.0f} accidents<extra></extra>")
    return apply_layout(fig)


def severity_by_user(users: pd.DataFrame, normalized: bool = True) -> go.Figure:
    counts = (
        users.groupby(["user_type", "gravity"], observed=False)
        .size()
        .reset_index(name="count")
    )
    counts["total"] = counts.groupby("user_type")["count"].transform("sum")
    counts["share"] = 100 * counts["count"] / counts["total"]
    fig = px.bar(
        counts,
        x="user_type",
        y="share" if normalized else "count",
        color="gravity",
        category_orders={"gravity": SEVERITY_ORDER},
        color_discrete_map=SEVERITY_COLORS,
        custom_data=["count", "total", "share"],
        labels={"user_type": "Catégorie d'usager", "count": "Personnes", "share": "Part des victimes (%)", "gravity": "Gravité BAAC"},
        title="Comparer les conséquences parmi les victimes enregistrées",
    )
    fig.update_layout(barmode="stack")
    fig.update_traces(hovertemplate="%{x}<br>%{customdata[0]:,.0f} sur %{customdata[1]:,.0f} victimes<br>%{customdata[2]:.1f} %<extra>%{fullData.name}</extra>")
    if normalized:
        fig.update_yaxes(range=[0, 100], ticksuffix=" %")
    return apply_layout(fig)


def department_ranking(
    accidents: pd.DataFrame, users: pd.DataFrame,
    by_rate: bool = False, min_victims: int = 30,
) -> go.Figure:
    victims = users.groupby("department", as_index=False).agg(
        victims=("user_id", "count"), serious=("is_serious", "sum")
    )
    totals = accidents.groupby("department", as_index=False).agg(accidents=("accident_id", "count"))
    ranking = totals.merge(victims, on="department", how="left")
    ranking["serious_rate"] = 100 * ranking["serious"] / ranking["victims"]
    metric = "serious_rate" if by_rate else "victims"
    if by_rate:
        ranking = ranking[ranking["victims"] >= min_victims]
    ranking = ranking.nlargest(12, metric).sort_values(metric)
    fig = px.bar(
        ranking,
        x=metric,
        y="department",
        orientation="h",
        color="serious_rate",
        color_continuous_scale=[[0, "#F3C677"], [1, "#9E2A2B"]],
        labels={
            "victims": "Nombre de victimes",
            "department": "Département",
            "serious_rate": "Tués ou hospitalisés (%)",
        },
        title="Part de tués ou hospitalisés" if by_rate else "Nombre de victimes par département",
        hover_data={"accidents": ":,.0f", "victims": ":,.0f", "serious": ":,.0f", "serious_rate": ":.1f"},
    )
    fig.update_yaxes(type="category")
    if by_rate:
        fig.update_xaxes(range=[0, 100], ticksuffix=" %")
    return apply_layout(fig)

