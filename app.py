import streamlit as st
import json
import time
import io
import re
import html
import hashlib
import base64
import qrcode
import random

from pathlib import Path

from dotenv import load_dotenv

from zamy_ai import (
    detectar_mime,
    ia_disponible,
    interpretar_pedido,
    transcribir_audio,
)

load_dotenv()

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Zamy - Atención & Menú Digital",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS con Paleta McDonald's, Tipografía Arial y Tarjetas PedidosYa
MCD_RED = "#DA291C"
MCD_YELLOW = "#FFC72C"
MCD_DARK = "#27251F"
MCD_BG = "#F4F6F8"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap');
    html, body, [class*="css"], div, p, span, h1, h2, h3, h4, h5, h6, button, input, textarea {{
        font-family: "Lato", "Segoe UI", Arial, sans-serif !important;
    }}
    /* Fondo principal y contenedor */
    .stApp {{
        background-color: #FFFFFF;
    }}

    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}

    /* Oculta la barra de herramientas de Streamlit (Deploy / Stop / menú) */
    header[data-testid="stHeader"] {{
        display: none;
    }}

    /* Navbar Superior */
    .top-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        padding: 6px 2px 14px 2px;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 12px;
    }}

    .nav-actions {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }}

    .nav-logo {{
        height: 60px;
        width: auto;
        max-width: 100%;
        display: block;
        object-fit: contain;
    }}
    
    .logo-title {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.7rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: #111111;
        min-width: 0;
    }}
    
    .logo-badge {{
        background-color: #E7F6EF;
        color: #12805C;
        font-size: 0.85rem;
        padding: 5px 14px;
        border-radius: 999px;
        font-weight: 700;
    }}
    
    .btn-top-alert {{
        background-color: #E2231A;
        color: white;
        font-weight: 800;
        padding: 9px 18px;
        border-radius: 999px;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }}

    .brand-mark {{
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #FFF1EC;
        border: 1px solid #F6D9D2;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
    }}

    .dot {{
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #16A34A;
        margin-right: 6px;
    }}
    
    /* Titular Principal */
    .main-hero-title {{
        font-size: 2.1rem;
        font-weight: 800;
        color: {MCD_DARK};
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 15px;
    }}

    .realtime-tag {{
        background-color: #E6F4EA;
        color: #00875A;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }}

    .hero-subtitle {{
        color: #5F6368;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }}
    
    /* Tarjetas principales estilo voz */
    .voice-card {{
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EAEAEA;
        height: 100%;
    }}

    .voice-card-header {{
        font-size: 1.15rem;
        font-weight: bold;
        color: {MCD_DARK};
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .assistant-badge {{
        background-color: #E8F0FE;
        color: #1A73E8;
        font-size: 0.85rem;
        padding: 6px 14px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
    }}

    .assistant-profile {{
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }}

    .assistant-avatar {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, {MCD_RED}, {MCD_YELLOW});
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        box-shadow: 0 4px 12px rgba(218, 41, 28, 0.3);
    }}

    /* Tarjeta de interpretación del pedido (IA) */
    .ia-card {{
        background-color: white;
        border: 1px solid #EAEAEA;
        border-left: 5px solid #1A73E8;
        border-radius: 14px;
        padding: 18px;
        margin-top: 16px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.05);
    }}

    .ia-card-title {{
        font-size: 1rem;
        font-weight: 800;
        color: {MCD_DARK};
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }}

    .ia-chip {{
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 10px;
        background-color: #E8F0FE;
        color: #1A73E8;
        text-transform: uppercase;
        letter-spacing: .03em;
    }}

    .ia-item {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #F1F1F1;
        font-size: 0.93rem;
        color: #343A40;
    }}

    .ia-note {{
        font-size: 0.79rem;
        color: #6C757D;
        margin-top: 2px;
    }}

    .ia-warn {{
        background-color: #FFF4E5;
        border: 1px solid #FFE0B2;
        color: #8A4B00;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.83rem;
        margin-top: 10px;
    }}

    .ia-hint {{
        background-color: #F1F3F5;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.83rem;
        color: #495057;
        margin-top: 10px;
    }}

    /* ==========================================
       ESTILOS TARJETAS MENÚ TIPO PEDIDOS YA
       ========================================== */
    .pedidosya-card {{
        background-color: white;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #EAEAEA;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 20px;
    }}

    .pedidosya-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }}

    .pedidosya-img-box {{
        position: relative;
        height: 180px;
        width: 100%;
        background-size: cover;
        background-position: center;
    }}

    .pedidosya-badge-top {{
        position: absolute;
        top: 12px;
        left: 12px;
        background-color: #00C9A7;
        color: white;
        font-weight: 800;
        font-size: 0.78rem;
        padding: 5px 12px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }}

    .pedidosya-info-body {{
        padding: 16px;
    }}

    .pedidosya-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }}

    .pedidosya-title {{
        font-size: 1.1rem;
        font-weight: 800;
        color: #000000;
        margin: 0;
        line-height: 1.25;
    }}

    .pedidosya-rating {{
        font-size: 0.9rem;
        font-weight: 800;
        color: {MCD_DARK};
        display: flex;
        align-items: center;
        gap: 3px;
    }}

    .pedidosya-sub-details {{
        display: flex;
        gap: 15px;
        color: #6C757D;
        font-size: 0.85rem;
        margin-top: 8px;
        font-weight: 600;
    }}

    .pedidosya-price-tag {{
        color: {MCD_RED};
        font-size: 1.25rem;
        font-weight: 900;
        margin-top: 10px;
    }}

    /* Estilo de pestañas: píldoras de navegación */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
        border: none;
        padding: 0;
        margin-bottom: 18px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #F4F5F7;
        border: 1px solid #ECEEF2;
        border-radius: 999px;
        padding: 9px 18px;
        font-weight: 700;
        color: #3F4650;
        font-size: 0.9rem;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background-color: #EDEFF3;
        color: #111111;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #B31217 !important;
        border-color: #B31217 !important;
        color: #FFFFFF !important;
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: transparent !important;
    }}

    .stTabs [data-baseweb="tab-border"] {{
        background-color: transparent !important;
    }}

    .stTabs [aria-selected="true"] p {{
        color: #FFFFFF !important;
    }}

    /* ==========================================
       PANELES DE LA VISTA DE PEDIDO POR VOZ
       ========================================== */
    .panel {{
        background: #FFFFFF;
        border: 1px solid #EAECEF;
        border-radius: 14px;
        padding: 16px 16px 18px 16px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        height: 100%;
    }}

    .panel-title {{
        font-size: 1.02rem;
        font-weight: 900;
        color: #111111;
        margin: 0 0 4px 0;
        letter-spacing: -0.01em;
    }}

    .panel-sub {{
        font-size: 0.82rem;
        color: #6B7280;
        margin: 0 0 10px 0;
    }}

    .section-label {{
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B7280;
        margin: 14px 0 6px 0;
    }}

    /* Micrófono central */
    div[data-testid="stAudioInput"] {{
        display: flex;
        justify-content: center;
        padding: 6px 0 2px 0;
    }}

    div[data-testid="stAudioInput"] button {{
        width: 74px !important;
        height: 74px !important;
        border-radius: 50% !important;
        background: #C4161C !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 0 0 9px rgba(196, 22, 28, 0.10),
                    0 0 0 20px rgba(196, 22, 28, 0.05) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    div[data-testid="stAudioInput"] button:hover {{
        transform: scale(1.04);
        box-shadow: 0 0 0 11px rgba(196, 22, 28, 0.13),
                    0 0 0 24px rgba(196, 22, 28, 0.07) !important;
    }}

    div[data-testid="stAudioInput"] svg {{
        width: 30px;
        height: 30px;
    }}

    /* Consola de transcripción con onda */
    .console-box {{
        background: #FAFBFC;
        border: 1px solid #ECEEF2;
        border-radius: 10px;
        padding: 10px 12px;
        margin-top: 12px;
    }}

    .console-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.72rem;
        font-weight: 700;
        color: #6B7280;
        margin-bottom: 6px;
    }}

    .wave {{
        display: flex;
        align-items: center;
        gap: 2px;
        height: 30px;
        margin-bottom: 6px;
    }}

    .wave i {{
        display: block;
        width: 3px;
        border-radius: 3px;
        background: #E2231A;
        opacity: 0.45;
    }}

    .live-text {{
        font-size: 0.8rem;
        color: #374151;
        line-height: 1.35;
    }}

    /* Burbujas de conversación */
    .chat-row {{
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
    }}

    .chat-avatar {{
        flex: 0 0 32px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #F97316, #C4161C);
        color: #FFFFFF;
        font-size: 0.68rem;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 2px;
    }}

    .chat-name {{
        font-size: 0.82rem;
        font-weight: 900;
        color: #111111;
        margin-bottom: 1px;
    }}

    .chat-role {{
        font-size: 0.7rem;
        color: #6B7280;
        margin-bottom: 6px;
    }}

    .bubble {{
        background: #F8F9FB;
        border: 1px solid #ECEEF2;
        border-radius: 12px;
        padding: 11px 13px;
        font-size: 0.85rem;
        color: #374151;
        line-height: 1.45;
    }}

    .bubble-user {{
        background: #FFF4F2;
        border-color: #F7DCD7;
    }}

    /* Panel de conversación transcrita */
    .transcript-box {{
        background: #FAFBFC;
        border: 1px solid #ECEEF2;
        border-radius: 10px;
        padding: 11px 13px;
        font-size: 0.79rem;
        color: #4B5563;
        line-height: 1.55;
    }}

    .transcript-box b {{
        color: #111111;
    }}

    /* Tarjetas de producto dentro del pedido */
    .order-item-name {{
        font-size: 0.86rem;
        font-weight: 800;
        color: #111111;
        line-height: 1.25;
    }}

    .order-item-price {{
        font-size: 0.78rem;
        color: #6B7280;
        margin-top: 2px;
    }}

    .order-thumb {{
        width: 46px;
        height: 46px;
        border-radius: 9px;
        background-size: cover;
        background-position: center;
        border: 1px solid #ECEEF2;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        background-color: #F6F7F9;
    }}

    .qty-pill {{
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F7F8FA;
        border: 1px solid #ECEEF2;
        border-radius: 8px;
        height: 30px;
        font-size: 0.85rem;
        font-weight: 800;
        color: #111111;
    }}

    .step-btn button {{
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        border: 1px solid #E3E6EB !important;
        background: #FFFFFF !important;
        color: #111111 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        line-height: 1 !important;
    }}

    .step-btn button:hover {{
        background: #FFF4F2 !important;
        color: {MCD_RED} !important;
        border-color: #F7DCD7 !important;
    }}

    .notes-label {{
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6B7280;
        margin: 6px 0 2px 0;
    }}

    /* Totales del pedido */
    .total-row {{
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #4B5563;
        padding: 3px 0;
    }}

    .total-final {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.05rem;
        font-weight: 900;
        color: #111111;
        border-top: 1px solid #ECEEF2;
        margin-top: 8px;
        padding-top: 9px;
    }}

    .total-final b {{
        color: {MCD_RED};
        font-size: 1.3rem;
    }}

    /* Botones generales */
    .stButton > button {{
        border-radius: 9px;
        font-weight: 700;
    }}

    /* Botones de sugerencia rápida */
    div.stElementContainer[class*="st-key-quick_"] button {{
        width: 100%;
        border: 1px solid #E6E8EC;
        background: #FFFFFF;
        color: #374151;
        border-radius: 9px;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 8px 6px;
        text-align: center;
    }}

    div.stElementContainer[class*="st-key-quick_"] button:hover {{
        border-color: #F3C4BF;
        background: #FFF6F5;
        color: #B31217;
    }}

    /* Contenedores de producto del carrito */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 12px;
    }}

    /* Contenedores clave (paneles y tarjetas de producto) */
    div[class*="st-key-panel_"] {{
        background: #FFFFFF;
        border: 1px solid #EAECEF;
        border-radius: 14px;
        padding: 16px 16px 18px 16px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        min-height: 585px;
    }}

    div[class*="st-key-item_"] {{
        background: #FCFCFD;
        border: 1px solid #EDEFF3;
        border-radius: 12px;
        padding: 10px 12px 6px 12px;
        margin-bottom: 10px;
        gap: 0.35rem !important;
    }}

    /* Etiqueta del campo de notas dentro de la tarjeta del producto */
    div[class*="st-key-item_"] div[data-testid="stWidgetLabel"] p,
    div[class*="st-key-item_"] label {{
        font-size: 0.66rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6B7280 !important;
        margin: 8px 0 3px 0 !important;
    }}

    .order-head {{
        background: linear-gradient(180deg, #C4161C, #A30F14);
        color: #FFFFFF;
        font-weight: 900;
        font-size: 0.95rem;
        text-align: center;
        padding: 9px 12px;
        border-radius: 9px;
        margin-bottom: 12px;
        letter-spacing: 0.01em;
    }}

    div.stElementContainer[class*="st-key-minus_"] button,
    div.stElementContainer[class*="st-key-plus_"] button {{
        height: 30px !important;
        min-height: 30px !important;
        padding: 0 !important;
        border-radius: 8px !important;
        border: 1px solid #E3E6EB !important;
        background: #FFFFFF !important;
        color: #111111 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        line-height: 1 !important;
    }}

    div.stElementContainer[class*="st-key-minus_"] button:hover,
    div.stElementContainer[class*="st-key-plus_"] button:hover {{
        background: #FFF4F2 !important;
        color: #C4161C !important;
        border-color: #F7DCD7 !important;
    }}

    div.stElementContainer[class*="st-key-del_"] button {{
        background: transparent !important;
        border: none !important;
        color: #9CA3AF !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        padding: 0 !important;
        min-height: 22px !important;
        height: 22px !important;
        text-decoration: underline;
    }}

    div.stElementContainer[class*="st-key-del_"] button:hover {{
        color: #C4161C !important;
    }}

    /* ==========================================
       TARJETAS DE LA CARTA DIGITAL (NUEVO DISEÑO)
       ========================================== */
    .carta-media {{
        position: relative;
        flex: 0 0 175px;
        height: 175px;
        width: 100%;
        background-size: cover;
        background-position: center;
        background-color: #F3F4F6;
    }}

    .carta-badge {{
        position: absolute;
        top: 12px;
        left: 12px;
        background: #C4161C;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.74rem;
        letter-spacing: 0.02em;
        padding: 5px 11px;
        border-radius: 999px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
    }}

    .carta-body {{
        display: flex;
        flex-direction: column;
        flex: 1;
        padding: 14px 16px 4px 16px;
    }}

    .carta-toprow {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
    }}

    .carta-title {{
        font-size: 1.02rem;
        font-weight: 900;
        color: #111111;
        margin: 0;
        line-height: 1.25;
        letter-spacing: -0.01em;
        min-height: 2.5em;
    }}

    .carta-rating {{
        flex: 0 0 auto;
        font-size: 0.78rem;
        font-weight: 800;
        color: #C4161C;
        background: #FFF4F2;
        border-radius: 999px;
        padding: 3px 8px;
    }}

    .carta-desc {{
        font-size: 0.82rem;
        color: #6B7280;
        line-height: 1.4;
        height: 3.5em;
        margin: 7px 0 10px 0;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }}

    .carta-meta {{
        display: flex;
        gap: 14px;
        color: #6B7280;
        font-size: 0.76rem;
        margin-top: auto;
    }}

    .carta-price {{
        font-size: 1.16rem;
        font-weight: 900;
        color: #C4161C;
        margin-top: 8px;
    }}

    /* Contenedor-tarjeta de cada producto */
    div[class*="st-key-carta_card_"] {{
        background: #FFFFFF;
        border: 1px solid #EAECEF;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(16, 24, 40, 0.05);
        padding: 0 !important;
        gap: 0 !important;
        display: flex;
        flex-direction: column;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }}

    div[class*="st-key-carta_card_"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(16, 24, 40, 0.10);
    }}

    div[class*="st-key-carta_card_"] div[data-testid="stButton"] {{
        padding: 0 16px 14px 16px;
    }}

    /* Streamlit aplica margen negativo al markdown; dentro de la tarjeta lo anulamos
       para que el botón no se monte sobre el precio. */
    div[class*="st-key-carta_card_"] [data-testid="stMarkdownContainer"] {{
        margin-bottom: 0 !important;
    }}

    div[class*="st-key-panel_"] [data-testid="stMarkdownContainer"],
    div[class*="st-key-item_"] [data-testid="stMarkdownContainer"] {{
        margin-bottom: 0 !important;
    }}

    div[class*="st-key-carta_card_"] div[data-testid="stButton"] button {{
        width: 100%;
        background: #C4161C;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.83rem;
        padding: 8px 10px;
    }}

    div[class*="st-key-carta_card_"] div[data-testid="stButton"] button:hover {{
        background: #A30F14;
        color: #FFFFFF;
    }}

    /* Caja de Pago Exitoso */
    .success-payment-box {{
        background-color: #E6F4EA;
        border: 2px solid #28A745;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #155724;
        margin: 15px 0;
    }}

    /* ==========================================
       RESPONSIVIDAD
       ========================================== */
    @media (max-width: 1100px) {{
        .nav-logo {{
            height: 52px;
        }}

        div[class*="st-key-panel_"] {{
            min-height: auto;
        }}
    }}

    @media (max-width: 760px) {{
        .block-container {{
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }}

        .top-nav {{
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }}

        .nav-logo {{
            height: 46px;
        }}

        .nav-actions {{
            width: 100%;
            gap: 8px;
        }}

        .logo-badge,
        .btn-top-alert {{
            font-size: 0.76rem;
            padding: 7px 12px;
        }}

        .panel-title {{
            font-size: 0.98rem;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            flex-wrap: wrap;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding: 8px 14px;
            font-size: 0.82rem;
        }}

        .carta-media {{
            height: 150px;
            flex-basis: 150px;
        }}

        .total-final b {{
            font-size: 1.15rem;
        }}
    }}
    </style>
""", unsafe_allow_html=True)


# ==========================================
# CARGA DE DATOS Y ESTADO DE SESIÓN
# ==========================================
@st.cache_data
def cargar_menu():
    try:
        with open("menu.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error cargando menú: {e}")
        return []

menu_data = cargar_menu()

DEFAULTS = {
    "carrito": [],
    "zamy_response": "Acá aparecerá la respuesta de Zamy y la confirmación de tu pedido una vez que presiones el micrófono y hables.",
    "audio_hash": None,
    "pending_audio": None,
    "audio_mime": "audio/wav",
    "transcripcion_texto": "",
    "texto_pedido": "",
    "interpretacion": None,
    "respuesta_audio": None,
    "voz_pendiente": False,
    "error_transcripcion": None,
    "error_ia": None,
    "texto_aplicado": "",
    "pago_exitoso": False,
    "last_order_id": None,
}
for clave, valor in DEFAULTS.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor

if "kitchen_orders" not in st.session_state:
    st.session_state.kitchen_orders = [
        {
            "id": "ORD-501",
            "cliente": "Mesa 3 (Voz)",
            "items": [
                {"nombre": "Zamy Mega Crunch Burger", "cant": 2, "notas": ""},
                {"nombre": "Zamy Loaded Fries Supreme", "cant": 1, "notas": ""},
                {"nombre": "Zamy Volcano Shake Nutella", "cant": 2, "notas": "sin crema batida"}
            ],
            "total": 34.46,
            "estado": "En Preparación",
            "hora": "14:15"
        },
        {
            "id": "ORD-502",
            "cliente": "Mesa 7 (Menú Digital)",
            "items": [
                {"nombre": "Zamy Monster Wrap de Pollo", "cant": 1, "notas": ""},
                {"nombre": "Limonada Zamy Frutos Rojos", "cant": 1, "notas": ""}
            ],
            "total": 12.91,
            "estado": "Pendiente",
            "hora": "14:22"
        }
    ]


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def agregar_al_carrito(producto, cantidad=1, notas=""):
    """Suma al carrito respetando la nota: misma nota se acumula, distinta nota es otra línea."""
    for item in st.session_state.carrito:
        if item["id"] == producto["id"] and item.get("notas", "") == notas:
            item["cantidad"] = min(20, item["cantidad"] + cantidad)
            return
    st.session_state.carrito.append({
        "id": producto["id"],
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "imagen": producto.get("imagen_emoji", "🍔"),
        "imagen_url": producto.get("imagen_url", ""),
        "cantidad": cantidad,
        "notas": notas,
    })


def calcular_total():
    """Total del pedido: suma directa de los ítems, sin impuestos."""
    return sum(item["precio"] * item["cantidad"] for item in st.session_state.carrito)


def generar_qr_pago(order_id, monto):
    qr_data = f"https://zamy.app/pay?order={order_id}&amount={monto:.2f}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=MCD_RED, back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generar_voz(texto):
    """Devuelve la respuesta de Zamy en audio (gTTS). Si falla, no bloquea la app."""
    if not texto:
        return None
    try:
        from gtts import gTTS

        limpio = re.sub(r"[*_#>`]", "", texto)
        limpio = re.sub(r"[^\w\sáéíóúÁÉÍÓÚñÑüÜ.,;:¿?¡!$%\-]", " ", limpio)
        limpio = re.sub(r"\s+", " ", limpio).strip()
        if not limpio:
            return None
        tts = gTTS(text=limpio, lang="es")
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


def responder_zamy(mensaje, con_voz=True):
    st.session_state.zamy_response = mensaje
    if con_voz:
        st.session_state.respuesta_audio = generar_voz(mensaje)
        st.session_state.voz_pendiente = bool(st.session_state.respuesta_audio)
    else:
        st.session_state.respuesta_audio = None


def reiniciar_audio():
    """Limpia el audio pendiente. El texto del widget se limpia al inicio del próximo run
    (no se puede modificar un widget que ya fue instanciado en este mismo run)."""
    st.session_state.pending_audio = None
    st.session_state.transcripcion_texto = ""
    st.session_state.interpretacion = None
    st.session_state.error_transcripcion = None
    st.session_state.error_ia = None
    st.session_state.texto_aplicado = ""
    st.session_state["_limpiar_texto_pedido"] = True


def interpretar_texto(texto):
    """Manda el texto (dictado o escrito) a Gemini y guarda el pedido interpretado."""
    st.session_state.error_ia = None
    if not texto or not texto.strip():
        st.session_state.error_ia = "Primero dicta o escribe tu pedido."
        return
    with st.spinner("🧠 Zamy está entendiendo tu pedido..."):
        try:
            resultado = interpretar_pedido(texto, menu_data, st.session_state.carrito)
        except Exception as exc:
            st.session_state.error_ia = f"No se pudo interpretar el pedido: {exc}"
            return
        responder_zamy(resultado["respuesta"])
    resultado["texto_original"] = texto.strip()
    st.session_state.interpretacion = resultado
    if resultado.get("modo") == "local":
        st.session_state.error_ia = (
            "Se usó el intérprete local de respaldo. "
            + (resultado.get("error_ia") or "Configura GEMINI_API_KEY para activar Gemini.")
        )


def aplicar_interpretacion():
    """Vuelca el pedido interpretado al carrito, donde el cliente puede seguir editándolo."""
    res = st.session_state.interpretacion
    if not res:
        return
    for item in res.get("items", []):
        producto = next((p for p in menu_data if p["id"] == item["id"]), None)
        if producto:
            agregar_al_carrito(producto, item["cantidad"], item.get("notas", ""))
    if res.get("quitar"):
        st.session_state.carrito = [
            i for i in st.session_state.carrito if i["id"] not in res["quitar"]
        ]
    st.session_state.texto_aplicado = res.get("texto_original", "").strip()
    st.session_state.interpretacion = None
    partes = []
    if res.get("items"):
        partes.append("agregué tu pedido al carrito")
    if res.get("quitar"):
        partes.append("quité lo que me pediste")
    if not partes:
        partes.append("no agregué nada nuevo")
    responder_zamy(
        f"¡Listo! {partes[0].capitalize()}. Puedes ajustar cantidades, notas o "
        "quitar productos directamente en el carrito antes de pagar."
    )


def html_seguro(texto):
    return html.escape(str(texto or "")).replace("\n", "<br>")


# ==========================================
# NAVBAR SUPERIOR
# ==========================================
@st.cache_data(show_spinner=False)
def logo_nav_uri(alto: int = 160) -> str:
    """Recorta el logo, lo escala y lo devuelve como data URI liviano.

    Se recorta el margen blanco y se evita la marca de agua inferior derecha.
    Si algo falla, devuelve "" y el navbar usa el respaldo de texto.
    """
    try:
        from PIL import Image

        ruta = Path(__file__).with_name("zamy_logo.png")
        if not ruta.exists():
            return ""
        img = Image.open(ruta).convert("RGB")
        ancho, alto_original = img.size
        img = img.crop((0, 0, int(ancho * 0.90), int(alto_original * 0.94)))
        mascara = img.convert("L").point(lambda p: 255 if p < 245 else 0)
        caja = mascara.getbbox()
        if caja:
            img = img.crop(caja)
        factor = alto / max(1, img.height)
        img = img.resize((max(1, int(img.width * factor)), alto), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return ""


logo_uri = logo_nav_uri()
if logo_uri:
    marca_html = (
        f'<img class="nav-logo" src="{logo_uri}" alt="Zamy Fast Food">'
    )
else:
    marca_html = (
        '<span class="brand-mark">🍔</span>'
        '<span>Zamy <span style="color: #B31217;">Fast Food</span></span>'
    )

st.markdown(f"""
    <div class="top-nav">
        <div class="logo-title">{marca_html}</div>
        <div class="nav-actions">
            <span class="logo-badge"><span class="dot"></span>Auto-Atención Digital</span>
            <span class="btn-top-alert">📞 PEDIDOS / +51 900 123 456</span>
        </div>
    </div>
""", unsafe_allow_html=True)

if not ia_disponible():
    st.warning(
        "⚠️ No se encontró `GEMINI_API_KEY`. La transcripción y la comprensión del pedido "
        "usarán el modo local de respaldo. Crea un archivo `.env` con "
        "`GEMINI_API_KEY=tu_clave` para activar Gemini."
    )


def onda_html(activa: bool) -> str:
    """Onda decorativa de la consola de transcripción."""
    alturas = [
        8, 16, 24, 12, 20, 30, 18, 10, 26, 34, 22, 14, 28, 12, 20, 32,
        24, 16, 10, 26, 18, 30, 14, 22, 34, 20, 12, 24, 16, 28, 10, 20,
        30, 16, 24, 12, 22, 34, 18, 14, 26, 20, 12, 28, 16, 24, 10, 18,
    ]
    opacidad = 0.62 if activa else 0.22
    barras = "".join(
        f'<i style="height:{h}px;opacity:{opacidad};"></i>' for h in alturas
    )
    return f'<div class="wave">{barras}</div>'


def duracion_audio(audio_bytes) -> str:
    if not audio_bytes:
        return "00:00"
    segundos = int(len(audio_bytes) / 32000)  # WAV 16 kHz, 16 bits, mono
    segundos = max(1, min(segundos, 3599))
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


# ==========================================
# SISTEMA DE BARRA DE NAVEGACIÓN (3 PESTAÑAS)
# ==========================================
tab_voz, tab_menu, tab_cocina = st.tabs([
    "🎙️ Atención por Voz",
    "📋 Carta Digital",
    "👨‍🍳 Comandas en Vivo"
])


# PESTAÑA 1: PEDIDO POR VOZ
# ------------------------------------------
with tab_voz:
    # Limpieza diferida del texto transcrito (seguro: ocurre antes de crear el widget)
    if st.session_state.pop("_limpiar_texto_pedido", False):
        st.session_state.texto_pedido = ""

    col_asistente, col_conversacion, col_pedido = st.columns(
        [1.02, 1.12, 1.0], gap="medium"
    )

    # ==========================================================
    # COLUMNA 1: ASISTENTE VIRTUAL + MICRÓFONO
    # ==========================================================
    with col_asistente:
        with st.container(key="panel_asistente"):
            st.markdown(
                '<div class="panel-title">Asistente Virtual Zamy</div>'
                '<div class="panel-sub">Habla con Zamy, tu asistente de pedidos IA</div>',
                unsafe_allow_html=True,
            )

            audio_val = st.audio_input(
                "Presiona el micrófono para hablar con Zamy",
                key="mic_pedido",
                label_visibility="collapsed",
            )

            if audio_val is not None:
                audio_bytes = audio_val.getvalue()
                nuevo_hash = hashlib.md5(audio_bytes).hexdigest()
                if nuevo_hash != st.session_state.audio_hash:
                    st.session_state.audio_hash = nuevo_hash
                    st.session_state.pending_audio = audio_bytes
                    st.session_state.audio_mime = detectar_mime(
                        audio_bytes, getattr(audio_val, "type", None)
                    )
                    st.session_state.interpretacion = None
                    st.session_state.error_transcripcion = None
                    st.session_state.error_ia = None
                    st.session_state.transcripcion_texto = ""
                    st.session_state.texto_pedido = ""
                    st.session_state.texto_aplicado = ""

                    if ia_disponible():
                        with st.spinner("✍️ Transcribiendo tu audio..."):
                            try:
                                transcripcion = transcribir_audio(
                                    audio_bytes, st.session_state.audio_mime
                                )
                            except Exception as exc:
                                transcripcion = ""
                                st.session_state.error_transcripcion = str(exc)[:250]
                        st.session_state.transcripcion_texto = transcripcion
                        st.session_state.texto_pedido = transcripcion
                        if transcripcion and not transcripcion.startswith("("):
                            responder_zamy(
                                f"Te escuché: «{transcripcion}»", con_voz=False
                            )
                    else:
                        st.session_state.error_transcripcion = (
                            "Sin GEMINI_API_KEY no se puede transcribir: escribe tu pedido abajo."
                        )

            # Consola de transcripción en vivo
            texto_consola = (
                st.session_state.transcripcion_texto
                or st.session_state.texto_pedido
                or "Presiona el micrófono y cuéntame qué se te antoja..."
            )
            st.markdown(
                '<div class="console-box">'
                '<div class="console-head">'
                '<span>🎙️ Transcripción en Vivo</span>'
                f'<span>{duracion_audio(st.session_state.pending_audio)}</span>'
                '</div>'
                f'{onda_html(bool(st.session_state.pending_audio))}'
                '<div class="live-text">'
                f'{html_seguro(texto_consola)}'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            if st.session_state.error_transcripcion:
                st.caption(f"⚠️ {st.session_state.error_transcripcion}")

            if st.session_state.pending_audio:
                st.markdown(
                    '<div class="section-label">Corrige el texto antes de enviarlo</div>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    "Texto transcrito del pedido",
                    key="texto_pedido",
                    height=96,
                    label_visibility="collapsed",
                    placeholder="Ej: quiero dos Mega Crunch, papas con cheddar y una limonada",
                )
                st.audio(
                    st.session_state.pending_audio,
                    format=st.session_state.audio_mime,
                )

                ya_aplicado = bool(
                    st.session_state.texto_aplicado
                    and st.session_state.texto_pedido.strip()
                    == st.session_state.texto_aplicado.strip()
                )
                if ya_aplicado:
                    st.success(
                        "✅ Pedido agregado. Ajusta cantidades o notas en tu pedido."
                    )

                c_env, c_desc = st.columns(2)
                with c_env:
                    enviar = st.button(
                        "🔁 Reinterpretar" if ya_aplicado else "🧠 Interpretar pedido",
                        type="primary",
                        use_container_width=True,
                        key="btn_interpretar",
                    )
                with c_desc:
                    descartar = st.button(
                        "🗑️ Descartar",
                        use_container_width=True,
                        key="btn_descartar_audio",
                    )

                if descartar:
                    reiniciar_audio()
                    responder_zamy(
                        "Descarté el audio. Puedes volver a presionar el micrófono cuando quieras.",
                        con_voz=False,
                    )
                    st.rerun()

                if enviar:
                    interpretar_texto(st.session_state.texto_pedido)
                    st.rerun()
            else:
                st.markdown(
                    '<div style="text-align:center; color:#6B7280; font-size:0.78rem; margin-top:10px;">'
                    'Presiona el micrófono y pide con tus palabras. '
                    'Zamy entiende el menú y arma tu pedido.'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="section-label">Prueba rápida (sin micrófono)</div>',
                unsafe_allow_html=True,
            )
            ejemplos = [
                (
                    "🍔 Dos Mega Crunch + malteada",
                    "Quiero dos hamburguesas Mega Crunch y una malteada de Nutella",
                ),
                ("🌱 Algo sin gluten", "Busco algo sin gluten para comer"),
                (
                    "✨ Recomiéndame algo",
                    "No sé qué pedir, recomiéndame algo rico de la carta",
                ),
                (
                    "✏️ Cambiar mi pedido",
                    "Mejor quita las papas y agrega una limonada",
                ),
            ]
            c_izq = c_der = None
            for idx, (etiqueta, frase) in enumerate(ejemplos):
                if idx % 2 == 0:
                    c_izq, c_der = st.columns(2)
                destino = c_izq if idx % 2 == 0 else c_der
                with destino:
                    if st.button(
                        etiqueta, use_container_width=True, key=f"quick_{idx}"
                    ):
                        st.session_state.pending_audio = None
                        st.session_state.transcripcion_texto = frase
                        st.session_state.texto_pedido = frase
                        st.session_state.error_transcripcion = None
                        st.session_state.error_ia = None
                        interpretar_texto(frase)
                        st.rerun()

    # ==========================================================
    # COLUMNA 2: CONVERSACIÓN
    # ==========================================================
    with col_conversacion:
        with st.container(key="panel_conversacion"):
            st.markdown(
                '<div class="panel-title">Tu Conversación</div>'
                '<div class="panel-sub">Zamy escucha, entiende y confirma tu pedido</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="chat-row">'
                '<div class="chat-avatar">zo</div>'
                '<div style="flex:1;">'
                '<div class="chat-name">Zamy Assistant <span style="color:#16A34A;">✔</span></div>'
                '<div class="chat-role">IA Asistida</div>'
                f'<div class="bubble">«{html_seguro(st.session_state.zamy_response)}»</div>'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

            if st.session_state.respuesta_audio:
                st.audio(
                    st.session_state.respuesta_audio,
                    format="audio/mp3",
                    autoplay=st.session_state.voz_pendiente,
                )
                st.session_state.voz_pendiente = False

            if st.session_state.transcripcion_texto:
                st.markdown(
                    '<div class="chat-row">'
                    '<div style="flex:1;">'
                    '<div class="chat-name" style="text-align:right;">Tú</div>'
                    '<div class="bubble bubble-user" style="text-align:right;">'
                    f'{html_seguro(st.session_state.transcripcion_texto)}'
                    '</div>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="section-label">Conversación Transcrita</div>',
                unsafe_allow_html=True,
            )
            zamy_linea = html_seguro(st.session_state.zamy_response[:170])
            cliente_linea = html_seguro(
                st.session_state.transcripcion_texto
                or st.session_state.texto_pedido
                or "—"
            )
            st.markdown(
                '<div class="transcript-box">'
                f'<b>Zamy:</b> {zamy_linea} '
                '<span style="color:#9CA3AF;">(actualizado)</span><br>'
                f'<b>Cliente:</b> {cliente_linea}'
                '</div>',
                unsafe_allow_html=True,
            )

        if st.session_state.error_ia:
            st.warning(st.session_state.error_ia)

        # --- Tarjeta del pedido interpretado por la IA ---
        res = st.session_state.interpretacion
        if res:
            menu_por_id = {p["id"]: p for p in menu_data}
            total_ia = 0.0
            filas = ""
            for item in res["items"]:
                producto = menu_por_id.get(item["id"])
                if not producto:
                    continue
                linea_total = producto["precio"] * item["cantidad"]
                total_ia += linea_total
                nota = (
                    f'<div class="ia-note">📝 {html_seguro(item["notas"])}</div>'
                    if item["notas"]
                    else ""
                )
                filas += (
                    '<div class="ia-item">'
                    f'<div><b>{item["cantidad"]}x</b> {html_seguro(producto["nombre"])}{nota}</div>'
                    f'<div style="font-weight:800; white-space:nowrap;">${linea_total:.2f}</div>'
                    '</div>'
                )

            if not filas:
                filas = (
                    "<p style='color:#6C757D; font-size:0.9rem; margin:6px 0;'>"
                    "No se agregaron productos en esta interpretación.</p>"
                )

            extra = ""
            if res["no_disponibles"]:
                faltantes = ", ".join(html_seguro(x) for x in res["no_disponibles"])
                extra += (
                    f'<div class="ia-warn">🚫 No tenemos <b>{faltantes}</b> en el menú. '
                    "Te propongo una alternativa parecida.</div>"
                )
            if res["sugerencias"]:
                nombres_sug = ", ".join(
                    html_seguro(menu_por_id[s]["nombre"])
                    for s in res["sugerencias"]
                    if s in menu_por_id
                )
                extra += (
                    f'<div class="ia-hint">✨ También te puede gustar: <b>{nombres_sug}</b></div>'
                )
            if res["aclaracion"]:
                extra += f'<div class="ia-hint">❓ {html_seguro(res["aclaracion"])}</div>'

            modo = "Gemini" if res.get("modo") == "gemini" else "Modo local"
            tarjeta = (
                '<div class="ia-card">'
                '<div class="ia-card-title">'
                '<span>🧠 Pedido entendido</span>'
                f'<span class="ia-chip">{modo} · {html_seguro(res["intencion"])}</span>'
                '</div>'
                f'{filas}'
                '<div style="display:flex; justify-content:space-between; margin-top:10px; font-size:0.95rem; color:#111111; font-weight:800;">'
                f'<span>Total</span><b>${total_ia:.2f}</b>'
                '</div>'
                f'{extra}'
                '</div>'
            )
            st.markdown(tarjeta, unsafe_allow_html=True)

            if res["items"] or res["quitar"]:
                c_a, c_b = st.columns(2)
                with c_a:
                    if st.button(
                        "✅ Agregar al carrito",
                        type="primary",
                        use_container_width=True,
                        key="btn_aplicar_ia",
                    ):
                        aplicar_interpretacion()
                        st.rerun()
                with c_b:
                    if st.button(
                        "✏️ Ajustar texto",
                        use_container_width=True,
                        key="btn_ajustar_texto",
                    ):
                        st.session_state.interpretacion = None
                        st.rerun()

    # ==========================================================
    # COLUMNA 3: MI PEDIDO ACTUAL
    # ==========================================================
    with col_pedido:
        with st.container(key="panel_pedido"):
            st.markdown(
                '<div class="panel-title">Mi Pedido Actual</div>'
                '<div class="panel-sub">Revisa, ajusta y confirma antes de pagar</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="order-head">🛒 Mi Pedido</div>', unsafe_allow_html=True)

            if not st.session_state.carrito:
                st.markdown(
                    '<div style="text-align:center; color:#94A3B8; font-size:0.82rem; '
                    'padding:26px 6px;">Tu pedido está vacío.<br>Habla con Zamy o agrega '
                    'productos desde la Carta Digital.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Ajusta cantidades y escribe notas para la cocina.")

                ids_eliminar = []
                for pos, item in enumerate(list(st.session_state.carrito)):
                    with st.container(key=f"item_{item['id']}_{pos}"):
                        c_img, c_info, c_step = st.columns(
                            [0.85, 2.45, 2.1], vertical_alignment="center"
                        )
                        with c_img:
                            url = item.get("imagen_url") or ""
                            if url:
                                miniatura = (
                                    '<div class="order-thumb" style="background-image:'
                                    f"url('{url}');\"></div>"
                                )
                            else:
                                miniatura = (
                                    f'<div class="order-thumb">{item["imagen"]}</div>'
                                )
                            st.markdown(miniatura, unsafe_allow_html=True)
                        with c_info:
                            st.markdown(
                                f'<div class="order-item-name">{html_seguro(item["nombre"])}</div>'
                                f'<div class="order-item-price">${item["precio"]:.2f} c/u</div>',
                                unsafe_allow_html=True,
                            )
                        with c_step:
                            c_menos, c_cant, c_mas = st.columns(3, vertical_alignment="center")
                            with c_menos:
                                if st.button(
                                    "−",
                                    key=f"minus_{item['id']}_{pos}",
                                    use_container_width=True,
                                ):
                                    if item["cantidad"] <= 1:
                                        ids_eliminar.append(item["id"])
                                    else:
                                        item["cantidad"] -= 1
                                    st.rerun()
                            with c_cant:
                                st.markdown(
                                    f'<div class="qty-pill">{item["cantidad"]}</div>',
                                    unsafe_allow_html=True,
                                )
                            with c_mas:
                                if st.button(
                                    "+",
                                    key=f"plus_{item['id']}_{pos}",
                                    use_container_width=True,
                                ):
                                    item["cantidad"] = min(20, item["cantidad"] + 1)
                                    st.rerun()

                        item["notas"] = st.text_input(
                            "Notas de cocina",
                            value=item.get("notas", ""),
                            key=f"nota_{item['id']}_{pos}",
                            placeholder="Sin cebolla, extra salsa...",
                        )
                        if st.button(
                            "🗑️ Quitar del pedido",
                            key=f"del_{item['id']}_{pos}",
                            use_container_width=False,
                        ):
                            ids_eliminar.append(item["id"])
                            st.rerun()

                if ids_eliminar:
                    st.session_state.carrito = [
                        i for i in st.session_state.carrito if i["id"] not in ids_eliminar
                    ]
                    st.rerun()

                total = calcular_total()
                st.markdown(
                    '<div style="margin-top:10px;">'
                    '<div class="total-final" style="border-top:none; margin-top:0;">'
                    "<span>Total</span>"
                    f'<b>${total:.2f}</b></div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                if not st.session_state.pago_exitoso:
                    if not st.session_state.last_order_id:
                        st.session_state.last_order_id = f"ORD-{random.randint(503, 999)}"

                    order_id = st.session_state.last_order_id
                    qr_img = generar_qr_pago(order_id, total)

                    c_qr1, c_qr2, c_qr3 = st.columns([1, 1.4, 1])
                    with c_qr2:
                        st.image(qr_img, width=150)

                    st.markdown(
                        '<div style="text-align:center; color:#6B7280; font-size:0.76rem; '
                        'margin-bottom:10px;">'
                        f'Pagar con QR · Código: <b>{order_id}</b></div>',
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "📱 Pagar",
                        type="primary",
                        use_container_width=True,
                        key="btn_pagar",
                    ):
                        progress_text = "🔄 Procesando simulación de pago con Zamy Pay..."
                        my_bar = st.progress(0, text=progress_text)
                        with st.spinner("Conectando con la pasarela bancaria..."):
                            for percent_complete in range(100):
                                time.sleep(0.02)
                                my_bar.progress(percent_complete + 1, text=progress_text)

                        my_bar.empty()
                        st.session_state.pago_exitoso = True

                        nueva_comanda = {
                            "id": order_id,
                            "cliente": "Mesa 2 (Pedido por Voz)",
                            "items": [
                                {
                                    "nombre": i["nombre"],
                                    "cant": i["cantidad"],
                                    "notas": i.get("notas", ""),
                                }
                                for i in st.session_state.carrito
                            ],
                            "total": round(total, 2),
                            "estado": "Pendiente",
                            "hora": time.strftime("%H:%M"),
                        }
                        st.session_state.kitchen_orders.insert(0, nueva_comanda)
                        st.rerun()

                    if st.button(
                        "🧹 Vaciar pedido",
                        use_container_width=True,
                        key="btn_vaciar",
                    ):
                        st.session_state.carrito = []
                        st.session_state.interpretacion = None
                        st.session_state.pago_exitoso = False
                        st.session_state.last_order_id = None
                        responder_zamy(
                            "Carrito vacío. ¿Qué se te antoja ahora?", con_voz=False
                        )
                        st.rerun()
                else:
                    st.markdown(
                        '<div class="success-payment-box">'
                        '<h3 style="margin: 0; color: #155724;">✅ Pago realizado exitosamente</h3>'
                        '<p style="margin: 5px 0 0 0; font-size: 0.85rem;">'
                        '¡Gracias por tu compra! Tu comanda fue enviada a la cocina.</p>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                    st.balloons()

                    if st.button(
                        "➕ Realizar Nuevo Pedido",
                        use_container_width=True,
                        key="btn_nuevo_pedido",
                    ):
                        st.session_state.carrito = []
                        st.session_state.pago_exitoso = False
                        st.session_state.last_order_id = None
                        reiniciar_audio()
                        st.rerun()


# ------------------------------------------
# ------------------------------------------
# PESTAÑA 2: CARTA & MENÚ DIGITAL (ESTILO PEDIDOSYA)
# ------------------------------------------
with tab_menu:
    st.markdown(
        '<div class="panel-title" style="font-size:1.55rem;">Descubre estas opciones en Zamy 🍔</div>'
        '<div class="panel-sub" style="font-size:0.92rem; margin:6px 0 14px 0;">'
        "Explora la carta, elige tus favoritos y agrégalos a tu pedido.</div>",
        unsafe_allow_html=True,
    )

    # Filtro por Categorías
    categorias = ["Todas"] + sorted(list(set(p["categoria"] for p in menu_data)))
    cat_sel = st.radio("Filtrar por categoría:", categorias, horizontal=True)

    prods_mostrar = menu_data if cat_sel == "Todas" else [p for p in menu_data if p["categoria"] == cat_sel]

    # Grid de tarjetas (3 columnas, altura uniforme)
    cols = st.columns(3, gap="medium")
    for idx, prod in enumerate(prods_mostrar):
        with cols[idx % 3]:
            with st.container(key=f"carta_card_{prod['id']}"):
                st.markdown(
                    '<div class="carta-media" style="background-image:url('
                    f"'{prod['imagen_url']}');\">"
                    f'<div class="carta-badge">{html_seguro(prod.get("badge", "Popular"))}</div>'
                    "</div>"
                    '<div class="carta-body">'
                    '<div class="carta-toprow">'
                    f'<h3 class="carta-title">{html_seguro(prod["nombre"])}</h3>'
                    f'<span class="carta-rating">★ {prod["rating"]}</span>'
                    "</div>"
                    f'<p class="carta-desc">{html_seguro(prod["descripcion"])}</p>'
                    '<div class="carta-meta">'
                    f'<span>🕒 {html_seguro(prod["tiempo"])}</span>'
                    "<span>🛵 Envío Gratis</span>"
                    "</div>"
                    f'<div class="carta-price">${prod["precio"]:.2f}</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )

                if st.button(
                    "🛒 Agregar al Pedido",
                    key=f"btn_pya_{prod['id']}",
                    use_container_width=True,
                ):
                    agregar_al_carrito(prod, 1)
                    st.toast(f"✅ Se agregó {prod['nombre']} al carrito", icon="🛒")
                    st.rerun()


# ------------------------------------------
# PESTAÑA 3: COMANDAS EN VIVO (COCINA)
# ------------------------------------------
with tab_cocina:
    st.subheader("👨‍🍳 Comandas en Vivo - Zamy Kitchen Display")
    st.info("💡 En esta pantalla la cocina recibe de forma instantánea los pedidos pagados desde la App por voz o desde la carta digital.")

    if st.button("🔄 Actualizar Comandas"):
        st.rerun()

    if not st.session_state.kitchen_orders:
        st.warning("No hay comandas activas en este momento.")
    else:
        cols_k = st.columns(3)
        for idx, order in enumerate(st.session_state.kitchen_orders):
            with cols_k[idx % 3]:
                border_color = MCD_YELLOW if order["estado"] == "Pendiente" else ("#0D6EFD" if order["estado"] == "En Preparación" else "#28A745")

                st.markdown(f"""
                    <div style="background-color: white; color: #000000; border-top: 5px solid {border_color}; border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #000000;">{order['id']}</h3>
                            <span style="font-size: 0.85rem; color: #000000;">🕒 {order['hora']}</span>
                        </div>
                        <p style="margin: 3px 0 10px 0; font-size: 0.95rem; font-weight: bold; color: #000000;">{order['cliente']}</p>
                        <hr style="margin: 8px 0; border: none; border-top: 1px solid #EEE;">
                        <ul style="padding-left: 20px; margin: 10px 0;">
                """, unsafe_allow_html=True)

                for item in order["items"]:
                    nota = (
                        f" <span style='color:#DA291C;font-size:0.82rem;'>({item['notas']})</span>"
                        if item.get("notas")
                        else ""
                    )
                    st.markdown(
                        f"<li><b>{item['cant']}x</b> {item['nombre']}{nota}</li>",
                        unsafe_allow_html=True,
                    )

                st.markdown(f"""
                        </ul>
                        <hr style="margin: 10px 0; border: none; border-top: 1px solid #EEE;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>Total: <b>${order['total']:.2f}</b></span>
                            <span style="background-color: {border_color}; color: black; padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;">
                                {order['estado']}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                c_a, c_b = st.columns(2)
                with c_a:
                    if order["estado"] == "Pendiente":
                        if st.button("🔥 Preparar", key=f"prep_{order['id']}", use_container_width=True):
                            order["estado"] = "En Preparación"
                            st.rerun()
                    elif order["estado"] == "En Preparación":
                        if st.button("✅ Servir", key=f"ready_{order['id']}", use_container_width=True):
                            order["estado"] = "Listo / Entregado"
                            st.rerun()
                with c_b:
                    if st.button("🗑️ Archivar", key=f"del_{order['id']}", use_container_width=True):
                        st.session_state.kitchen_orders.remove(order)
                        st.rerun()
