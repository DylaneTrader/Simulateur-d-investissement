# ui/layout.py
# ----------------------------------------
# Composants d'affichage du contenu principal
# (résultats, métriques, cartes, graphiques)
#
# Utilise la palette provenant de `core/config.py`

import math
import streamlit as st

from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from core.calculations import calculate_fv, calculate_pmt, calculate_pv, calculate_n_years
from core.utils import fmt_money
from ui.charts import create_simulation_chart
from core.export import create_pdf_report, create_download_link, send_email_with_attachment
from datetime import datetime


def display_results(inputs: dict, calculation_mode: str):
    """
    Affiche le bloc principal des résultats et appelle le graphique.
    `inputs` : dict contenant les valeurs 'pv', 'pmt', 'fv', 'rate', 'n_years'
    `calculation_mode` : texte (Montant Final, PV, PMT, Horizon)
    """

    # On récupère les données
    pv = inputs.get("pv", 0)
    pmt = inputs.get("pmt", 0)
    fv = inputs.get("fv", 0)
    rate = inputs.get("rate", 0)
    n_years = inputs.get("n_years", 0)

    # -------- CALCUL DU PARAMÈTRE MANQUANT --------
    calculated_value = None
    
    try:
        if calculation_mode == "Montant Final":
            calculated_value = calculate_fv(pv, pmt, rate, n_years)
            fv = calculated_value
            result_text = f"Montant Final calculé : **{fmt_money(calculated_value)}**"
            
        elif calculation_mode == "Versement Mensuel":
            calculated_value = calculate_pmt(fv, pv, rate, n_years)
            pmt = calculated_value
            result_text = f"Versement Mensuel calculé : **{fmt_money(calculated_value)}**"
            
            # Afficher aussi les équivalents trimestriels et annuels
            pmt_quarterly = calculated_value * 3
            pmt_yearly = calculated_value * 12
            result_text += f"\n\n*Équivalents :*\n- Par trimestre : {fmt_money(pmt_quarterly)}\n- Par an : {fmt_money(pmt_yearly)}"
            
        elif calculation_mode == "Montant Initial":
            calculated_value = calculate_pv(fv, pmt, rate, n_years)
            pv = calculated_value
            result_text = f"Montant Initial calculé : **{fmt_money(calculated_value)}**"
            
        elif calculation_mode == "Horizon de Placement":
            calculated_value = calculate_n_years(fv, pv, pmt, rate)
            n_years = calculated_value
            
            if not math.isfinite(calculated_value):
                result_text = "⚠️ **Impossible d'atteindre l'objectif** avec ces paramètres (horizon infini requis)"
            elif calculated_value <= 0:
                result_text = "✅ **L'objectif est déjà atteint** avec le montant initial actuel (aucun horizon nécessaire)"
            else:
                years = int(calculated_value)
                months = int((calculated_value - years) * 12)
                result_text = f"Horizon de Placement calculé : **{years} ans et {months} mois** ({calculated_value:.2f} années)"
        
        else:
            st.error("Mode de calcul non reconnu")
            return

    except Exception as e:
        st.error(f"Erreur lors du calcul : {str(e)}")
        return

    # -------- AFFICHAGE DU RÉSULTAT --------
    st.markdown(
        f"""
        <h2 style="
            color: {PRIMARY_COLOR};
            font-weight: 700;
            margin-top: 10px;">
            Résultats — {calculation_mode}
        </h2>
        """,
        unsafe_allow_html=True
    )

    # Affichage du résultat calculé dans une boîte mise en évidence
    st.success(result_text)

    st.markdown("---")

    # ----------- CARTES ESTHÉTIQUES DES MÉTRIQUES -----------
    # Calcul des valeurs finales
    total_capital = fv
    total_invested = pv + (pmt * n_years * 12)
    total_interest = total_capital - total_invested
    
    # Calcul des pourcentages
    invested_percent = (total_invested / total_capital * 100) if total_capital > 0 else 0
    interest_percent = (total_interest / total_capital * 100) if total_capital > 0 else 0
    
    st.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR}; margin-bottom: 20px;">
            📊 Vue d'ensemble financière
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    # Première ligne : Paramètres actuels en cartes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        _display_metric_card("Montant Initial", fmt_money(pv), "💰", PRIMARY_COLOR)
    with col2:
        _display_metric_card("Versement Mensuel", fmt_money(pmt), "💳", PRIMARY_COLOR)
    with col3:
        _display_metric_card("Rendement Annuel", f"{rate:.2f} %", "📈", ACCENT_COLOR)
    with col4:
        _display_metric_card("Horizon", f"{n_years} ans", "⏱️", ACCENT_COLOR)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Deuxième ligne : Résultats financiers en cartes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _display_result_card(
            "Capital Total",
            fmt_money(total_capital),
            "",
            PRIMARY_COLOR,
            "💎"
        )
    
    with col2:
        _display_result_card(
            "Capital Investi",
            fmt_money(total_invested),
            f"{invested_percent:.1f}% du total",
            SECONDARY_COLOR,
            "💵"
        )
    
    with col3:
        _display_result_card(
            "Intérêts Générés",
            fmt_money(total_interest),
            f"{interest_percent:.1f}% du total",
            ACCENT_COLOR,
            "✨"
        )

    st.markdown("---")

    # ----------- BLOC DES GRAPHIQUES -----------
    st.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR};">Visualisations détaillées</h3>
        """,
        unsafe_allow_html=True
    )

    # Graphique principal
    create_simulation_chart(
        pv=pv,
        pmt=pmt,
        rate=rate,
        n_years=n_years,
        fv_target=inputs.get("fv")
    )

    st.markdown("---")

    # ----------- BLOC D'EXPORTATION -----------
    st.markdown(
        f"""
        <h3 style="color:{PRIMARY_COLOR};">📤 Exporter le rapport</h3>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        # Bouton de téléchargement PDF
        if st.button("📥 Générer et télécharger le PDF", type="primary", use_container_width=True):
            # Récupérer les informations commerciales depuis session_state
            commercial_info = {
                'date': datetime.now().strftime("%d/%m/%Y"),
                'interlocuteur': st.session_state.get('interlocuteur', ''),
                'client_name': st.session_state.get('client_name', ''),
                'country': st.session_state.get('country', 'Côte d\'Ivoire')
            }
            
            # Préparer les données pour le PDF
            results = {
                'total_capital': total_capital,
                'total_invested': total_invested,
                'total_interest': total_interest
            }
            
            # Générer le PDF
            with st.spinner("Génération du rapport PDF..."):
                pdf_bytes = create_pdf_report(inputs, results, commercial_info)
                
                # Créer un nom de fichier unique
                filename = f"rapport_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Offrir le téléchargement
                st.download_button(
                    label="📥 Télécharger le rapport",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success("✅ Rapport PDF généré avec succès !")

    with col2:
        # Formulaire d'envoi par email
        with st.expander("📧 Envoyer par email", expanded=False):
            recipient_email = st.text_input(
                "Email du destinataire",
                placeholder="exemple@email.com",
                key="recipient_email"
            )
            
            if st.button("📧 Envoyer le rapport", use_container_width=True):
                if recipient_email and '@' in recipient_email:
                    # Récupérer les informations commerciales
                    commercial_info = {
                        'date': datetime.now().strftime("%d/%m/%Y"),
                        'interlocuteur': st.session_state.get('interlocuteur', ''),
                        'client_name': st.session_state.get('client_name', ''),
                        'country': st.session_state.get('country', 'Côte d\'Ivoire')
                    }
                    
                    # Préparer les données pour le PDF
                    results = {
                        'total_capital': total_capital,
                        'total_invested': total_invested,
                        'total_interest': total_interest
                    }
                    
                    # Générer le PDF
                    with st.spinner("Préparation et envoi de l'email..."):
                        pdf_bytes = create_pdf_report(inputs, results, commercial_info)
                        
                        # Préparer l'email
                        client_name = commercial_info.get('client_name', 'Client')
                        subject = f"CGF GESTION - Rapport de simulation d'investissement - {client_name}"
                        
                        body = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: {PRIMARY_COLOR};">CGF GESTION</h2>
                            <p>Bonjour,</p>
                            <p>Veuillez trouver ci-joint votre rapport de simulation d'investissement.</p>
                            <p><strong>Résumé :</strong></p>
                            <ul>
                                <li>Capital Total : {fmt_money(total_capital)}</li>
                                <li>Capital Investi : {fmt_money(total_invested)}</li>
                                <li>Intérêts Générés : {fmt_money(total_interest)}</li>
                            </ul>
                            <p>Pour toute question, n'hésitez pas à nous contacter.</p>
                            <p>Cordialement,<br/>
                            <strong>L'équipe CGF GESTION</strong><br/>
                            RIVIERA 4, immeuble BRANDON & MCAIN</p>
                        </body>
                        </html>
                        """
                        
                        filename = f"rapport_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        
                        # Envoyer l'email
                        success = send_email_with_attachment(
                            recipient_email,
                            subject,
                            body,
                            pdf_bytes,
                            filename
                        )
                        
                        if success:
                            st.success(f"✅ Rapport envoyé avec succès à {recipient_email} !")
                        else:
                            st.info("ℹ️ L'envoi par email nécessite une configuration SMTP. Utilisez le téléchargement PDF pour le moment.")
                else:
                    st.error("⚠️ Veuillez entrer une adresse email valide.")


def _display_metric_card(label: str, value: str, icon: str, color: str):
    """
    Affiche une petite carte de métrique avec icône.
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
            border-left: 4px solid {color};
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
            <div style="color: #666; font-size: 12px; font-weight: 500; margin-bottom: 5px;">
                {label}
            </div>
            <div style="color: {color}; font-size: 18px; font-weight: 700;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _display_result_card(label: str, value: str, subtitle: str, color: str, icon: str):
    """
    Affiche une carte de résultat avec valeur principale et sous-titre (pourcentage).
    """
    subtitle_html = f"""
        <div style="color: #888; font-size: 13px; margin-top: 8px; font-weight: 500;">
            {subtitle}
        </div>
    """ if subtitle else ""
    
    st.markdown(
        f"""
        <div style="
            background: white;
            border: 2px solid {color}30;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            height: 100%;
        ">
            <div style="font-size: 32px; margin-bottom: 10px;">{icon}</div>
            <div style="color: #666; font-size: 13px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase;">
                {label}
            </div>
            <div style="color: {color}; font-size: 22px; font-weight: 700;">
                {value}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )

