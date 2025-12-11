# pages/2_Analyse.py
# ------------------------------------------------------------
# Page d'analyse avancée :
#   - Comparaison plusieurs horizons de placement
#   - Sensibilité au taux
#   - Sensibilité aux versements
#
# Utilise Altair pour les visualisations.
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
import altair as alt

from ui.sidebar import display_sidebar
from core.config import get_theme_css, PRIMARY_COLOR, SECONDARY_COLOR, APP_NAME
from core.calculations import calculate_fv


def simulate_series(pv, pmt, rate, horizons):
    """Retourne un DataFrame contenant FV pour plusieurs horizons."""
    rows = []
    for n in horizons:
        fv = calculate_fv(pv, pmt, rate, n)
        rows.append({"Horizon": n, "FV": fv})
    return pd.DataFrame(rows)


def simulate_rate_sensitivity(pv, pmt, n_years, rates):
    """Sensibilité aux taux."""
    rows = []
    for r in rates:
        fv = calculate_fv(pv, pmt, r, n_years)
        rows.append({"Rendement (%)": r, "FV": fv})
    return pd.DataFrame(rows)


def simulate_pmt_sensitivity(pv, rate, n_years, pmt_values):
    """Sensibilité aux versements mensuels."""
    rows = []
    for p in pmt_values:
        fv = calculate_fv(pv, p, rate, n_years)
        rows.append({"Versement Mensuel": p, "FV": fv})
    return pd.DataFrame(rows)


def main():
    st.set_page_config(page_title="Analyse | " + APP_NAME, layout="wide")
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    display_sidebar()

    st.markdown("<h1>Analyse avancée</h1>", unsafe_allow_html=True)

    st.markdown(
        "Cette section permet d’explorer différents scénarios et visualiser "
        "l’impact du temps, du taux ou des versements sur la valeur future."
    )

    st.markdown("---")

    # -------------------------------
    # PARAMÈTRES DE BASE POUR L'ANALYSE
    # -------------------------------
    pv = st.number_input("Montant initial (PV)", value=100_000, step=10_000, format="%d")
    pmt = st.number_input("Versement mensuel (PMT)", value=50_000, step=5_000, format="%d")
    rate = st.number_input("Rendement annuel (%)", value=5.0, step=0.1, format="%.2f")
    n_years = st.number_input("Horizon (années)", value=10, step=1, format="%d")

    st.markdown("---")

    # ============================================================
    # 1) COMPARAISON PAR HORIZON
    # ============================================================
    with st.expander("📊 Comparaison par horizon de placement (5, 10, 15, 20 ans)", expanded=True):

        horizons = [5, 10, 15, 20]
        df = simulate_series(pv, pmt, rate, horizons)

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x="Horizon:O",
                y="FV:Q",
                color=alt.value(PRIMARY_COLOR),
                tooltip=[alt.Tooltip("FV:Q", format=",.0f")],
            )
            .properties(height=350)
        )

        st.altair_chart(chart, use_container_width=True)

    # ============================================================
    # 2) SENSIBILITÉ AUX TAUX
    # ============================================================
    with st.expander("📈 Analyse de sensibilité aux taux (+/- 1%)"):

        rates = [rate - 1, rate, rate + 1, rate + 2]
        rates = [r for r in rates if r > 0]
        df_r = simulate_rate_sensitivity(pv, pmt, n_years, rates)

        chart_r = (
            alt.Chart(df_r)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x="Rendement (%):Q",
                y="FV:Q",
                color=alt.value(SECONDARY_COLOR),
                tooltip=[
                    alt.Tooltip("Rendement (%):Q"),
                    alt.Tooltip("FV:Q", format=",.0f"),
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_r.interactive(), use_container_width=True)

    # ============================================================
    # 3) SENSIBILITÉ AUX VERSEMENTS
    # ============================================================
    with st.expander("💵 Sensibilité aux versements mensuels (PMT)"):

        pmt_values = [pmt * x for x in [0.5, 1, 1.5, 2]]
        df_p = simulate_pmt_sensitivity(pv, rate, n_years, pmt_values)

        chart_p = (
            alt.Chart(df_p)
            .mark_bar()
            .encode(
                x="Versement Mensuel:O",
                y="FV:Q",
                color=alt.value(PRIMARY_COLOR),
                tooltip=[alt.Tooltip("FV:Q", format=",.0f")],
            )
            .properties(height=350)
        )

        st.altair_chart(chart_p, use_container_width=True)


if __name__ == "__main__":
    main()
