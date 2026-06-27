# =============================================================================
#  Système d'Analyse et de Prévision des Recettes Fiscales du Cameroun
#  Ministère des Finances (MINFI) — République du Cameroun
#  Application Streamlit (design moderne inspiré Acme dashboard)
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from pathlib import Path
from datetime import datetime
from streamlit_option_menu import option_menu

from utils import (
    load_default_data,
    parse_uploaded_file,
    load_metrics,
    load_previsions_2025,
    load_backtest,
    extend_forecast_multi_year,
    compute_kpis,
    compute_forecast_kpis,
    generate_word_report,
    generate_pdf_report,
)

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Prévisions Recettes Fiscales | MINFI",
    page_icon="₣",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR  = Path(__file__).parent / "assets"
FIGURES_DIR = Path(__file__).parent / "data" / "figures"
LOGO_PATH   = ASSETS_DIR / "minfi_logo.jpeg"
BUILDING_PATH = ASSETS_DIR / "minfi_building.png"

# -----------------------------------------------------------------------------
# Palette de couleurs (inspirée du dashboard Acme : navy + violet)
# -----------------------------------------------------------------------------
NAVY        = "#0F1535"
NAVY_LIGHT  = "#1B1F4E"
PURPLE      = "#4318FF"
PURPLE_LT   = "#7551FF"
ACCENT_GOLD = "#FFB547"
ACCENT_GREEN= "#01B574"
ACCENT_PINK = "#FF5757"
ACCENT_CYAN = "#39B8FF"
TEXT_DARK   = "#1B2559"
TEXT_GRAY   = "#68769F"
BG_LIGHT    = "#F4F7FE"

# -----------------------------------------------------------------------------
# Logo MINFI et image du bâtiment encodés en base64
# -----------------------------------------------------------------------------
b64_logo = ""
if LOGO_PATH.exists():
    with open(LOGO_PATH, "rb") as _f:
        b64_logo = base64.b64encode(_f.read()).decode()

b64_building = ""
if BUILDING_PATH.exists():
    with open(BUILDING_PATH, "rb") as _f:
        b64_building = base64.b64encode(_f.read()).decode()

# -----------------------------------------------------------------------------
# CSS GLOBAL
# -----------------------------------------------------------------------------
CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }}

    /* === Fond d'écran === */
    .stApp {{
        background-color: {BG_LIGHT};
    }}
    [data-testid="stSidebar"] {{
        background: {NAVY} !important;
    }}
</style>
"""

CUSTOM_CSS = CUSTOM_CSS.replace("</style>", "") + f"""

    /* Masquer chrome Streamlit */
    #MainMenu, footer, header {{visibility: hidden;}}
    .block-container {{padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1400px;}}

    /* === SIDEBAR (navy sombre) === */
    [data-testid="stSidebar"] {{
        background: {NAVY} !important;
        border-right: none;
    }}
    [data-testid="stSidebar"] > div {{
        background: {NAVY} !important;
        padding-top: 1rem;
    }}
    [data-testid="stSidebar"] * {{
        color: #E6E9F4 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.08);
        margin: 0.5rem 0 !important;
    }}

    /* Logo container */
    .sidebar-logo {{
        text-align: center;
        padding: 4px 12px 0 12px;
    }}
    .sidebar-logo img {{
        max-width: 140px;
        border-radius: 12px;
        background: white;
        padding: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.20);
    }}
    .sidebar-ministry {{
        text-align: center;
        padding: 12px 12px 4px 12px;
        line-height: 1.35;
    }}
    .sidebar-ministry-name {{
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: 0.2px;
    }}
    .sidebar-ministry-country {{
        font-size: 13px;
        font-weight: 500;
        color: {TEXT_GRAY} !important;
        margin-top: 2px;
    }}

    /* === Header haut === */
    .top-header {{
        background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 50%, {PURPLE} 130%);
        color: white;
        padding: 18px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 30px rgba(15,21,53,0.25);
    }}
    .top-header-title {{
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
    .top-header-sub {{
        font-size: 12px;
        font-weight: 500;
        color: rgba(255,255,255,0.75);
        margin-top: 2px;
    }}
    .top-header-right {{
        font-size: 13px;
        font-weight: 500;
        color: rgba(255,255,255,0.85);
    }}

    /* === KPI CARDS (style Acme) === */
    .kpi-card {{
        background: white;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 4px 24px rgba(112,144,176,0.10);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 170px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 35px rgba(112,144,176,0.20);
    }}
    .kpi-top {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 12px;
    }}
    .kpi-label {{
        font-size: 13px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin: 0;
        letter-spacing: 0.1px;
        line-height: 1.35;
        flex: 1;
        opacity: 0.85;
    }}
    .kpi-body {{
        display: flex;
        flex-direction: column;
    }}
    .kpi-value {{
        font-size: 42px;
        font-weight: 900;
        color: {TEXT_DARK};
        margin: 0;
        line-height: 1.0;
        letter-spacing: -1.2px;
    }}
    .kpi-unit {{
        font-size: 12px;
        font-weight: 600;
        color: {TEXT_DARK};
        opacity: 0.65;
        margin-top: 8px;
        letter-spacing: 0.2px;
    }}
    .kpi-icon-box {{
        width: 44px;
        height: 44px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    }}
    .kpi-delta {{
        font-size: 13px;
        font-weight: 700;
        margin-top: 10px;
        display: inline-block;
        padding: 3px 10px;
        border-radius: 8px;
        align-self: flex-start;
    }}
    .kpi-delta.pos {{color: {ACCENT_GREEN}; background: rgba(1,181,116,0.10);}}
    .kpi-delta.neg {{color: {ACCENT_PINK}; background: rgba(255,87,87,0.10);}}

    /* === Section title === */
    .section-title {{
        font-size: 20px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin: 24px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .section-subtitle {{
        font-size: 13px;
        font-weight: 500;
        color: {TEXT_GRAY};
        margin-top: -8px;
        margin-bottom: 14px;
    }}

    /* === Card générique === */
    .panel {{
        background: white;
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 4px 24px rgba(112,144,176,0.10);
        margin-bottom: 16px;
    }}
    .panel-title {{
        font-size: 17px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin: 0 0 12px 0;
    }}

    /* === Boutons === */
    .stButton > button {{
        background: linear-gradient(135deg, {PURPLE} 0%, {PURPLE_LT} 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(67,24,255,0.25);
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(67,24,255,0.40);
        background: linear-gradient(135deg, {PURPLE_LT} 0%, {PURPLE} 100%);
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {ACCENT_GREEN} 0%, #02C589 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(1,181,116,0.25);
    }}

    /* === Selectbox & inputs === */
    .stSelectbox > div > div, .stTextInput > div > div, .stDateInput > div > div {{
        background: white;
        border-radius: 12px !important;
        border: 1px solid #E0E5F2 !important;
    }}

    /* === Tabs === */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: white;
        padding: 6px;
        border-radius: 14px;
        box-shadow: 0 4px 24px rgba(112,144,176,0.10);
        width: fit-content;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 600;
        color: {TEXT_GRAY};
        font-size: 14px;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {PURPLE} 0%, {PURPLE_LT} 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(67,24,255,0.25);
    }}

    /* === Tableaux === */
    .stDataFrame {{
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(112,144,176,0.08);
    }}

    /* === Markdown h1/h2 === */
    h1 {{color: {TEXT_DARK}; font-weight: 800; letter-spacing: -0.5px;}}
    h2, h3 {{color: {TEXT_DARK}; font-weight: 700;}}

    /* === Info boxes === */
    .info-box {{
        background: linear-gradient(135deg, rgba(67,24,255,0.06) 0%, rgba(117,81,255,0.04) 100%);
        border-left: 4px solid {PURPLE};
        border-radius: 12px;
        padding: 14px 18px;
        font-size: 13px;
        color: {TEXT_DARK};
        line-height: 1.6;
    }}

    /* === Hero homepage === */
    .hero {{
        background: white;
        border-radius: 22px;
        padding: 40px 48px;
        margin-bottom: 28px;
        box-shadow: 0 8px 40px rgba(112,144,176,0.12);
        position: relative;
        overflow: hidden;
    }}
    .hero::before {{
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(67,24,255,0.10) 0%, rgba(67,24,255,0) 70%);
        border-radius: 50%;
    }}
    .hero-title {{
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(135deg, {NAVY} 0%, {PURPLE} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        letter-spacing: -1px;
        margin: 0 0 14px 0;
    }}
    .hero-sub {{
        font-size: 17px;
        color: {TEXT_GRAY};
        font-weight: 500;
        margin: 0;
    }}

    /* === Feature cards homepage === */
    .feature-card {{
        background: white;
        border-radius: 18px;
        padding: 26px 24px;
        box-shadow: 0 4px 24px rgba(112,144,176,0.10);
        height: 100%;
        transition: transform 0.25s ease;
    }}
    .feature-card:hover {{
        transform: translateY(-4px);
    }}
    .feature-icon-box {{
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
    }}
    .feature-title {{
        font-size: 19px;
        font-weight: 700;
        color: {TEXT_DARK};
        margin: 0 0 8px 0;
    }}
    .feature-text {{
        font-size: 14px;
        color: {TEXT_GRAY};
        line-height: 1.6;
        margin: 0;
        font-weight: 500;
    }}

    /* === Radio button (date_input) === */
    .stRadio > label {{font-weight: 600; color: {TEXT_DARK};}}

    /* === Checkbox === */
    .stCheckbox label {{font-size: 14px; color: {TEXT_DARK} !important;}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Icônes SVG inline (style Lucide / line icons)
# -----------------------------------------------------------------------------
def svg_icon(name, color="white", size=24):
    paths = {
        "home":      'M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1h-5v-7h-6v7H4a1 1 0 01-1-1V9.5z',
        "upload":    'M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12',
        "chart":     'M3 3v18h18M7 14l4-4 4 4 5-5',
        "report":    'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M9 13h6 M9 17h4',
        "trending":  'M23 6l-9.5 9.5-5-5L1 18 M17 6h6v6',
        "growth":    'M12 2v20M5 12l7-7 7 7',
        "target":    'M12 12m-10 0a10 10 0 1020 0a10 10 0 10-20 0 M12 12m-6 0a6 6 0 1012 0a6 6 0 10-12 0 M12 12m-2 0a2 2 0 104 0a2 2 0 10-4 0',
        "calendar":  'M19 4H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2zM16 2v4M8 2v4M3 10h18',
        "dollar":    'M12 1v22 M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6',
        "lightning": 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
        "shield":    'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
        "settings":  'M12 15a3 3 0 100-6 3 3 0 000 6z M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09a1.65 1.65 0 001.51-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z',
    }
    p = paths.get(name, paths["home"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{"".join(f"<path d=\\\"{p}\\\"/>")}</svg>'''


def kpi_card(label, value, unit="", icon="dollar", bg=PURPLE, delta=None, delta_label=""):
    """Construit le HTML d'une carte KPI sur une seule ligne pour éviter
    que les indentations soient interprétées comme blocs de code par markdown."""
    delta_html = ""
    if delta is not None:
        cls = "pos" if delta >= 0 else "neg"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = (
            f'<div class="kpi-delta {cls}">{arrow} {delta:+.2f}%'
            f'<span style="color:{TEXT_GRAY}; font-weight:500; font-size:12px; margin-left:6px;">'
            f'{delta_label}</span></div>'
        )

    icon_svg = svg_icon(icon, color="white", size=24)
    bg_grad = f"linear-gradient(135deg, {bg} 0%, {bg}CC 100%)"

    # IMPORTANT : tout sur une seule ligne sans indentation pour échapper au markdown.
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-top">'
        f'<p class="kpi-label">{label}</p>'
        f'<div class="kpi-icon-box" style="background: {bg_grad};">{icon_svg}</div>'
        f'</div>'
        f'<div class="kpi-body">'
        f'<p class="kpi-value">{value}</p>'
        f'<p class="kpi-unit">{unit}</p>'
        f'{delta_html}'
        f'</div>'
        f'</div>'
    )


def section_title(text, icon=None):
    icon_svg = svg_icon(icon, color=PURPLE, size=22) if icon else ""
    st.markdown(f'<div class="section-title">{icon_svg}<span>{text}</span></div>', unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# THÈME PLOTLY GLOBAL (axes bien visibles, typo cohérente)
# -----------------------------------------------------------------------------
def apply_plotly_theme(fig, height=440):
    """Thème Plotly cohérent."""
    fig.update_layout(
        title=dict(text="", font=dict(size=1)),
        font=dict(family="Plus Jakarta Sans", size=13, color=TEXT_DARK),
        plot_bgcolor="white",
        paper_bgcolor="rgba(255,255,255,0.98)",
        height=height,
        margin=dict(l=70, r=40, t=70, b=60),
        hovermode="x unified",
        legend=dict(
            orientation="h", y=1.08, x=0, yanchor="bottom", xanchor="left",
            font=dict(size=12, color=TEXT_DARK, family="Plus Jakarta Sans", weight=600),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="#EDF2F7",
        title_font=dict(size=14, color=TEXT_DARK, weight=700),
        tickfont=dict(size=12, color=TEXT_DARK, weight=600),
        linecolor="#CBD5E0", linewidth=1.5,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="#EDF2F7",
        title_font=dict(size=14, color=TEXT_DARK, weight=700),
        tickfont=dict(size=12, color=TEXT_DARK, weight=600),
        linecolor="#CBD5E0", linewidth=1.5,
    )
    return fig


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    # Logo (b64_logo déjà chargé en haut du fichier)
    if b64_logo:
        st.markdown(
            f'<div class="sidebar-logo"><img src="data:image/jpeg;base64,{b64_logo}"/></div>',
            unsafe_allow_html=True,
        )

    # Nom du ministère (plus gros, moins d'espace)
    st.markdown(
        '<div class="sidebar-ministry">'
        '<p class="sidebar-ministry-name">Ministère des Finances</p>'
        '<p class="sidebar-ministry-country">République du Cameroun</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Menu de navigation avec vraies icônes Bootstrap (via streamlit-option-menu)
    page = option_menu(
        menu_title=None,
        options=["Accueil", "Importation", "Tableau de bord", "Rapport"],
        icons=["house", "cloud-upload", "bar-chart", "file-earmark-text"],
        default_index=0,
        styles={
            "container": {"padding": "0 8px", "background-color": NAVY, "margin-top": "8px"},
            "icon": {"color": TEXT_GRAY, "font-size": "18px"},
            "nav-link": {
                "color": "#C9D1E2",
                "font-size": "15px",
                "font-weight": "600",
                "text-align": "left",
                "padding": "12px 14px",
                "margin": "4px 0",
                "border-radius": "10px",
                "font-family": "Plus Jakarta Sans",
                "--hover-color": NAVY_LIGHT,
            },
            "nav-link-selected": {
                "background-color": PURPLE,
                "color": "white",
                "font-weight": "700",
                "box-shadow": "0 4px 12px rgba(67,24,255,0.30)",
            },
        },
    )

    # Footer sidebar
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        f"""<div style='padding:12px 18px; font-size:11px; color:{TEXT_GRAY};
                       border-top: 1px solid rgba(255,255,255,0.06); margin-top:auto;'>
        v1.0 · Mémoire DSEA 2024<br>
        Outil d'aide à la décision
        </div>""",
        unsafe_allow_html=True,
    )


# =============================================================================
# HEADER HAUT
# =============================================================================
st.markdown(
    f"""<div class='top-header'>
        <div>
            <div class='top-header-title'>Prévisions des Recettes Fiscales du Cameroun</div>
            <div class='top-header-sub'>Outil d'aide à la décision · Machine Learning</div>
        </div>
        <div class='top-header-right'>
            {datetime.now().strftime('%A %d %B %Y').capitalize()}
        </div>
    </div>""",
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================
if "df_data" not in st.session_state:
    st.session_state.df_data = load_default_data()
if "data_source" not in st.session_state:
    st.session_state.data_source = "Jeu de données du mémoire (2010 à 2024)"


# =============================================================================
#                            PAGE 1 : ACCUEIL
# =============================================================================
if page == "Accueil":
    # Fond bâtiment MINFI uniquement sur la page d'accueil
    st.markdown(
        f"""<style>
        .stApp {{
            background-image: url('data:image/png;base64,{b64_building}');
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(180deg,
                        rgba(244,247,254,0.58) 0%,
                        rgba(244,247,254,0.80) 50%,
                        rgba(244,247,254,0.94) 100%);
        }}
        </style>""",
        unsafe_allow_html=True,
    )

    # === HERO ===
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown(
            """<div class='hero'>
                <h1 class='hero-title'>Système d'Analyse et de Prévision des Recettes Fiscales</h1>
                <p class='hero-sub'>République du Cameroun · Ministère des Finances</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_h2:
        if LOGO_PATH.exists():
            st.markdown(
                f"""<div style='display:flex; justify-content:center; align-items:center; height:100%;
                                padding: 12px;'>
                    <img src='data:image/jpeg;base64,{b64_logo}'
                         style='max-width: 180px; border-radius: 16px; background:white;
                                padding: 14px; box-shadow: 0 8px 30px rgba(15,21,53,0.15);'/>
                </div>""",
                unsafe_allow_html=True,
            )

    # === OBJECTIF ===
    st.markdown(
        f"""<div class='panel'>
            <h3 class='panel-title' style='display:flex; align-items:center; gap:10px;'>
                {svg_icon('target', color=PURPLE, size=22)} Objectif de la plateforme
            </h3>
            <p style='color:{TEXT_DARK}; font-size:15px; line-height:1.7; margin:0;'>
            Cet outil d'aide à la décision met à disposition des responsables, analystes et décideurs
            du Ministère des Finances un environnement intégré pour <b>analyser, visualiser et prévoir</b>
            les recettes fiscales du Cameroun. Il s'appuie sur des techniques avancées de
            <b>Machine Learning</b> (XGBoost, Random Forest, Elastic Net, SVR) pour produire des prévisions
            à trois horizons opérationnels : <b>trimestriel, semestriel et annuel</b>, avec quantification
            de l'incertitude par intervalles de confiance à 95 %.
            </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # === 3 FEATURE CARDS ===
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            f"""<div class='feature-card'>
                <div class='feature-icon-box' style='background: rgba(1,181,116,0.12);'>
                    {svg_icon('trending', color=ACCENT_GREEN, size=26)}
                </div>
                <p class='feature-title'>Visualiser les tendances</p>
                <p class='feature-text'>Évolution mensuelle et annuelle des recettes fiscales de 2010 à 2024,
                profils saisonniers et heatmaps année par année.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            f"""<div class='feature-card'>
                <div class='feature-icon-box' style='background: rgba(255,181,71,0.14);'>
                    {svg_icon('lightning', color=ACCENT_GOLD, size=26)}
                </div>
                <p class='feature-title'>Effectuer des prévisions</p>
                <p class='feature-text'>Modèles ML calibrés pour trimestre, semestre et annuel.
                Prévisions multi-années (1 à 3 ans) avec intervalles de confiance à 95 %.</p>
            </div>""",
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            f"""<div class='feature-card'>
                <div class='feature-icon-box' style='background: rgba(67,24,255,0.10);'>
                    {svg_icon('report', color=PURPLE, size=26)}
                </div>
                <p class='feature-title'>Générer des rapports</p>
                <p class='feature-text'>Documents personnalisés Word ou PDF avec en-tête institutionnel,
                indicateurs, graphiques et analyses, prêts pour le reporting.</p>
            </div>""",
            unsafe_allow_html=True,
        )

    # === TABLEAU MODÈLES ===
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Modèles retenus par horizon de prévision", icon="shield")
    st.markdown(
        f"<p style='color:{TEXT_GRAY}; font-size:14px; margin-top:-8px;'>"
        f"Sélection effectuée sur la base de la convergence de plusieurs métriques "
        f"(RMSE, MAE, MAPE, R²) sur l'année test 2024."
        f"</p>",
        unsafe_allow_html=True,
    )

    metrics_overview = pd.DataFrame({
        "Horizon"        : ["Trimestriel (H = 3 mois)", "Semestriel (H = 6 mois)", "Annuel (H = 12 mois)"],
        "Modèle retenu"  : ["XGBoost", "XGBoost", "Random Forest"],
        "RMSE (Mds FCFA)": [29.06, 25.91, 27.73],
        "MAE (Mds FCFA)" : [22.32, 19.81, 22.52],
        "MAPE (%)"       : [6.46, 5.77, 6.66],
        "R²"             : [0.812, 0.851, 0.828],
    })
    st.dataframe(metrics_overview, use_container_width=True, hide_index=True)


# =============================================================================
#                          PAGE 2 : IMPORTATION
# =============================================================================
elif page == "Importation":
    section_title("Importation des données", icon="upload")
    st.markdown(
        f"<p style='color:{TEXT_GRAY}; font-size:14px; margin-top:-8px;'>"
        "Chargez les données nécessaires aux analyses depuis un fichier Excel ou CSV. "
        "Le tableau interactif offre un aperçu immédiat pour validation."
        "</p>",
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns([1, 2])

    with col_l:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Charger les données</p>', unsafe_allow_html=True)

            uploaded = st.file_uploader(
                "Sélectionnez un fichier CSV ou Excel",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
            )

            use_default = st.checkbox(
                "Utiliser le jeu de données du mémoire",
                value=(uploaded is None),
            )

            if uploaded is not None and not use_default:
                try:
                    df_new = parse_uploaded_file(uploaded)
                    st.session_state.df_data = df_new
                    st.session_state.data_source = f"Fichier importé : {uploaded.name}"
                    st.success(f"{len(df_new)} lignes chargées avec succès.")
                except Exception as e:
                    st.error(f"Erreur de chargement : {e}")
            elif use_default:
                st.session_state.df_data = load_default_data()
                st.session_state.data_source = "Jeu de données du mémoire (2010 à 2024)"

        # Filtres
        with st.container(border=True):
            st.markdown('<p class="panel-title">Filtres</p>', unsafe_allow_html=True)

            df = st.session_state.df_data
            idx_ts = df.index.to_timestamp() if hasattr(df.index, "to_timestamp") else df.index
            min_d, max_d = idx_ts.min(), idx_ts.max()

            date_range = st.date_input(
                "Période",
                value=(min_d, max_d), min_value=min_d, max_value=max_d,
            )
            all_vars = df.columns.tolist()
            sel_vars = st.multiselect(
                "Variables à afficher",
                options=all_vars, default=all_vars,
            )

    with col_r:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Aperçu des données</p>', unsafe_allow_html=True)

            df = st.session_state.df_data.copy()

            if isinstance(date_range, tuple) and len(date_range) == 2:
                d0, d1 = date_range
                mask = (idx_ts >= pd.Timestamp(d0)) & (idx_ts <= pd.Timestamp(d1))
                df = df.loc[mask]

            if sel_vars:
                df = df[sel_vars]

            df_show = df.copy()
            if hasattr(df_show.index, "to_timestamp"):
                df_show.insert(0, "Date", df_show.index.to_timestamp().strftime("%Y-%m"))
            else:
                df_show.insert(0, "Date", df_show.index.astype(str))
            df_show = df_show.reset_index(drop=True)

            c_a, c_b = st.columns(2)
            c_a.caption(f"**Source :** {st.session_state.data_source}")
            c_b.caption(f"**Dimensions :** {df_show.shape[0]} lignes × {df_show.shape[1]-1} variables")

            st.dataframe(df_show, use_container_width=True, height=420, hide_index=True)

            with st.expander("Statistiques descriptives"):
                st.dataframe(df.describe().round(2), use_container_width=True)


# =============================================================================
#                       PAGE 3 : TABLEAU DE BORD
# =============================================================================
elif page == "Tableau de bord":
    tab_hist, tab_prev = st.tabs(["Visualisation historique", "Prévision"])

    df = st.session_state.df_data
    df_ts = df.copy()
    if hasattr(df_ts.index, "to_timestamp"):
        df_ts.index = df_ts.index.to_timestamp()

    # ============== ONGLET 1 : VISUALISATION HISTORIQUE ==================
    with tab_hist:
        if "Recettes_fiscales" not in df.columns:
            st.warning("La variable 'Recettes_fiscales' n'est pas présente dans les données.")
        else:
            kpis = compute_kpis(df_ts["Recettes_fiscales"])

            # KPIs (4 colonnes style Acme)
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card(
                "Valeur maximale",
                f"{kpis['max_value']:.1f}",
                f"Mds FCFA · atteint en {kpis['max_date']}",
                icon="lightning", bg=PURPLE,
            ), unsafe_allow_html=True)
            c2.markdown(kpi_card(
                f"Total annuel {kpis['last_year']}",
                f"{kpis['total_last_year']:,.0f}",
                "Mds FCFA",
                icon="growth", bg=ACCENT_GREEN,
                delta=kpis["yoy_total"], delta_label="vs N-1",
            ), unsafe_allow_html=True)
            c3.markdown(kpi_card(
                "Moyenne mensuelle",
                f"{kpis['mean_12m']:.1f}",
                "Mds FCFA · sur 12 mois",
                icon="chart", bg=ACCENT_GOLD,
            ), unsafe_allow_html=True)
            c4.markdown(kpi_card(
                "Volatilité",
                f"{kpis['cv_12m']:.1f}%",
                "Coef. de variation 12 mois",
                icon="trending", bg=ACCENT_CYAN,
            ), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- Graphique principal : évolution mensuelle + MA ---
            section_title("Évolution des recettes fiscales", icon="chart")
            freq = st.radio(
                "Fréquence",
                ["Mensuelle", "Annuelle"],
                horizontal=True, label_visibility="collapsed",
            )

            serie = df_ts["Recettes_fiscales"].dropna()
            if freq == "Mensuelle":
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=serie.index, y=serie.values,
                    mode="lines", name="Recettes fiscales",
                    line=dict(color=PURPLE, width=2.5),
                    fill="tozeroy", fillcolor="rgba(67,24,255,0.08)",
                ))
                ma = serie.rolling(12).mean()
                fig.add_trace(go.Scatter(
                    x=ma.index, y=ma.values,
                    mode="lines", name="Moyenne mobile (12m)",
                    line=dict(color=ACCENT_GOLD, width=2.5, dash="dash"),
                ))
                apply_plotly_theme(fig, height=440)
                fig.update_yaxes(title="Mds FCFA")
                fig.update_xaxes(title="Date")
                st.plotly_chart(fig, use_container_width=True)
            else:
                annual = serie.resample("YE").sum()
                annual.index = annual.index.year
                colors = [PURPLE if i != len(annual)-1 else ACCENT_GREEN for i in range(len(annual))]
                fig = go.Figure(go.Bar(
                    x=annual.index, y=annual.values,
                    marker_color=colors,
                    text=[f"{v:,.0f}" for v in annual.values],
                    textposition="outside",
                    textfont=dict(size=11, weight=600, color=TEXT_DARK),
                ))
                apply_plotly_theme(fig, height=440)
                fig.update_yaxes(title="Mds FCFA")
                fig.update_xaxes(title="Année", tickmode="linear")
                st.plotly_chart(fig, use_container_width=True)

            # --- Heatmap année × mois (REMPLACE le graphe non pertinent) ---
            section_title("Heatmap : recettes par mois et par année", icon="calendar")
            st.markdown(
                f"<p style='color:{TEXT_GRAY}; font-size:13px; margin-top:-8px;'>"
                "Détecte les mois clés de collecte et l'évolution structurelle annuelle. "
                "Les cellules les plus foncées indiquent les pics de collecte."
                "</p>",
                unsafe_allow_html=True,
            )
            pivot = serie.copy()
            pivot.index = pd.MultiIndex.from_arrays(
                [pivot.index.year, pivot.index.month],
                names=["Année", "Mois"],
            )
            pivot = pivot.unstack(level="Mois")
            mois_lbl = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
            pivot.columns = mois_lbl[:pivot.shape[1]]

            fig_hm = go.Figure(data=go.Heatmap(
                z=pivot.values, x=pivot.columns, y=pivot.index.astype(str),
                colorscale=[[0, "#F4F7FE"], [0.5, "#7551FF"], [1, "#0F1535"]],
                colorbar=dict(
                    title=dict(text="Mds FCFA", font=dict(size=12)),
                    tickfont=dict(size=11),
                ),
                hovertemplate="<b>%{y} · %{x}</b><br>%{z:.1f} Mds FCFA<extra></extra>",
            ))
            apply_plotly_theme(fig_hm, height=440)
            fig_hm.update_yaxes(title="Année", autorange="reversed")
            fig_hm.update_xaxes(title="Mois", side="top")
            st.plotly_chart(fig_hm, use_container_width=True)

            # --- Matrice de corrélations (Pearson et Spearman) ---
            section_title("Corrélations avec les variables exogènes", icon="lightning")
            st.markdown(
                f"<p style='color:{TEXT_GRAY}; font-size:13px; margin-top:-8px;'>"
                "Coefficients de corrélation de <b>Pearson</b> (relation linéaire) et de "
                "<b>Spearman</b> (relation monotone, robuste aux valeurs extrêmes) entre les "
                "recettes fiscales et chaque variable exogène. Les valeurs proches de ±1 "
                "indiquent une forte association ; le signe en donne le sens."
                "</p>",
                unsafe_allow_html=True,
            )

            exog_cols = [c for c in df_ts.columns if c != "Recettes_fiscales"]
            if len(exog_cols) > 0:
                df_corr = df_ts[exog_cols + ["Recettes_fiscales"]].dropna()
                corr_p = df_corr.corr(method="pearson")["Recettes_fiscales"].drop("Recettes_fiscales")
                corr_s = df_corr.corr(method="spearman")["Recettes_fiscales"].drop("Recettes_fiscales")

                # Tri par |Pearson| décroissant (top des plus corrélées en haut visuel)
                order = corr_p.abs().sort_values(ascending=True).index.tolist()
                corr_p = corr_p.reindex(order)
                corr_s = corr_s.reindex(order)

                fig_corr = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("Pearson", "Spearman"),
                    horizontal_spacing=0.18,
                )

                fig_corr.add_trace(
                    go.Bar(
                        y=order, x=corr_p.values, orientation="h",
                        marker_color=[PURPLE if v >= 0 else ACCENT_PINK for v in corr_p.values],
                        text=[f"{v:+.2f}" for v in corr_p.values],
                        textposition="outside",
                        textfont=dict(size=11, color=TEXT_DARK, weight=700),
                        showlegend=False,
                        hovertemplate="<b>%{y}</b><br>Pearson : %{x:.3f}<extra></extra>",
                    ),
                    row=1, col=1,
                )
                fig_corr.add_trace(
                    go.Bar(
                        y=order, x=corr_s.values, orientation="h",
                        marker_color=[ACCENT_GREEN if v >= 0 else ACCENT_GOLD for v in corr_s.values],
                        text=[f"{v:+.2f}" for v in corr_s.values],
                        textposition="outside",
                        textfont=dict(size=11, color=TEXT_DARK, weight=700),
                        showlegend=False,
                        hovertemplate="<b>%{y}</b><br>Spearman : %{x:.3f}<extra></extra>",
                    ),
                    row=1, col=2,
                )

                apply_plotly_theme(fig_corr, height=max(380, 28 * len(order) + 90))
                fig_corr.update_xaxes(range=[-1.15, 1.15], title="Coefficient",
                                      zeroline=True, zerolinecolor="#CBD5E0", zerolinewidth=1)
                fig_corr.update_yaxes(title=None)
                # Styliser les sous-titres
                for ann in fig_corr.layout.annotations:
                    ann.font = dict(size=14, color=TEXT_DARK, family="Plus Jakarta Sans", weight=700)
                st.plotly_chart(fig_corr, use_container_width=True)

            # --- Profil saisonnier ---
            section_title("Profil saisonnier moyen", icon="calendar")
            saison = serie.groupby(serie.index.month).agg(["mean", "std"])
            saison.index = mois_lbl[:len(saison)]

            fig_s = go.Figure()
            fig_s.add_trace(go.Bar(
                x=saison.index, y=saison["mean"],
                error_y=dict(type="data", array=saison["std"], color="#A3AED0", thickness=1.5),
                marker=dict(color=PURPLE,
                            line=dict(color=NAVY, width=0)),
                text=[f"{v:.0f}" for v in saison["mean"]],
                textposition="outside",
                textfont=dict(size=11, weight=600, color=TEXT_DARK),
                hovertemplate="<b>%{x}</b><br>Moyenne : %{y:.1f} Mds FCFA<extra></extra>",
                showlegend=False,
            ))
            apply_plotly_theme(fig_s, height=400)
            fig_s.update_yaxes(title="Mds FCFA")
            fig_s.update_xaxes(title="Mois")
            st.plotly_chart(fig_s, use_container_width=True)

            # --- Évolution des variables exogènes (groupées par unité) ---
            section_title("Évolution des variables exogènes", icon="trending")
            st.markdown(
                f"<p style='color:{TEXT_GRAY}; font-size:13px; margin-top:-8px;'>"
                "Suivi des indicateurs économiques utilisés par le modèle, "
                "regroupés par unité de mesure pour une comparaison pertinente. "
                "Sélectionnez ci-dessous le groupe à afficher."
                "</p>",
                unsafe_allow_html=True,
            )

            # Définition des groupes par unité
            unit_groups = {
                "Comptes publics (Mds FCFA)":             ["Recettes_fiscales", "Depenses_pub", "Solde_budg"],
                "Prix agricoles ($/kg)":                  ["Prix_cacao", "Prix_cafe_Robusta", "Prix_coton"],
                "Indices économiques mondiaux (base 100)":["REER", "Indice_prix_alim_FAO", "Indice_engrais"],
                "Énergie et céréales (axes distincts)":   ["Prix_petrole_Brent", "Prix_riz_composite"],
                "Climat (axes distincts)":                ["Temp_moy", "Precipitations"],
            }
            unit_units = {
                "Comptes publics (Mds FCFA)":             "Mds FCFA",
                "Prix agricoles ($/kg)":                  "$/kg",
                "Indices économiques mondiaux (base 100)":"Indice",
                "Énergie et céréales (axes distincts)":   ("$/bbl (Brent)", "$/mt (Riz)"),
                "Climat (axes distincts)":                ("°C (Température)", "mm (Précipitations)"),
            }
            # Filtre selon les colonnes disponibles
            unit_groups = {
                name: [c for c in cols if c in df_ts.columns]
                for name, cols in unit_groups.items()
            }
            unit_groups = {k: v for k, v in unit_groups.items() if len(v) >= 1}

            if unit_groups:
                group_choice = st.radio(
                    "Groupe de variables",
                    options=list(unit_groups.keys()),
                    horizontal=True,
                    label_visibility="collapsed",
                )

                cols_sel = unit_groups[group_choice]
                palette_exog = [PURPLE, ACCENT_GREEN, ACCENT_GOLD, ACCENT_PINK, ACCENT_CYAN, NAVY, "#8B5CF6"]

                if "distincts" in group_choice and len(cols_sel) >= 2:
                    # Double axe Y
                    fig_g = make_subplots(specs=[[{"secondary_y": True}]])
                    fig_g.add_trace(
                        go.Scatter(x=df_ts.index, y=df_ts[cols_sel[0]],
                                   mode="lines", name=cols_sel[0],
                                   line=dict(color=PURPLE, width=2.3)),
                        secondary_y=False,
                    )
                    fig_g.add_trace(
                        go.Scatter(x=df_ts.index, y=df_ts[cols_sel[1]],
                                   mode="lines", name=cols_sel[1],
                                   line=dict(color=ACCENT_GOLD, width=2.3)),
                        secondary_y=True,
                    )
                    apply_plotly_theme(fig_g, height=440)
                    units = unit_units[group_choice]
                    fig_g.update_yaxes(title_text=units[0] if isinstance(units, tuple) else units, secondary_y=False)
                    fig_g.update_yaxes(title_text=units[1] if isinstance(units, tuple) else "", secondary_y=True)
                    fig_g.update_xaxes(title_text="Date")
                else:
                    # Axe Y unique (même unité)
                    fig_g = go.Figure()
                    for i, var in enumerate(cols_sel):
                        fig_g.add_trace(go.Scatter(
                            x=df_ts.index, y=df_ts[var],
                            mode="lines", name=var,
                            line=dict(color=palette_exog[i % len(palette_exog)], width=2.3),
                        ))
                    apply_plotly_theme(fig_g, height=440)
                    fig_g.update_yaxes(title=unit_units.get(group_choice, ""))
                    fig_g.update_xaxes(title="Date")

                st.plotly_chart(fig_g, use_container_width=True)
            else:
                st.info("Aucune variable exogène disponible dans les données chargées.")

    # ==================== ONGLET 2 : PRÉVISION ============================
    with tab_prev:
        col_p1, col_p2 = st.columns([1, 2])

        with col_p1:
            with st.container(border=True):
                st.markdown('<p class="panel-title">Paramètres de prévision</p>', unsafe_allow_html=True)

                horizon = st.selectbox(
                    "Horizon de prévision",
                    options=[3, 6, 12],
                    format_func=lambda h: {
                        3:  "3 mois · Trimestriel",
                        6:  "6 mois · Semestriel",
                        12: "12 mois · Annuel",
                    }[h],
                )

                n_years = 1
                if horizon == 12:
                    n_years = st.selectbox(
                        "Nombre d'années à projeter",
                        options=[1, 2, 3],
                        format_func=lambda n: f"{n} an{'s' if n > 1 else ''}",
                    )

                # Nom du modèle retenu selon l'horizon
                best_model_name = "Random Forest" if horizon == 12 else "XGBoost"
                best_model_reason = (
                    "domine sur les métriques RMSE et R² tout en restant compétitif sur MAE et MAPE"
                    if horizon == 12
                    else "domine simultanément sur les quatre métriques (RMSE, MAE, MAPE, R²)"
                )

                st.markdown(
                    f"""<div class='info-box' style='margin-top:14px;'>
                    <b>Modèle retenu</b> : {best_model_name} a été sélectionné pour cet horizon car il
                    {best_model_reason}, évalué sur l'année test 2024.
                    </div>""",
                    unsafe_allow_html=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)
                run_btn = st.button("Lancer la prévision", use_container_width=True)

        with col_p2:
            with st.container(border=True):
                st.markdown('<p class="panel-title">Performance comparée des modèles</p>', unsafe_allow_html=True)
                metrics_df = load_metrics(horizon)
                if metrics_df is not None:
                    m = metrics_df.copy()
                    m["RMSE"] = m["RMSE"].round(2)
                    m["MAE"]  = m["MAE"].round(2)
                    m["MAPE"] = m["MAPE"].round(2)
                    m["R2"]   = m["R2"].round(4)
                    best_idx = m["RMSE"].idxmin()

                    def _hl(row):
                        if row.name == best_idx:
                            return [f"background-color:{PURPLE}; color:white; font-weight:700"] * len(row)
                        return [""] * len(row)

                    st.dataframe(
                        m.style.apply(_hl, axis=1),
                        use_container_width=True, hide_index=True,
                    )
                    st.caption(f"Ligne en violet : modèle retenu pour cet horizon.")

        # === Résultats prévision ===
        if run_btn or st.session_state.get("forecast_done"):
            st.session_state.forecast_done = True
            st.session_state.forecast_horizon = horizon
            st.session_state.forecast_nyears = n_years

            # Récupération
            if horizon == 12 and n_years > 1:
                prev_df, by_year = extend_forecast_multi_year(
                    df_ts, n_years=n_years,
                )
            else:
                prev_df = load_previsions_2025(horizon)
                by_year = None

            if prev_df is None or prev_df.empty:
                st.error("Impossible de charger les prévisions.")
            else:
                # === KPIs prévision pertinents ===
                fkpis = compute_forecast_kpis(prev_df, df_ts, horizon, metrics_df)
                k1, k2, k3 = st.columns(3)

                k1.markdown(kpi_card(
                    "Total prévu",
                    f"{fkpis['total']:,.0f}",
                    f"Mds FCFA · {len(prev_df)} mois",
                    icon="dollar", bg=PURPLE,
                ), unsafe_allow_html=True)
                k2.markdown(kpi_card(
                    "Croissance attendue",
                    f"{fkpis['growth']:+.1f}%",
                    f"vs {fkpis['ref_year']}",
                    icon="growth",
                    bg=(ACCENT_GREEN if fkpis['growth'] >= 0 else ACCENT_PINK),
                ), unsafe_allow_html=True)
                k3.markdown(kpi_card(
                    "Précision modèle",
                    f"{fkpis['mape']:.2f}%",
                    "MAPE sur test",
                    icon="shield", bg=ACCENT_CYAN,
                ), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # === Graphique prévision ===
                section_title("Trajectoire prévue", icon="trending")
                serie_hist = df_ts["Recettes_fiscales"].dropna().tail(36)
                prev_dates = pd.to_datetime(prev_df["Mois"] + "-01")

                fig_p = go.Figure()
                fig_p.add_trace(go.Scatter(
                    x=serie_hist.index, y=serie_hist.values,
                    mode="lines+markers", name="Historique (36 derniers mois)",
                    line=dict(color=NAVY, width=2),
                    marker=dict(size=5),
                ))
                fig_p.add_trace(go.Scatter(
                    x=prev_dates, y=prev_df["Prévision (Mds)"],
                    mode="lines+markers", name=f"Prévision (H = {horizon} mois)",
                    line=dict(color=PURPLE, width=2.8),
                    marker=dict(size=8, symbol="diamond"),
                ))
                fig_p.add_trace(go.Scatter(
                    x=list(prev_dates) + list(prev_dates[::-1]),
                    y=list(prev_df["IC haut 95%"]) + list(prev_df["IC bas 95%"][::-1]),
                    fill="toself", fillcolor="rgba(67,24,255,0.13)",
                    line=dict(color="rgba(255,255,255,0)"),
                    name="Intervalle de confiance 95 %",
                ))
                apply_plotly_theme(fig_p, height=460)
                fig_p.update_yaxes(title="Mds FCFA")
                fig_p.update_xaxes(title="Date")
                st.plotly_chart(fig_p, use_container_width=True)

                # === Tableau & synthèse ===
                ca, cb = st.columns([3, 2])
                with ca:
                    with st.container(border=True):
                        st.markdown('<p class="panel-title">Tableau des prévisions mensuelles</p>', unsafe_allow_html=True)
                        st.dataframe(prev_df.round(2), use_container_width=True, hide_index=True, height=400)

                with cb:
                    with st.container(border=True):
                        st.markdown('<p class="panel-title">Synthèse</p>', unsafe_allow_html=True)
                        if by_year is not None:
                            # cumul par année (sans total inter-années)
                            for yr, total in by_year.items():
                                st.markdown(
                                    f"""<div style='background:{BG_LIGHT}; padding:14px 18px; border-radius:12px;
                                                    margin-bottom:10px; border-left: 4px solid {PURPLE};'>
                                        <div style='font-size:13px; color:{TEXT_GRAY}; font-weight:600;'>Cumul {yr}</div>
                                        <div style='font-size:24px; color:{TEXT_DARK}; font-weight:800;'>{total:,.0f} Mds</div>
                                    </div>""",
                                    unsafe_allow_html=True,
                                )
                        else:
                            tot = prev_df["Prévision (Mds)"].sum()
                            st.markdown(
                                f"""<div style='background:{BG_LIGHT}; padding:14px 18px; border-radius:12px;
                                                margin-bottom:10px; border-left: 4px solid {PURPLE};'>
                                    <div style='font-size:13px; color:{TEXT_GRAY}; font-weight:600;'>Cumul sur {horizon} mois</div>
                                    <div style='font-size:24px; color:{TEXT_DARK}; font-weight:800;'>{tot:,.0f} Mds</div>
                                </div>""",
                                unsafe_allow_html=True,
                            )

                        moy = prev_df["Prévision (Mds)"].mean()
                        st.markdown(
                            f"""<div style='background:{BG_LIGHT}; padding:14px 18px; border-radius:12px;
                                            margin-bottom:10px; border-left: 4px solid {ACCENT_GREEN};'>
                                <div style='font-size:13px; color:{TEXT_GRAY}; font-weight:600;'>Moyenne mensuelle prévue</div>
                                <div style='font-size:24px; color:{TEXT_DARK}; font-weight:800;'>{moy:,.1f} Mds</div>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                # === Comparaison Prévu vs Réel (2024) ===
                bt = load_backtest(horizon, year=2024)
                if bt is not None:
                    section_title("Validation sur 2024 (comparaison prévu vs réel)", icon="shield")
                    st.markdown(
                        f"<p style='color:{TEXT_GRAY}; font-size:13px; margin-top:-8px;'>"
                        "Confronte les prévisions du modèle aux valeurs réellement observées sur 2024 "
                        "pour évaluer la qualité opérationnelle des prévisions."
                        "</p>",
                        unsafe_allow_html=True,
                    )
                    fig_bt = go.Figure()
                    fig_bt.add_trace(go.Bar(
                        x=bt["Mois"], y=bt["Réel (Mds)"],
                        name="Réel 2024", marker_color=NAVY,
                    ))
                    fig_bt.add_trace(go.Bar(
                        x=bt["Mois"], y=bt["Prévu (Mds)"],
                        name="Prévu par le modèle", marker_color=PURPLE_LT,
                    ))
                    apply_plotly_theme(fig_bt, height=400)
                    fig_bt.update_yaxes(title="Mds FCFA")
                    fig_bt.update_xaxes(title="Mois")
                    fig_bt.update_layout(barmode="group")
                    st.plotly_chart(fig_bt, use_container_width=True)
                    st.dataframe(bt.round(2), use_container_width=True, hide_index=True)

                # === SHAP : variables les plus contributives ===
                section_title("Variables les plus contributives au modèle", icon="lightning")
                st.markdown(
                    f"<p style='color:{TEXT_GRAY}; font-size:13px; margin-top:-8px;'>"
                    "Importance des variables explicatives selon les valeurs SHAP. "
                    "Plus la barre est longue, plus la variable contribue à la prévision."
                    "</p>",
                    unsafe_allow_html=True,
                )

                shap_path = FIGURES_DIR / f"11_SHAP_XGBoost_H{horizon}.png"
                rf_path   = FIGURES_DIR / f"12_importance_RF_H{horizon}.png"

                cs1, cs2 = st.columns(2)
                with cs1:
                    st.markdown(f"<p style='font-weight:700; color:{TEXT_DARK};'>SHAP · XGBoost (H = {horizon})</p>", unsafe_allow_html=True)
                    if shap_path.exists():
                        st.image(str(shap_path), use_column_width=True)
                    else:
                        st.info("Graphique SHAP non disponible.")
                with cs2:
                    st.markdown(f"<p style='font-weight:700; color:{TEXT_DARK};'>Feature importance · Random Forest (H = {horizon})</p>", unsafe_allow_html=True)
                    if rf_path.exists():
                        st.image(str(rf_path), use_column_width=True)
                    else:
                        st.info("Graphique RF non disponible.")


# =============================================================================
#                            PAGE 4 : RAPPORT
# =============================================================================
elif page == "Rapport":
    section_title("Génération de rapports", icon="report")
    st.markdown(
        f"<p style='color:{TEXT_GRAY}; font-size:14px; margin-top:-8px;'>"
        "Produisez des documents personnalisés au format Word ou PDF intégrant en-tête institutionnel, "
        "indicateurs, graphiques et analyses."
        "</p>",
        unsafe_allow_html=True,
    )

    col_form, col_prev = st.columns([1, 1.4])

    with col_form:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Paramètres du rapport</p>', unsafe_allow_html=True)

            fmt = st.selectbox("Format du rapport", ["Word (.docx)", "PDF (.pdf)"])
            titre = st.text_input(
                "Intitulé du rapport",
                value="Rapport sur les Recettes Fiscales du Cameroun",
            )
            horizon_rap = st.selectbox(
                "Horizon analysé",
                options=[3, 6, 12],
                format_func=lambda h: f"{h} mois · {['Trimestriel','Semestriel','Annuel'][[3,6,12].index(h)]}",
            )

            n_years_rap = 1
            if horizon_rap == 12:
                n_years_rap = st.selectbox(
                    "Nombre d'années à projeter",
                    [1, 2, 3], format_func=lambda n: f"{n} an{'s' if n>1 else ''}",
                )

            st.markdown('<p style="font-weight:700; color:#1B2559; margin-top:18px;">Sections à inclure</p>', unsafe_allow_html=True)
            inc_kpis = st.checkbox("Indicateurs clés et synthèse", value=True)
            inc_hist = st.checkbox("Graphique historique",          value=True)
            inc_prev = st.checkbox("Tableau et graphique de prévision", value=True)
            inc_val  = st.checkbox("Validation sur 2024",           value=True)
            inc_mtr  = st.checkbox("Comparaison des modèles",       value=False)
            inc_shap = st.checkbox("Analyse SHAP des variables",    value=False)
            inc_meth = st.checkbox("Méthodologie complète",         value=False)

        # Niveau de détail = compteur des sections cochées
        sections = [inc_kpis, inc_hist, inc_prev, inc_val, inc_mtr, inc_shap, inc_meth]
        n_inc = sum(sections)
        if n_inc <= 2:
            niv_label, niv_color = "Synthèse rapide", ACCENT_CYAN
        elif n_inc <= 4:
            niv_label, niv_color = "Rapport standard", PURPLE
        elif n_inc <= 6:
            niv_label, niv_color = "Rapport complet", ACCENT_GREEN
        else:
            niv_label, niv_color = "Rapport exhaustif", ACCENT_GOLD

        st.markdown(
            f"""<div style='background: white; border-radius:12px; padding:14px 18px;
                            box-shadow:0 4px 24px rgba(112,144,176,0.10); margin-top:14px;
                            border-left: 4px solid {niv_color};'>
                <div style='font-size:13px; color:{TEXT_GRAY}; font-weight:600;'>Niveau de détail</div>
                <div style='font-size:18px; color:{TEXT_DARK}; font-weight:800;'>{niv_label}</div>
                <div style='font-size:12px; color:{TEXT_GRAY}; margin-top:4px;'>
                    {n_inc} / 7 sections incluses
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        gen_btn = st.button("Générer le rapport", use_container_width=True)

    with col_prev:
        with st.container(border=True):
            st.markdown('<p class="panel-title">Aperçu du contenu</p>', unsafe_allow_html=True)

            df = st.session_state.df_data
            df_ts = df.copy()
            if hasattr(df_ts.index, "to_timestamp"):
                df_ts.index = df_ts.index.to_timestamp()

            kpis     = compute_kpis(df_ts["Recettes_fiscales"]) if "Recettes_fiscales" in df.columns else None
            metrics  = load_metrics(horizon_rap)

            if horizon_rap == 12 and n_years_rap > 1:
                prev_df, by_year = extend_forecast_multi_year(df_ts, n_years=n_years_rap)
            else:
                prev_df = load_previsions_2025(horizon_rap)
                by_year = None

            backtest = load_backtest(horizon_rap, year=2024)
            fkpis = compute_forecast_kpis(prev_df, df_ts, horizon_rap, metrics) if prev_df is not None else None

            # Entête institutionnel mock
            if LOGO_PATH.exists():
                st.markdown(
                    f"""<div style='display:flex; align-items:center; gap:18px;
                                    border-bottom: 3px solid {PURPLE}; padding-bottom: 16px;'>
                        <img src='data:image/jpeg;base64,{b64_logo}'
                             style='width:80px; height:80px; border-radius:12px; background:white;
                                    padding:6px; box-shadow: 0 2px 8px rgba(0,0,0,0.10);'/>
                        <div>
                            <div style='font-size:11px; color:{TEXT_GRAY}; font-weight:600; letter-spacing:0.8px;'>
                                RÉPUBLIQUE DU CAMEROUN
                            </div>
                            <div style='font-size:15px; color:{TEXT_DARK}; font-weight:700;'>
                                Ministère des Finances
                            </div>
                            <div style='font-size:11px; color:{TEXT_GRAY}; font-style:italic;'>
                                Paix · Travail · Patrie
                            </div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown(f"<h2 style='margin-top: 18px; color:{TEXT_DARK};'>{titre}</h2>", unsafe_allow_html=True)
            st.caption(
                f"Horizon de prévision : {horizon_rap} mois "
                f"{f'sur {n_years_rap} ans' if horizon_rap==12 and n_years_rap>1 else ''}"
                f" · Modèle {'Random Forest' if horizon_rap == 12 else 'XGBoost'} · Édité le {datetime.now().strftime('%d / %m / %Y')}"
            )
            st.markdown("---")

            if inc_kpis and kpis:
                st.markdown("**Indicateurs clés**")
                st.markdown(
                    f"- Dernière valeur : **{kpis['last_value']:.2f} Mds FCFA** ({kpis['last_date']})\n"
                    f"- Total {kpis['last_year']} : **{kpis['total_last_year']:,.0f} Mds FCFA** ({kpis['yoy_total']:+.2f}% vs année précédente)\n"
                    f"- Moyenne sur 12 mois : **{kpis['mean_12m']:.2f} Mds FCFA**\n"
                    f"- Coefficient de variation : **{kpis['cv_12m']:.1f}%**"
                )

            if inc_prev and prev_df is not None and fkpis is not None:
                st.markdown(f"**Prévisions à {horizon_rap} mois**")
                st.markdown(
                    f"- Total prévu : **{fkpis['total']:,.0f} Mds FCFA**\n"
                    f"- Croissance attendue : **{fkpis['growth']:+.2f}%** vs {fkpis['ref_year']}\n"
                    f"- Précision du modèle (MAPE test) : **{fkpis['mape']:.2f}%**"
                )
                st.dataframe(prev_df.round(2), use_container_width=True, hide_index=True)

                if by_year is not None:
                    st.markdown("**Cumul par année**")
                    for yr, total in by_year.items():
                        st.markdown(f"- Année {yr} : **{total:,.0f} Mds FCFA**")

            if inc_mtr and metrics is not None:
                st.markdown("**Performance comparée des modèles**")
                st.dataframe(metrics.round(3), use_container_width=True, hide_index=True)

            if inc_val and backtest is not None:
                st.markdown("**Validation sur 2024**")
                mape_bt = backtest["Écart (%)"].abs().mean()
                st.markdown(f"MAPE constatée sur 2024 : **{mape_bt:.2f}%**")
                st.dataframe(backtest.round(2), use_container_width=True, hide_index=True)

            if inc_shap:
                st.markdown("**Analyse SHAP**")
                st.markdown(
                    "Sera intégrée dans le document : graphique d'importance "
                    "des variables explicatives selon les valeurs SHAP."
                )

            if inc_meth:
                st.markdown("**Méthodologie**")
                st.markdown(
                    "Sera détaillée dans le document : architecture des modèles, "
                    "ingénierie des features, validation croisée, sélection."
                )

        if gen_btn:
            with st.spinner("Génération du rapport..."):
                try:
                    figures_dir = FIGURES_DIR if (inc_shap or inc_prev) else None
                    kwargs = dict(
                        titre=titre, horizon=horizon_rap, n_years=n_years_rap,
                        kpis=kpis, metrics_d=metrics, prev_df=prev_df, by_year=by_year,
                        backtest=backtest, fkpis=fkpis,
                        include_kpis=inc_kpis, include_hist=inc_hist, include_prev=inc_prev,
                        include_val=inc_val,   include_mtr=inc_mtr,   include_shap=inc_shap,
                        include_meth=inc_meth, df_hist=df_ts, logo_path=str(LOGO_PATH),
                        figures_dir=str(FIGURES_DIR),
                    )
                    if fmt.startswith("Word"):
                        file_bytes = generate_word_report(**kwargs)
                        st.download_button(
                            "Télécharger le rapport Word",
                            data=file_bytes,
                            file_name=f"{titre.replace(' ','_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                        )
                    else:
                        file_bytes = generate_pdf_report(**kwargs)
                        st.download_button(
                            "Télécharger le rapport PDF",
                            data=file_bytes,
                            file_name=f"{titre.replace(' ','_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    st.success("Rapport généré avec succès.")
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
                    import traceback
                    st.code(traceback.format_exc())
