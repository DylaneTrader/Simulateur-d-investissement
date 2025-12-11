# ui/charts.py
# ---------------------------------------------------------
# Graphiques en Altair pour :
# - Évolution mensuelle du portefeuille
# - Histogramme annuel (Capital Investi vs Intérêts)
# - Courbe Capital vs Intérêts cumulés
# - Waterfall final
#
# Désormais organisés dans des sous-sections pliables (expanders)
# ---------------------------------------------------------

import pandas as pd
import altair as alt
import streamlit as st

from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR


def create_simulation_chart(pv, pmt, rate, n_years, fv_target=None):
    """
    Produit :
        - 4 graphiques, chacun dans un expander
    """

    # ---------------------------------------------------------
    # 1) Génération des données mensuelles
    # ---------------------------------------------------------
    months = int(n_years * 12)
    rate_m = rate / 100 / 12

    data = []
    value = pv
    capital = pv

    data.append({
        "Mois": 0,
        "Année": 0,
        "Valeur Totale": pv,
        "Capital Investi": pv,
        "Interets": 0
    })

    for m in range(1, months + 1):
        value = value * (1 + rate_m) + pmt
        capital += pmt

        data.append({
            "Mois": m,
            "Année": m / 12,
            "Valeur Totale": value,
            "Capital Investi": capital,
            "Interets": value - capital
        })

    df = pd.DataFrame(data)

    # =========================================================
    # ==========  I — Courbe d’évolution du portefeuille ======
    # =========================================================

    with st.expander("📈 Évolution du portefeuille (courbe principale)", expanded=True):

        curve_val = (
            alt.Chart(df)
            .mark_line(strokeWidth=3)
            .encode(
                x=alt.X("Année:Q", title="Horizon (années)"),
                y=alt.Y("Valeur Totale:Q", title="Montant (FCFA)"),
                color=alt.value(PRIMARY_COLOR),
                tooltip=[
                    alt.Tooltip("Année:Q", format=".2f"),
                    alt.Tooltip("Valeur Totale:Q", format=",.0f"),
                ],
            )
            .properties(height=350)
        )

        invested_line = (
            alt.Chart(df)
            .mark_line(strokeDash=[4, 4], strokeWidth=2)
            .encode(
                x="Année:Q",
                y="Capital Investi:Q",
                color=alt.value(SECONDARY_COLOR),
                tooltip=[alt.Tooltip("Capital Investi:Q", format=",.0f")],
            )
        )

        chart = curve_val + invested_line

        if fv_target is not None and fv_target > 0:
            rule = (
                alt.Chart(pd.DataFrame({"y": [fv_target]}))
                .mark_rule(color="red", strokeDash=[5, 4])
                .encode(y="y:Q")
            )
            chart = chart + rule

        st.altair_chart(chart.interactive(), use_container_width=True)

    # =========================================================
    # =======  II — Histogramme Capital/Intérêts annuel =======
    # =========================================================

    with st.expander("📊 Répartition annuelle : Capital Investi vs Intérêts"):

        df_yearly = df.copy()
        df_yearly["Année_int"] = df_yearly["Année"].astype(int)
        df_group = df_yearly.groupby("Année_int").agg({
            "Capital Investi": "last",
            "Interets": "last",
        }).reset_index()

        df_group["Capital Investi Annuel"] = df_group["Capital Investi"].diff().fillna(df_group["Capital Investi"])
        df_group["Interets Annuel"] = df_group["Interets"].diff().fillna(df_group["Interets"])

        df_bar = df_group.melt(
            id_vars="Année_int",
            value_vars=["Capital Investi Annuel", "Interets Annuel"],
            var_name="Catégorie",
            value_name="Montant"
        )

        color_scale = alt.Scale(
            domain=["Capital Investi Annuel", "Interets Annuel"],
            range=[SECONDARY_COLOR, PRIMARY_COLOR]
        )

        bar = (
            alt.Chart(df_bar)
            .mark_bar()
            .encode(
                x=alt.X("Année_int:O", title="Année"),
                y=alt.Y("Montant:Q", title="Montant (FCFA)"),
                color=alt.Color("Catégorie:N", scale=color_scale),
                tooltip=[
                    alt.Tooltip("Catégorie:N"),
                    alt.Tooltip("Montant:Q", format=",.0f")
                ],
            )
            .properties(height=350)
        )

        st.altair_chart(bar, use_container_width=True)

    # =========================================================
    # === III — Couroles cumulées : Capital vs Intérêts ======
    # =========================================================

    with st.expander("📈 Capital vs Intérêts cumulés"):

        curve_cum_cap = (
            alt.Chart(df)
            .mark_line(strokeWidth=3)
            .encode(
                x="Année:Q",
                y="Capital Investi:Q",
                color=alt.value(SECONDARY_COLOR),
                tooltip=[alt.Tooltip("Capital Investi:Q", format=",.0f")],
            )
        )

        curve_cum_int = (
            alt.Chart(df)
            .mark_line(strokeWidth=3)
            .encode(
                x="Année:Q",
                y="Interets:Q",
                color=alt.value(PRIMARY_COLOR),
                tooltip=[alt.Tooltip("Interets:Q", format=",.0f")],
            )
        )

        st.altair_chart((curve_cum_cap + curve_cum_int).interactive(), use_container_width=True)

    # =========================================================
    # =============== IV — Waterfall FV breakdown =============
    # =========================================================

    with st.expander("💧 Décomposition du montant final (Waterfall)"):

        final = df.iloc[-1]
        total_pmt = pmt * months
        total_interest = final["Interets"]

        wf_df = pd.DataFrame({
            "Étape": ["Capital Initial", "Versements Totaux", "Intérêts", "Montant Final"],
            "Montant": [pv, total_pmt, total_interest, final["Valeur Totale"]],
            "Couleur": [SECONDARY_COLOR, SECONDARY_COLOR, PRIMARY_COLOR, ACCENT_COLOR]
        })

        waterfall = (
            alt.Chart(wf_df)
            .mark_bar()
            .encode(
                x=alt.X("Étape:N"),
                y=alt.Y("Montant:Q", title="Montant (FCFA)"),
                color=alt.Color("Couleur:N", scale=None),
                tooltip=[
                    alt.Tooltip("Étape:N"),
                    alt.Tooltip("Montant:Q", format=",.0f")
                ]
            )
            .properties(height=300)
        )

        st.altair_chart(waterfall, use_container_width=True)
