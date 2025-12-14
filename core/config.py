# core/config.py
# ----------------
# Configuration globale et palette de couleurs tirée du logo "CGF GESTION".
# Ce fichier sert de source unique pour les couleurs et quelques constantes
# réutilisables dans toute l'application (UI, CSS, graphiques...).
#
# Usage :
#   from core.config import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, APP_NAME, get_theme_css
#   st.markdown(get_theme_css(), unsafe_allow_html=True)
#
# Les couleurs ont été extraites automatiquement depuis le fichier logo que tu as
# chargé dans /mnt/data/logo cgf gestion.jpeg (dominantes : deep blue, blue-gray, light-blue).

APP_NAME = "Simulateur d'Investissement - CGF Gestion"

# Palette (hex)
# - PRIMARY_COLOR : couleur principale (titres, accents forts)
# - SECONDARY_COLOR : couleur secondaire (widgets, bordures, tracés secondaires)
# - ACCENT_COLOR : couleur d'accent / background léger (cartes, badges)
PRIMARY_COLOR   = "#114B80"  # Bleu profond — bon pour titres, boutons principaux
SECONDARY_COLOR = "#567389"  # Bleu-gris — idéal pour widgets, lignes, icônes
ACCENT_COLOR    = "#ACC7DF"  # Bleu clair — pour fonds de cartes, hover, petites touches

# Autres variables globales utiles
TEXT_COLOR = "#1f2a33"       # couleur de texte par défaut (suffisamment contrastée)
CARD_BG = "#ffffff"          # fond des cartes / containers (on reste sobre)
BORDER_RADIUS = "12px"       # rayon de bord des cartes / boutons

# Default values for calculations
DEFAULT_INITIAL_CAPITAL = 100_000
DEFAULT_MONTHLY_PAYMENT = 50_000
DEFAULT_TARGET_AMOUNT = 10_000_000
DEFAULT_ANNUAL_RATE = 5.0
DEFAULT_HORIZON_YEARS = 10

# Constraints
MIN_RATE = -100
MAX_RATE = 100
MIN_HORIZON = 1
MAX_HORIZON = 100

# UI Configuration
CHART_HEIGHT = 350
PIE_CHART_HEIGHT = 400
EXPANDER_EXPANDED_BY_DEFAULT = True

# Countries for dropdown
UEMOA_COUNTRIES = [
    "Côte d'Ivoire",
    "Bénin",
    "Burkina Faso",
    "Guinée-Bissau",
    "Mali",
    "Niger",
    "Sénégal",
    "Togo"
]

def get_theme_css() -> str:
    """
    Retourne une chaîne CSS à injecter dans Streamlit via st.markdown(..., unsafe_allow_html=True).
    Cette CSS applique la palette définie ci-dessus à quelques éléments courants :
    - Titres (h1, h2)
    - Boutons Streamlit (classe .stButton)
    - Cartes / containers (via des sélecteurs communs)
    - Couleurs personnalisées pour les metrics & widgets
    NOTE: Les sélecteurs Streamlit changent parfois entre versions ; adapte-les si nécessaire.
    """
    css = f"""
    <style>
    /* ----- Typographie & titres ----- */
    .css-1d391kg h1, .css-1d391kg h2, .stMarkdown h1, .stMarkdown h2 {{
        color: {PRIMARY_COLOR} !important;
    }}

    /* ----- Boutons ----- */
    div.stButton > button {{
        background: linear-gradient(180deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: {BORDER_RADIUS} !important;
        padding: 8px 14px !important;
        box-shadow: 0 2px 6px rgba(17,75,128,0.18) !important;
    }}
    div.stButton > button:hover {{
        filter: brightness(0.95);
    }}

    /* ----- Cartes / conteneurs (approche générale) ----- */
    .card, .stCard, .stExpander {{
        background: {CARD_BG} !important;
        border: 1px solid rgba(86,115,137,0.15) !important; /* utilise secondary en outline léger */
        border-radius: {BORDER_RADIUS} !important;
        padding: 12px !important;
    }}

    /* ----- Background léger pour les zones d'accent ----- */
    .accent-bg {{
        background-color: {ACCENT_COLOR}22; /* peu opaque */
        border-radius: {BORDER_RADIUS};
        padding: 8px;
    }}

    /* ----- Metrics (valeurs) ----- */
    .stMetric-value {{
        color: {PRIMARY_COLOR} !important;
        font-weight: 700;
    }}

    /* ----- Inputs / Selectbox / Sliders ----- */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {{
        border-radius: 8px !important;
        border: 1px solid rgba(86,115,137,0.18) !important;
    }}

    /* ----- Lignes de séparation ----- */
    .stMarkdown hr, .css-1v3fvcr hr {{
        border-color: rgba(86,115,137,0.12) !important;
    }}

    /* ----- Graphiques Plotly : exemple d'utilisation de couleurs par défaut (si besoin) ----- */
    .plotly-graph-div .main-svg {{
        /* ce sélecteur n'est qu'illustratif ; les couleurs Plotly se passent idéalement via go.Layout */
    }}

    /* ----- Ajustement responsive (petit polish) ----- */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }}

    /* Cache footer Streamlit (optionnel) */
    footer {{ visibility: hidden; }}

    </style>
    """
    return css
