# core/export.py
# ---------------------------------------------------------
# Fonctionnalités d'exportation et d'envoi de rapports
# - Génération de PDF
# - Envoi par email
# ---------------------------------------------------------

import io
import base64
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from core.utils import fmt_money
from core.config import PRIMARY_COLOR, SECONDARY_COLOR, APP_NAME, ACCENT_COLOR


def _create_portfolio_evolution_chart(pv, pmt, rate, n_years):
    """
    Crée le graphique d'évolution du portefeuille pour le PDF.
    
    Returns:
        io.BytesIO: Buffer contenant l'image du graphique
    """
    # Générer les données mensuelles
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
    })
    
    for m in range(1, months + 1):
        value = value * (1 + rate_m) + pmt
        capital += pmt
        
        data.append({
            "Mois": m,
            "Année": m / 12,
            "Valeur Totale": value,
            "Capital Investi": capital,
        })
    
    df = pd.DataFrame(data)
    
    # Créer le graphique avec matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    
    ax.plot(df["Année"], df["Valeur Totale"], 
            color=PRIMARY_COLOR, linewidth=2.5, label="Valeur Totale")
    ax.plot(df["Année"], df["Capital Investi"], 
            color=SECONDARY_COLOR, linewidth=2, linestyle='--', label="Capital Investi")
    
    ax.set_xlabel("Horizon (années)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Montant (FCFA)", fontsize=11, fontweight='bold')
    ax.set_title("Évolution du Portefeuille", fontsize=14, fontweight='bold', color=PRIMARY_COLOR)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Formater l'axe Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    plt.tight_layout()
    
    # Sauvegarder dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def _create_pie_chart(total_invested, total_interest):
    """
    Crée le graphique en camembert de distribution du capital pour le PDF.
    
    Returns:
        io.BytesIO: Buffer contenant l'image du graphique
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    
    labels = ['Capital Investi', 'Intérêts Générés']
    sizes = [total_invested, total_interest]
    colors_pie = [SECONDARY_COLOR, PRIMARY_COLOR]
    explode = (0.05, 0.05)  # Légère séparation des parts
    
    # Créer le camembert
    wedges, texts, autotexts = ax.pie(
        sizes, 
        explode=explode, 
        labels=labels, 
        colors=colors_pie,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )
    
    # Améliorer la lisibilité des pourcentages
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')
    
    ax.set_title("Distribution du Capital Estimé", fontsize=14, fontweight='bold', color=PRIMARY_COLOR, pad=20)
    ax.axis('equal')
    
    plt.tight_layout()
    
    # Sauvegarder dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def create_pdf_report(inputs: dict, results: dict, commercial_info: dict = None):
    """
    Crée un rapport PDF de la simulation.
    
    Args:
        inputs: dict contenant pv, pmt, rate, n_years, fv
        results: dict contenant total_capital, total_invested, total_interest
        commercial_info: dict contenant interlocuteur, client_name, country, date
    
    Returns:
        bytes: Le contenu du PDF
    """
    buffer = io.BytesIO()
    
    # Configuration du document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Container pour les éléments
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Logo en-tête
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=4*cm, height=4*cm, kind='proportional')
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))
        except Exception as e:
            # Si le logo ne peut pas être chargé, on continue sans
            pass
    
    # En-tête
    elements.append(Paragraph("CGF GESTION", title_style))
    elements.append(Paragraph("Rapport de Simulation d'Investissement", heading_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Informations commerciales
    if commercial_info:
        info_data = [
            ['Date:', commercial_info.get('date', datetime.now().strftime("%d/%m/%Y"))],
            ['Interlocuteur:', commercial_info.get('interlocuteur', 'Non renseigné')],
            ['Client:', commercial_info.get('client_name', 'Non renseigné')],
            ['Entreprise:', 'CGF GESTION'],
            ['Adresse:', 'RIVIERA 4, immeuble BRANDON & MCAIN'],
            ['Pays:', commercial_info.get('country', 'Côte d\'Ivoire')]
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(PRIMARY_COLOR)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 1*cm))
    
    # Séparateur
    elements.append(Paragraph("<hr width='100%'/>", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Paramètres de la simulation
    elements.append(Paragraph("Paramètres de la Simulation", heading_style))
    
    params_data = [
        ['Paramètre', 'Valeur'],
        ['Montant Initial', fmt_money(inputs.get('pv', 0))],
        ['Versement Mensuel', fmt_money(inputs.get('pmt', 0))],
        ['Rendement Annuel', f"{inputs.get('rate', 0):.2f} %"],
        ['Horizon de Placement', f"{inputs.get('n_years', 0)} ans"]
    ]
    
    params_table = Table(params_data, colWidths=[7*cm, 7*cm])
    params_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(params_table)
    elements.append(Spacer(1, 1*cm))
    
    # Résultats
    elements.append(Paragraph("Résultats de la Simulation", heading_style))
    
    total_capital = results.get('total_capital', 0)
    total_invested = results.get('total_invested', 0)
    total_interest = results.get('total_interest', 0)
    
    invested_percent = (total_invested / total_capital * 100) if total_capital > 0 else 0
    interest_percent = (total_interest / total_capital * 100) if total_capital > 0 else 0
    
    results_data = [
        ['Résultat', 'Montant', 'Pourcentage'],
        ['Capital Total', fmt_money(total_capital), '100%'],
        ['Capital Investi', fmt_money(total_invested), f"{invested_percent:.1f}%"],
        ['Intérêts Générés', fmt_money(total_interest), f"{interest_percent:.1f}%"]
    ]
    
    results_table = Table(results_data, colWidths=[5*cm, 5*cm, 4*cm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (0, 1), colors.HexColor(PRIMARY_COLOR + '40')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 2), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 1*cm))
    
    # Analyse
    elements.append(Paragraph("Analyse", heading_style))
    
    analysis_text = f"""
    <b>Résumé de votre investissement :</b><br/>
    <br/>
    Avec un investissement initial de {fmt_money(inputs.get('pv', 0))} et des versements mensuels 
    de {fmt_money(inputs.get('pmt', 0))} sur une période de {inputs.get('n_years', 0)} ans 
    à un taux de rendement de {inputs.get('rate', 0):.2f}% par an, vous accumulerez un capital total 
    de {fmt_money(total_capital)}.<br/>
    <br/>
    Sur ce montant, {fmt_money(total_invested)} ({invested_percent:.1f}%) correspond à votre capital investi 
    et {fmt_money(total_interest)} ({interest_percent:.1f}%) représente les intérêts générés par vos placements.<br/>
    <br/>
    <b>Points clés :</b><br/>
    • Durée totale de l'investissement : {inputs.get('n_years', 0)} ans ({int(inputs.get('n_years', 0) * 12)} mois)<br/>
    • Versements mensuels cumulés : {fmt_money(inputs.get('pmt', 0) * inputs.get('n_years', 0) * 12)}<br/>
    • Rendement total : {((total_capital - total_invested) / total_invested * 100) if total_invested > 0 else 0:.1f}%<br/>
    """
    
    elements.append(Paragraph(analysis_text, normal_style))
    elements.append(Spacer(1, 1*cm))
    
    # Graphiques
    elements.append(PageBreak())
    elements.append(Paragraph("Visualisations", heading_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Graphique 1: Évolution du portefeuille
    try:
        chart_buffer = _create_portfolio_evolution_chart(
            inputs.get('pv', 0),
            inputs.get('pmt', 0),
            inputs.get('rate', 0),
            inputs.get('n_years', 0)
        )
        chart_img = Image(chart_buffer, width=16*cm, height=8*cm)
        elements.append(chart_img)
        elements.append(Spacer(1, 1*cm))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erreur lors de la génération du graphique d'évolution: {str(e)}</i>", normal_style))
        elements.append(Spacer(1, 0.5*cm))
    
    # Graphique 2: Distribution du capital (pie chart)
    try:
        pie_buffer = _create_pie_chart(total_invested, total_interest)
        pie_img = Image(pie_buffer, width=12*cm, height=8*cm)
        pie_img.hAlign = 'CENTER'
        elements.append(pie_img)
        elements.append(Spacer(1, 1*cm))
    except Exception as e:
        elements.append(Paragraph(f"<i>Erreur lors de la génération du graphique de distribution: {str(e)}</i>", normal_style))
        elements.append(Spacer(1, 0.5*cm))
    
    # Pied de page
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("<hr width='100%'/>", normal_style))
    footer_text = f"""
    <i>Document généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}</i><br/>
    <b>CGF GESTION</b> - RIVIERA 4, immeuble BRANDON & MCAIN<br/>
    Simulateur d'Investissement - Version 1.0
    """
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Construire le PDF
    doc.build(elements)
    
    # Récupérer le contenu
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def create_download_link(pdf_bytes, filename="rapport_simulation.pdf"):
    """
    Crée un lien de téléchargement pour le PDF.
    
    Args:
        pdf_bytes: Le contenu du PDF en bytes
        filename: Le nom du fichier
        
    Returns:
        str: HTML pour le lien de téléchargement
    """
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Télécharger le rapport PDF</a>'


def send_email_with_attachment(recipient_email: str, subject: str, body: str, pdf_bytes: bytes, filename: str = "rapport.pdf"):
    """
    Envoie un email avec le rapport PDF en pièce jointe.
    
    Note: Cette fonction nécessite la configuration d'un serveur SMTP.
    Pour une utilisation en production, configurez les variables d'environnement:
    - SMTP_SERVER
    - SMTP_PORT
    - SMTP_USERNAME
    - SMTP_PASSWORD
    
    Args:
        recipient_email: Email du destinataire
        subject: Sujet de l'email
        body: Corps de l'email
        pdf_bytes: Contenu du PDF
        filename: Nom du fichier PDF
        
    Returns:
        tuple: (success: bool, message: str) - True si l'envoi a réussi avec un message de statut
    """
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        import os
        
        # Configuration SMTP (à configurer selon l'environnement)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        if not smtp_username or not smtp_password:
            return False, "⚠️ La fonctionnalité d'envoi par email n'est pas configurée. Veuillez configurer les variables d'environnement SMTP (SMTP_USERNAME et SMTP_PASSWORD)."
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Ajouter le corps du message
        msg.attach(MIMEText(body, 'html'))
        
        # Ajouter le PDF en pièce jointe
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(pdf_attachment)
        
        # Envoyer l'email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, f"✅ Email envoyé avec succès à {recipient_email}"
        
    except Exception as e:
        return False, f"❌ Erreur lors de l'envoi de l'email : {str(e)}"
