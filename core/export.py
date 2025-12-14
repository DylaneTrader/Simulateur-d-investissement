# core/export.py
# ----------------------------------------
# Gestion de l'exportation PDF et de l'envoi par email
# - Création de rapports PDF avec reportlab
# - Génération de graphiques matplotlib pour inclusion dans le PDF
# - Envoi d'emails avec pièce jointe via SMTP

import io
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR
from core.utils import fmt_money


def _hex_to_rgb(hex_color: str) -> tuple:
    """Convertit une couleur hexadécimale en tuple RGB (0-1)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


def _create_portfolio_evolution_chart(pv: float, pmt: float, rate: float, n_years: float) -> io.BytesIO:
    """
    Crée un graphique matplotlib de l'évolution du portefeuille.
    Retourne un buffer BytesIO contenant l'image PNG.
    """
    months = int(n_years * 12)
    rate_m = rate / 100 / 12
    
    # Génération des données
    years_list = []
    portfolio_values = []
    invested_values = []
    
    value = pv
    capital = pv
    
    years_list.append(0)
    portfolio_values.append(pv)
    invested_values.append(pv)
    
    for m in range(1, months + 1):
        value = value * (1 + rate_m) + pmt
        capital += pmt
        
        years_list.append(m / 12)
        portfolio_values.append(value)
        invested_values.append(capital)
    
    # Création du graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    
    primary_rgb = _hex_to_rgb(PRIMARY_COLOR)
    secondary_rgb = _hex_to_rgb(SECONDARY_COLOR)
    
    ax.plot(years_list, portfolio_values, color=primary_rgb, linewidth=2.5, label='Valeur Totale')
    ax.plot(years_list, invested_values, color=secondary_rgb, linewidth=2, linestyle='--', label='Capital Investi')
    
    ax.set_xlabel('Années', fontsize=11, fontweight='bold')
    ax.set_ylabel('Montant (FCFA)', fontsize=11, fontweight='bold')
    ax.set_title('Évolution du Portefeuille', fontsize=13, fontweight='bold', color=primary_rgb)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='plain', axis='y')
    
    # Formater l'axe y avec séparateurs de milliers
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'.replace(',', ' ')))
    
    plt.tight_layout()
    
    # Sauvegarder dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def _create_pie_chart(total_invested: float, total_interest: float) -> io.BytesIO:
    """
    Crée un graphique en camembert de la répartition capital/intérêts.
    Retourne un buffer BytesIO contenant l'image PNG.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    
    primary_rgb = _hex_to_rgb(PRIMARY_COLOR)
    secondary_rgb = _hex_to_rgb(SECONDARY_COLOR)
    
    sizes = [total_invested, total_interest]
    labels = ['Capital Investi', 'Intérêts Générés']
    colors_pie = [secondary_rgb, primary_rgb]
    
    # Calculer les pourcentages
    total = total_invested + total_interest
    percentages = [(s / total * 100) if total > 0 else 0 for s in sizes]
    
    # Créer le camembert
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        colors=colors_pie,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )
    
    ax.set_title('Distribution du Capital', fontsize=13, fontweight='bold', color=primary_rgb)
    
    plt.tight_layout()
    
    # Sauvegarder dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def create_pdf_report(inputs: dict, calculation_mode: str, commercial_info: dict = None) -> io.BytesIO:
    """
    Génère un rapport PDF complet avec:
    - En-tête CGF GESTION
    - Informations commerciales
    - Paramètres de simulation
    - Résultats financiers
    - Graphiques
    
    Args:
        inputs: Dictionnaire avec pv, pmt, fv, rate, n_years
        calculation_mode: Mode de calcul utilisé
        commercial_info: Dictionnaire avec interlocuteur, client_name, country, date
    
    Returns:
        Buffer BytesIO contenant le PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style pour le titre principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style pour les sous-titres
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # Style pour le texte normal
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Contenu du PDF
    story = []
    
    # ====== EN-TÊTE ======
    story.append(Paragraph("CGF GESTION", title_style))
    story.append(Paragraph("Simulation d'Investissement", heading_style))
    story.append(Spacer(1, 0.3*cm))
    
    # ====== INFORMATIONS COMMERCIALES ======
    if commercial_info:
        story.append(Paragraph("Informations", heading_style))
        
        info_data = [
            ["Date:", commercial_info.get('date', datetime.now().strftime("%d/%m/%Y"))],
            ["Interlocuteur:", commercial_info.get('interlocuteur', 'N/A')],
            ["Client:", commercial_info.get('client_name', 'N/A')],
            ["Pays:", commercial_info.get('country', 'N/A')],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(PRIMARY_COLOR)),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))
    
    # ====== PARAMÈTRES DE SIMULATION ======
    story.append(Paragraph("Paramètres de Simulation", heading_style))
    story.append(Paragraph(f"<b>Mode de calcul:</b> {calculation_mode}", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    pv = inputs.get('pv', 0)
    pmt = inputs.get('pmt', 0)
    fv = inputs.get('fv', 0)
    rate = inputs.get('rate', 0)
    n_years = inputs.get('n_years', 0)
    
    params_data = [
        ["Paramètre", "Valeur"],
        ["Montant Initial", fmt_money(pv)],
        ["Versement Mensuel", fmt_money(pmt)],
        ["Rendement Annuel", f"{rate:.2f} %"],
        ["Horizon de Placement", f"{n_years:.1f} ans"],
        ["Objectif (Montant Final)", fmt_money(fv)],
    ]
    
    params_table = Table(params_data, colWidths=[8*cm, 8*cm])
    params_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(params_table)
    story.append(Spacer(1, 0.5*cm))
    
    # ====== RÉSULTATS FINANCIERS ======
    story.append(Paragraph("Résultats Financiers", heading_style))
    
    total_capital = fv
    total_invested = pv + (pmt * n_years * 12)
    total_interest = total_capital - total_invested
    
    results_data = [
        ["Métrique", "Montant", "% du Total"],
        ["Capital Total", fmt_money(total_capital), "100%"],
        ["Capital Investi", fmt_money(total_invested), f"{(total_invested/total_capital*100) if total_capital > 0 else 0:.1f}%"],
        ["Intérêts Générés", fmt_money(total_interest), f"{(total_interest/total_capital*100) if total_capital > 0 else 0:.1f}%"],
    ]
    
    results_table = Table(results_data, colWidths=[6*cm, 6*cm, 4*cm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(ACCENT_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Équivalents du versement mensuel si applicable
    if pmt > 0:
        story.append(Paragraph("Équivalents du Versement Mensuel", heading_style))
        equiv_data = [
            ["Période", "Montant"],
            ["Mensuel", fmt_money(pmt)],
            ["Trimestriel", fmt_money(pmt * 3)],
            ["Semestriel", fmt_money(pmt * 6)],
            ["Annuel", fmt_money(pmt * 12)],
        ]
        
        equiv_table = Table(equiv_data, colWidths=[8*cm, 8*cm])
        equiv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(SECONDARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))
        story.append(equiv_table)
        story.append(Spacer(1, 0.5*cm))
    
    # ====== GRAPHIQUES ======
    story.append(PageBreak())
    story.append(Paragraph("Visualisations", heading_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Graphique d'évolution
    story.append(Paragraph("Évolution du Portefeuille", normal_style))
    chart_buffer = _create_portfolio_evolution_chart(pv, pmt, rate, n_years)
    chart_img = Image(chart_buffer, width=16*cm, height=9.6*cm)
    story.append(chart_img)
    story.append(Spacer(1, 0.5*cm))
    
    # Graphique en camembert
    story.append(Paragraph("Distribution du Capital", normal_style))
    pie_buffer = _create_pie_chart(total_invested, total_interest)
    pie_img = Image(pie_buffer, width=12*cm, height=12*cm)
    story.append(pie_img)
    story.append(Spacer(1, 0.5*cm))
    
    # ====== COMMENTAIRE ======
    story.append(Paragraph("Analyse et Commentaires", heading_style))
    
    # Générer un commentaire automatique
    roi = ((total_interest / total_invested) * 100) if total_invested > 0 else 0
    comment = f"""
    Cette simulation montre qu'avec un investissement initial de {fmt_money(pv)} 
    et des versements mensuels de {fmt_money(pmt)} sur une période de {n_years:.1f} ans 
    avec un rendement annuel de {rate:.2f}%, vous pouvez atteindre un capital total de {fmt_money(total_capital)}.
    <br/><br/>
    Le capital investi total s'élève à {fmt_money(total_invested)}, 
    tandis que les intérêts générés représentent {fmt_money(total_interest)}, 
    soit un retour sur investissement de {roi:.1f}%.
    <br/><br/>
    Cette projection est basée sur des hypothèses de rendement constant et ne garantit pas 
    les performances futures. Les résultats réels peuvent varier.
    """
    
    story.append(Paragraph(comment, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # ====== PIED DE PAGE ======
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "CGF GESTION - RIVIERA 4, immeuble BRANDON & MCAIN",
        footer_style
    ))
    story.append(Paragraph(
        f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        footer_style
    ))
    
    # Construire le PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer


def send_email_with_attachment(
    sender_email: str,
    recipient_email: str,
    pdf_buffer: io.BytesIO,
    simulation_date: str,
    summary: str
) -> tuple[bool, str]:
    """
    Envoie un email avec le PDF en pièce jointe.
    
    Args:
        sender_email: Email de l'expéditeur (interlocuteur)
        recipient_email: Email du destinataire (client)
        pdf_buffer: Buffer contenant le PDF
        simulation_date: Date de la simulation (format DD/MM/YYYY)
        summary: Résumé des résultats à inclure dans l'email
    
    Returns:
        Tuple (success: bool, message: str)
    """
    # Récupérer les variables d'environnement SMTP
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    # Vérifier que les variables sont configurées
    if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
        return False, """Configuration SMTP incomplète. Veuillez configurer les variables d'environnement:
        SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
        
        Consultez le fichier .env.example pour plus d'informations."""
    
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"CGF GESTION - Simulation d'investissement au {simulation_date}"
        
        # Corps de l'email
        body = f"""
Bonjour,

Veuillez trouver ci-joint votre simulation d'investissement réalisée par CGF GESTION.

{summary}

Ce document présente une projection détaillée de votre investissement avec:
- Les paramètres de simulation
- Les résultats financiers attendus
- Des visualisations graphiques
- Une analyse complète

Pour toute question ou clarification, n'hésitez pas à nous contacter.

Cordialement,
CGF GESTION
RIVIERA 4, immeuble BRANDON & MCAIN

---
Cet email a été généré automatiquement par le Simulateur d'Investissement CGF GESTION.
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Attacher le PDF
        pdf_buffer.seek(0)
        pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
        pdf_attachment.add_header(
            'Content-Disposition', 
            'attachment', 
            filename=f'Simulation_CGF_GESTION_{simulation_date.replace("/", "-")}.pdf'
        )
        msg.attach(pdf_attachment)
        
        # Envoyer l'email
        with smtplib.SMTP(smtp_server, int(smtp_port), timeout=30) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, f"✅ Email envoyé avec succès à {recipient_email}"
        
    except smtplib.SMTPAuthenticationError:
        return False, """❌ Erreur d'authentification SMTP. 
        
        Pour Gmail, assurez-vous d'utiliser un mot de passe d'application (pas votre mot de passe normal):
        1. Activez la validation en 2 étapes
        2. Générez un mot de passe d'application: https://myaccount.google.com/apppasswords
        3. Utilisez ce mot de passe dans la variable SMTP_PASSWORD"""
        
    except smtplib.SMTPException as e:
        return False, f"❌ Erreur SMTP: {str(e)}"
        
    except Exception as e:
        return False, f"❌ Erreur lors de l'envoi de l'email: {str(e)}"
