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
    # ===== IV — Distribution du capital (Pie Chart) ==========
    # =========================================================

    with st.expander("🥧 Distribution du capital estimé", expanded=True):

        final = df.iloc[-1]
        total_invested = final["Capital Investi"]
        total_interest = final["Interets"]

        # Données pour le camembert
        pie_df = pd.DataFrame({
            "Catégorie": ["Capital Investi", "Intérêts Générés"],
            "Montant": [total_invested, total_interest],
            "Couleur": [SECONDARY_COLOR, PRIMARY_COLOR]
        })

        # Création du graphique en camembert avec Altair
        pie_chart = (
            alt.Chart(pie_df)
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta("Montant:Q", stack=True),
                color=alt.Color(
                    "Catégorie:N",
                    scale=alt.Scale(
                        domain=["Capital Investi", "Intérêts Générés"],
                        range=[SECONDARY_COLOR, PRIMARY_COLOR]
                    ),
                    legend=alt.Legend(title="Composition")
                ),
                tooltip=[
                    alt.Tooltip("Catégorie:N"),
                    alt.Tooltip("Montant:Q", format=",.0f", title="Montant (FCFA)"),
                ]
            )
            .properties(height=400)
        )

        st.altair_chart(pie_chart, use_container_width=True)
        
        # Afficher les pourcentages
        total = total_invested + total_interest
        invested_pct = (total_invested / total * 100) if total > 0 else 0
        interest_pct = (total_interest / total * 100) if total > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Capital Investi** : {invested_pct:.1f}%")
        with col2:
            st.success(f"**Intérêts Générés** : {interest_pct:.1f}%")
