from pathlib import Path

import pandas as pd
import streamlit as st

from utils.constants import DATASET_PAGE

from utils.data import filter_data, load_data, safe_rate
from utils.viz import (
    PLOTLY_CONFIG,
    accident_map,
    department_ranking,
    monthly_trend,
    severity_by_user,
    weekday_hour_heatmap,
)

ONISR_BILAN = "https://www.onisr.securite-routiere.gouv.fr/etat-de-linsecurite-routiere/bilans-annuels-de-la-securite-routiere/bilan-2024-de-la-securite-routiere"
CEREMA_BILAN = "https://www.cerema.fr/fr/activites/mobilites/chiffres-cles"
CONSEILS = "https://www.masecurite.interieur.gouv.fr/fr/fiches-pratiques/securite-routiere-et-transport/regles-bonne-conduite-route"


def number(value: int | float) -> str:
    return f"{value:,.0f}".replace(",", " ")


st.set_page_config(
    page_title="Routes à risque | BAAC 2021–2024",
    page_icon="🚦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1240px; padding-top: 2rem;}
    [data-testid="stMetric"] {background:#F3F6F8; border-left:4px solid #D1495B; padding:1rem; border-radius:.4rem;}
    .story-card {background:#F3F6F8; border-radius:.6rem; padding:1rem 1.2rem; margin:.5rem 0 1rem 0;}
    .small-note {color:#536878; font-size:.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def prepare_options(accidents: pd.DataFrame, users: pd.DataFrame) -> dict:
    return {
        "departments": sorted(accidents["department"].dropna().unique().tolist()),
        "environments": sorted(accidents["environment"].dropna().unique().tolist()),
        "user_types": sorted(users["user_type"].dropna().unique().tolist()),
    }


try:
    accidents, users, quality = load_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

options = prepare_options(accidents, users)

with st.sidebar:
    st.image(str(Path(__file__).resolve().parent / "assets" / "efrei-logo.png"), width=220)
    st.subheader("Gabriel Geniez")
    st.markdown("INGE-2 Data Engineering  \n2026-2027 · Promo 2028")
    st.markdown("[gabriel.geniez@efrei.net](mailto:gabriel.geniez@efrei.net)")
    st.markdown(
        "[LinkedIn](https://www.linkedin.com/in/gabriel-geniez-670029292/) · "
        "[GitHub](https://github.com/Slowzzzz)"
    )
    st.markdown("**Course Name**  \nData Analysis & Visualization")
    st.markdown("**Project proposed :** Prof. Mano Mathew")
    st.markdown("[LinkedIn](https://www.linkedin.com/in/manomathew/)")
    st.divider()
    st.header("Explorer les données")
    year_range = st.slider(
        "Période",
        int(accidents["year"].min()),
        int(accidents["year"].max()),
        (int(accidents["year"].min()), int(accidents["year"].max())),
    )
    selected_departments = st.multiselect(
        "Départements",
        options["departments"],
        help="Laissez vide pour conserver toute la France.",
    )
    selected_environments = st.multiselect(
        "Environnement",
        options["environments"],
        default=options["environments"],
    )
    selected_users = st.multiselect(
        "Catégories d'usagers",
        options["user_types"],
        default=options["user_types"],
    )
    st.divider()
    st.caption(
        "Départements vide = France entière. Environnement ou catégories vide = aucune donnée. "
        "Tous les graphiques décrivent les victimes sélectionnées et les accidents qui les concernent."
    )

filtered_accidents, filtered_users = filter_data(
    accidents,
    users,
    year_range,
    selected_departments,
    selected_environments,
    selected_users,
)

st.title("🚦 Routes à risque")
st.subheader("Comprendre les accidents pour mieux prévenir leurs conséquences")
st.markdown(
    """
    <div class="story-card">
    <strong>Où agir, quand sensibiliser, qui protéger ?</strong>
    Pour les collectivités et acteurs de la sécurité routière, ce parcours relie les accidents
    enregistrés entre 2021 et 2024 à des priorités de prévention : suivre les conséquences humaines,
    distinguer les concentrations de victimes de la gravité, puis préparer un diagnostic local.
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Gabriel Geniez — étudiant 20231128 · Source : Ministère de l’Intérieur, "
    "fichier BAAC 2021–2024 · Licence Ouverte 2.0"
)
st.info(
    "**Le point de départ : des vies à protéger.** En 2024, le bilan définitif compte "
    "3 432 personnes tuées sur les routes : 3 193 en métropole et 239 en outre-mer. "
    "Le Cerema rappelle l’objectif de réduire de moitié les tués et blessés graves entre 2019 et 2030. "
    f"[Repères officiels 2024 — Cerema]({CEREMA_BILAN}). "
    "Ce repère national est fixe ; les indicateurs ci-dessous suivent vos filtres."
)

if filtered_accidents.empty or filtered_users.empty:
    st.warning("Aucune donnée ne correspond à cette combinaison de filtres.")
    st.stop()

victim_count = len(filtered_users)
serious_count = int(filtered_users["is_serious"].sum())
killed_count = int(filtered_users["is_killed"].sum())
latest_year = int(filtered_users["year"].max())
previous_year = latest_year - 1
latest_victims = int((filtered_users["year"] == latest_year).sum())
previous_victims = int((filtered_users["year"] == previous_year).sum())
delta = safe_rate(latest_victims - previous_victims, previous_victims)
victim_delta = (
    f"{delta:+.2f}% en {latest_year} vs {previous_year}"
    if previous_victims > 0
    else None
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Accidents corporels", f"{len(filtered_accidents):,}".replace(",", " "))
kpi2.metric("Victimes", f"{victim_count:,}".replace(",", " "), victim_delta, delta_color="inverse")
kpi3.metric("Tués", f"{killed_count:,}".replace(",", " "))
kpi4.metric("Tués ou hospitalisés", f"{safe_rate(serious_count, victim_count):.1f}%", help="Nombre de tués et blessés hospitalisés divisé par le nombre de victimes sélectionnées.")
st.caption(
    "Victimes = personnes tuées ou blessées, hors indemnes. Tués ou hospitalisés = codes BAAC 2 et 3. "
    "Ce regroupement ne correspond pas aux blessés graves au sens médical MAIS3+ estimés par l’ONISR. "
    "La carte et la heatmap comptent chaque accident une seule fois."
)

st.divider()
st.header("1. Suivre les vies touchées, au-delà du nombre d’accidents")
st.markdown(
    "**Pourquoi cette courbe ?** Elle montre l’évolution du bilan humain mois par mois et aide à "
    "repérer les périodes à examiner avant de programmer une campagne de prévention. "
    "L’axe horizontal représente les mois, l’axe vertical le nombre de personnes. "
    "La seconde courbe isole les tués et hospitalisés au sein de toutes les victimes."
)
peak = (
    filtered_users.assign(month=filtered_users["date"].dt.to_period("M"))
    .groupby("month")
    .size()
    .idxmax()
)
st.markdown(f"**Dans votre sélection —** Le mois comptant le plus de victimes est **{peak.month:02d}/{peak.year}**.")
st.plotly_chart(monthly_trend(filtered_users, year_range), use_container_width=True, config=PLOTLY_CONFIG)
annual = filtered_users.groupby("year").agg(
    victims=("user_id", "size"), serious=("is_serious", "sum"), killed=("is_killed", "sum")
)
if latest_year in annual.index and previous_year in annual.index:
    previous_killed = int(annual.loc[previous_year, "killed"])
    latest_killed = int(annual.loc[latest_year, "killed"])
    st.markdown(
        f"Entre **{previous_year} et {latest_year}**, les victimes passent de "
        f"**{number(previous_victims)} à {number(latest_victims)}** ({delta:+.2f} %), "
        f"et les personnes tuées de **{number(previous_killed)} à {number(latest_killed)}** "
        f"({latest_killed - previous_killed:+d}). **Le volume et les conséquences doivent être suivis ensemble.**"
    )
else:
    st.caption("Sélectionnez au moins deux années consécutives pour comparer leur bilan humain.")
st.caption(
    "Les deux courbes se recouvrent : les tués et hospitalisés font partie de toutes les victimes. "
    "Un pic mensuel ne suffit pas à établir une saisonnalité ; les déplacements et le contexte de 2021 "
    "peuvent aussi modifier les volumes observés."
)

st.header("2. Localiser les besoins : volume et gravité ne racontent pas la même chose")
st.markdown(
    "**Pourquoi une carte et un classement ?** La carte situe les accidents pour préparer un "
    "diagnostic de terrain ; chaque point représente un accident et sa couleur indique la "
    "conséquence la plus sévère parmi les victimes sélectionnées. Le classement compare les "
    "départements : les volumes situent les besoins, les proportions décrivent les conséquences "
    "parmi les victimes. Ces deux lectures peuvent conduire à des priorités différentes."
)
valid_coordinates = filtered_accidents[["latitude", "longitude"]].notna().all(axis=1).sum()
st.markdown(
    f"**Dans votre sélection —** **{number(valid_coordinates)} accidents** disposent de coordonnées. "
    "La carte en affiche au maximum 7 000 ; les indicateurs utilisent toute la sélection."
)
map_col, rank_col = st.columns([1.35, 1])
with map_col:
    if valid_coordinates:
        st.plotly_chart(accident_map(filtered_accidents), use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.info("Aucune coordonnée disponible dans cette sélection. Les autres analyses restent disponibles.")
with rank_col:
    ranking_mode = st.radio(
        "Comparer les départements par", ["Nombre de victimes", "Part de tués ou hospitalisés"],
        key="ranking_mode",
    )
    by_rate = ranking_mode == "Part de tués ou hospitalisés"
    min_victims = st.number_input(
        "Minimum de victimes pour comparer les proportions", min_value=1, value=30,
        disabled=not by_rate,
        help="Seuil de lecture, pas un test statistique : les petits effectifs donnent des proportions instables.",
    )
    if by_rate and not (filtered_users.groupby("department").size() >= min_victims).any():
        st.info("Aucun département n’atteint ce minimum. Réduisez le seuil ou élargissez la sélection.")
    st.plotly_chart(
        department_ranking(filtered_accidents, filtered_users, by_rate, int(min_victims)),
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )
st.caption(
    "Carte : conséquence la plus sévère parmi les victimes sélectionnées dans chaque accident. "
    "Exemple : avec le filtre piétons, un décès de conducteur ne colore pas en rouge un accident "
    "où le piéton est légèrement blessé. Le classement affiche au plus 12 départements ; "
    "une proportion élevée parmi les victimes n’est pas un taux de risque pour les habitants."
)
environment = filtered_users.groupby("environment").agg(
    victims=("user_id", "size"), serious=("is_serious", "sum"), killed=("is_killed", "sum")
)
environment["share"] = 100 * environment["serious"] / environment["victims"]
st.markdown("**Avant de choisir une action, comparer aussi les milieux de circulation.**")
if len(environment) > 1:
    high_environment = environment["share"].idxmax()
    low_environment = environment["share"].idxmin()
    st.markdown(
        f"La part de tués ou hospitalisés parmi les victimes est de "
        f"**{environment.loc[high_environment, 'share']:.1f} % {high_environment.lower()}**, "
        f"contre **{environment.loc[low_environment, 'share']:.1f} % {low_environment.lower()}**. "
        "Une concentration de victimes et une forte proportion de conséquences sévères "
        "peuvent donc appeler des diagnostics différents."
    )
st.dataframe(
    environment.rename(columns={"victims": "Victimes", "serious": "Tués ou hospitalisés", "killed": "Tués", "share": "Tués ou hospitalisés (%)"})
    .rename_axis("Milieu").round(1),
    use_container_width=True,
)
st.caption(
    "Lecture du tableau : « Tués » est inclus dans « Tués ou hospitalisés », lui-même inclus dans "
    "« Victimes » ; ces colonnes ne s’additionnent pas. Le pourcentage rapporte les tués et "
    "hospitalisés aux victimes du même milieu. Cette comparaison aide à adapter le diagnostic "
    "aux routes en agglomération et hors agglomération, sans attribuer une cause au milieu."
)

st.header("3. Choisir les moments de prévention selon les conséquences observées")
st.markdown(
    "**Pourquoi cette carte de chaleur ?** Chaque case cumule les accidents d’un jour de semaine "
    "et d’une tranche d’une heure sur toute la période sélectionnée. Une case plus foncée indique "
    "un effectif plus élevé. Passer de tous les accidents à ceux avec tué ou hospitalisé permet "
    "de vérifier si les créneaux les plus fréquents sont aussi ceux à examiner pour leurs conséquences."
)
time_measure = st.radio(
    "Accidents représentés dans la heatmap",
    ["Tous les accidents", "Avec tué ou hospitalisé", "Avec tué"], horizontal=True,
    key="time_measure",
)
time_accidents = filtered_accidents
if time_measure == "Avec tué ou hospitalisé":
    time_accidents = time_accidents[time_accidents["serious"] > 0]
elif time_measure == "Avec tué":
    time_accidents = time_accidents[time_accidents["killed"] > 0]
known_time_accidents = time_accidents.dropna(subset=["weekday", "hour"])
if not known_time_accidents.empty:
    slots = known_time_accidents.groupby(["weekday", "hour"]).size()
    peak_day, peak_hour = slots.idxmax()
    st.markdown(
        f"**Dans votre sélection —** Pour « {time_measure.lower()} », le créneau le plus fréquent "
        f"est **{peak_day.lower()}, {peak_hour} h–{peak_hour + 1} h**, avec **{number(slots.max())} accidents** "
        "cumulés sur la période (premier créneau en cas d’égalité)."
    )
else:
    st.info("Aucun accident avec jour et heure connus ne correspond à cette sélection.")
st.plotly_chart(weekday_hour_heatmap(filtered_accidents, time_measure), use_container_width=True, config=PLOTLY_CONFIG)
st.caption(
    "La couleur mesure un nombre d’accidents, sans correction du trafic. L’échelle se recalcule "
    "à chaque sélection : comparez les valeurs, pas les couleurs entre deux vues. "
    "Un créneau fréquent justifie une observation locale, sans démontrer un effet de l’obscurité ou de la fatigue."
)
st.caption(
    f"Heures manquantes : {number(time_accidents['hour'].isna().sum())} accidents exclus de cette "
    "carte de chaleur, mais conservés dans les autres indicateurs."
)

st.header("4. Adapter la prévention aux personnes touchées")
st.markdown(
    "**Pourquoi des barres empilées ?** Chaque barre représente une catégorie de victimes, "
    "répartie selon les trois niveaux de gravité BAAC. En proportions, les barres totalisent "
    "100 % et permettent de comparer des groupes de tailles différentes. En effectifs, elles "
    "montrent combien de personnes sont concernées pour dimensionner la prévention."
)
group_rates = filtered_users.groupby("user_type").agg(victims=("user_id", "count"), serious=("is_serious", "sum"))
group_rates["rate"] = 100 * group_rates["serious"] / group_rates["victims"]
highest_share = group_rates["rate"].idxmax()
st.markdown(
    f"**Dans votre sélection —** La catégorie **{highest_share.lower()}** présente la plus forte part "
    f"de tués ou hospitalisés : **{group_rates.loc[highest_share, 'rate']:.1f} %** "
    f"sur **{number(group_rates.loc[highest_share, 'victims'])} victimes** "
    "(première catégorie en cas d’égalité)."
)
user_view = st.radio("Lecture des catégories", ["Proportions (%)", "Effectifs"], horizontal=True)
st.plotly_chart(severity_by_user(filtered_users, user_view == "Proportions (%)"), use_container_width=True, config=PLOTLY_CONFIG)
st.caption(
    "Survolez les barres pour lire le pourcentage et son effectif. Conducteur, passager et piéton "
    "décrivent le rôle dans l’accident. Les publications ONISR distinguent aussi les modes "
    "(vélo, deux-roues motorisé, voiture…) : ces catégories ne sont pas interchangeables. "
    "La part parmi les victimes ne mesure pas le risque de se déplacer à pied ou de conduire."
)
if group_rates["victims"].min() < 30:
    st.warning("Au moins une catégorie compte moins de 30 victimes : interprétez ses proportions avec prudence.")

st.header("5. Passer du constat à un plan de prévention")
st.markdown(
    "**Une concentration observée sert à choisir où approfondir le diagnostic.** "
    "Les actions suivantes sont des pistes à discuter avec les acteurs locaux ; "
    "leur efficacité n’est pas estimée par ce dashboard."
)
priority_department = filtered_users.groupby("department").size().idxmax()
st.table(pd.DataFrame([
    {
        "Constat dans la sélection": f"Le département {priority_department} compte le plus de victimes (premier en cas d’égalité).",
        "Diagnostic à mener": "Comparer volume et proportions, puis examiner les lieux et les flux de circulation.",
        "Piste de prévention": "Avec la collectivité, examiner les vitesses pratiquées et les possibilités de sécuriser les traversées.",
        "Suivi à prévoir": "Victimes et tués/hospitalisés sur le secteur, avec données de trafic et comparaison temporelle.",
    },
    {
        "Constat dans la sélection": f"{highest_share} : {group_rates.loc[highest_share, 'rate']:.1f} % de tués ou hospitalisés parmi les victimes.",
        "Diagnostic à mener": "Examiner les âges, modes de déplacement et circonstances avant de cibler une campagne.",
        "Piste de prévention": "Adapter les messages : attention aux traversées, visibilité, vitesse adaptée et vigilance partagée.",
        "Suivi à prévoir": "Effectifs et proportion de tués/hospitalisés pour le public concerné, avant et après l’action.",
    },
    {
        "Constat dans la sélection": "La heatmap distingue les créneaux fréquents selon la gravité choisie.",
        "Diagnostic à mener": "Observer ces créneaux sur le terrain ; vérifier les déplacements, l’éclairage et les usages.",
        "Piste de prévention": "Programmer sensibilisation et observations locales aux moments identifiés.",
        "Suivi à prévoir": "Accidents par créneau sur des périodes comparables ; une baisse seule ne prouve pas l’effet de l’action.",
    },
]).set_index("Constat dans la sélection"))
st.markdown(
    "**Les gestes de prévention à relayer.** Le ministère de l’Intérieur recommande "
    "d’adapter l’allure aux conditions de circulation, de rester vigilant lorsque la visibilité "
    "diminue et de prévoir des pauses régulières sur les longs trajets. "
    f"[Conseils nationaux — Ma Sécurité, ministère de l’Intérieur]({CONSEILS})."
)
st.warning(
    "**Ce que l’analyse ne démontre pas.** Les associations observées ne prouvent pas une cause. "
    "Les données couvrent les accidents corporels connus des forces de l’ordre, sans exposition "
    "au trafic. Ce dashboard n’établit ni responsabilité, ni effet causal de la vitesse, de l’alcool "
    "ou d’une action de prévention. Pour évaluer une action, il faut un protocole et des données complémentaires."
)

with st.expander("Sources officielles et différences de périmètre"):
    st.markdown(
        f"- [BAAC : fichiers ouverts utilisés pour les calculs 2021–2024]({DATASET_PAGE}).\n"
        f"- [ONISR : bilan définitif 2024, analyses par territoires et modes de déplacement]({ONISR_BILAN}).\n"
        f"- [Cerema : repères nationaux 2024 et objectif 2030]({CEREMA_BILAN}).\n"
        f"- [Ministère de l’Intérieur : conseils de conduite]({CONSEILS})."
    )
    st.markdown(
        "**Comment lire les écarts avec les publications ?** Le dashboard compte les victimes "
        "enregistrées dans les fichiers BAAC, en métropole et dans les territoires ultramarins présents "
        "dans ces fichiers. Certaines publications portent sur la métropole seule ou utilisent des "
        "estimations du nombre de blessés et de blessés graves (MAIS3+), complétées par des données "
        "médicales. Ces estimations ne se comparent pas directement aux blessés hospitalisés du BAAC. "
        "Les repères officiels cités sont ceux de 2024, pas un bilan des années suivantes. "
        "Sources vérifiées le 24 octobre 2026."
    )

with st.expander("Qualité des données et méthode", expanded=False):
    st.caption("Ces contrôles portent sur l’ensemble des fichiers préparés, avant les filtres.")
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Accidents source", f"{quality['accidents']:,}".replace(",", " "))
    q2.metric("Coordonnées disponibles", f"{quality['coordinate_coverage_pct']:.1f}%")
    q3.metric("Âges manquants", f"{quality['missing_age_pct']:.1f}%")
    q4.metric("Doublons accident", quality["duplicate_accident_ids"])
    st.caption(
        f"Heures manquantes : {quality['missing_hour_pct']:.2f} %. "
        "Elles sont exclues des analyses horaires, sans être remplacées par minuit. "
        "Les coordonnées manquantes excluent uniquement les points de la carte."
    )
    st.markdown(
        "Les quatre fichiers annuels — caractéristiques, lieux, véhicules et usagers — sont téléchargés "
        "depuis data.gouv.fr, normalisés puis reliés par leurs identifiants. Les KPIs d'accidents reposent "
        "sur une table à une ligne par accident afin d'éviter le double comptage lié aux multiples usagers."
    )
    st.json(quality["validation"], expanded=False)

download_columns = [
    "date",
    "department",
    "environment",
    "user_type",
    "gravity",
    "age_group",
    "vehicle_type",
]
st.download_button(
    "Télécharger les victimes filtrées (CSV)",
    filtered_users[download_columns].to_csv(index=False).encode("utf-8-sig"),
    file_name="baac_victimes_filtrees.csv",
    mime="text/csv",
)

st.divider()
st.markdown(
    f"[Consulter le jeu de données officiel]({DATASET_PAGE}) · "
    "Analyse descriptive réalisée dans un objectif pédagogique."
)

