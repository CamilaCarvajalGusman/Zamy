import streamlit as st
import json
import time
import io
import re
import html
import hashlib
import qrcode
import random

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
    @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Montserrat:wght@100..900&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Quicksand:wght@300..700&display=swap');
    *{{
      font-family: "Lato", sans-serif;
  font-optical-sizing: auto;
  font-weight: <weight>;
  font-style: normal;
    }}
    /* Fondo principal y contenedor */
    .stApp {{
        background-color: {MCD_BG};
    }}
    
    /* Navbar Superior */
    .top-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 5px 20px 5px;
        border-bottom: 1px solid #E0E0E0;
        margin-bottom: 20px;
    }}
    
    .logo-title {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.6rem;
        font-weight: 800;
        color: {MCD_DARK};
    }}
    
    .logo-badge {{
        background-color: #E6F4EA;
        color: #0D6EFD;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }}
    
    .btn-top-alert {{
        background-color: {MCD_RED};
        color: white;
        font-weight: bold;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
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

    /* Estilo de pestañas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        margin-bottom: 25px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #E2E8F0;
        border-radius: 12px 12px 0 0;
        padding: 12px 26px;
        font-weight: 800;
        color: {MCD_DARK};
        font-size: 1rem;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {MCD_RED} !important;
        color: black !important;
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
        "cantidad": cantidad,
        "notas": notas,
    })


def calcular_total():
    subtotal = sum(item["precio"] * item["cantidad"] for item in st.session_state.carrito)
    impuesto = subtotal * 0.10
    total = subtotal + impuesto
    return subtotal, impuesto, total


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
st.markdown(f"""
    <div class="top-nav">
        <div class="logo-title">
            <span>🍔 Zamy Fast Food</span>
        </div>
        <div>
            <span class="logo-badge">Auto-Atención Digital</span>
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


# ==========================================
# SISTEMA DE BARRA DE NAVEGACIÓN (3 PESTAÑAS)
# ==========================================
tab_voz, tab_menu, tab_cocina = st.tabs([
    "🎙️ Atención & Pedidos por Voz",
    "📋 Carta & Menú Digital",
    "👨‍🍳 Comandas en Vivo (Cocina)"
])


# ------------------------------------------
# PESTAÑA 1: PEDIDO POR VOZ
# ------------------------------------------
with tab_voz:
    # Limpieza diferida del texto transcrito (seguro: ocurre antes de crear el widget)
    if st.session_state.pop("_limpiar_texto_pedido", False):
        st.session_state.texto_pedido = ""

    st.markdown("""
        <div class="main-hero-title">
            Atención y pedido inteligente por voz
            <span class="realtime-tag">Tiempo Real</span>
        </div>
        <div class="hero-subtitle">
            Habla con Zamy: la IA transcribe tu audio, entiende tu pedido y lo arma según el menú real.
        </div>
    """, unsafe_allow_html=True)

    col_mic, col_dictamen, col_cart = st.columns([1.15, 1.1, 1.0], gap="medium")

    # COLUMNA IZQUIERDA: ENTRADA DE AUDIO + TRANSCRIPCIÓN EDITABLE
    with col_mic:
        st.markdown("""
            <div class="voice-card">
                <div class="voice-card-header">
                    🎙️ Entrada de Audio Directa
                </div>
        """, unsafe_allow_html=True)

        audio_val = st.audio_input(
            "Presiona el micrófono para hablar con Zamy", key="mic_pedido"
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
                    with st.spinner("✍️ Transcribiendo tu audio a texto..."):
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
                        responder_zamy(f"Te escuché: «{transcripcion}»", con_voz=False)
                else:
                    st.session_state.error_transcripcion = (
                        "Sin GEMINI_API_KEY no se puede transcribir: escribe tu pedido abajo."
                    )

        # --- Audio recibido: reproducción + transcripción editable ---
        if st.session_state.pending_audio:
            st.markdown(
                "<p style='font-weight:700; margin:12px 0 4px 0; color:#27251F;'>"
                "🎧 Tu audio recibido:</p>",
                unsafe_allow_html=True,
            )
            st.audio(
                st.session_state.pending_audio,
                format=st.session_state.audio_mime,
            )

            st.markdown(
                "<p style='font-weight:700; margin:10px 0 4px 0; color:#27251F;'>"
                "🗣️ Audio transcrito (puedes corregirlo antes de enviarlo):</p>",
                unsafe_allow_html=True,
            )
            st.text_area(
                "Texto transcrito del pedido",
                key="texto_pedido",
                height=120,
                label_visibility="collapsed",
                placeholder="Ej: quiero dos Mega Crunch, unas papas con cheddar y una limonada",
            )

            if st.session_state.error_transcripcion:
                st.caption(f"⚠️ {st.session_state.error_transcripcion}")

            ya_aplicado = bool(
                st.session_state.texto_aplicado
                and st.session_state.texto_pedido.strip()
                == st.session_state.texto_aplicado.strip()
            )
            if ya_aplicado:
                st.success(
                    "✅ Este pedido ya está en tu carrito. Puedes ajustarlo ahí mismo "
                    "(cantidades, notas, quitar) o corregir el texto y volver a interpretarlo."
                )

            c_env, c_desc = st.columns(2)
            with c_env:
                enviar = st.button(
                    "🔁 Volver a interpretar" if ya_aplicado else "🧠 Interpretar pedido",
                    type="primary",
                    use_container_width=True,
                    key="btn_interpretar",
                )
            with c_desc:
                descartar = st.button(
                    "🗑️ Descartar", use_container_width=True, key="btn_descartar_audio"
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

            st.markdown(
                "<p style='color:#6C757D; font-size:0.82rem; margin-top:8px;'>"
                "El texto queda visible: si Zamy entendió algo distinto, corrígelo aquí o "
                "ajusta el pedido directamente en el carrito.</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("""
                <div style="text-align: center; margin-top: 15px;">
                    <p style="font-weight: bold; font-size: 1.05rem; margin-bottom: 4px; color: #27251F;">
                        Presiona el micrófono y realiza tu pedido
                    </p>
                    <p style="color: #6C757D; font-size: 0.9rem; margin-top: 0;">
                        Habla con tranquilidad. Puedes mencionar qué deseas comer, tus bebidas o hacer preguntas.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)
        st.write("💡 **Prueba rápida (sin micrófono):**")

        ejemplos = [
            ("🍔 'Dos Mega Crunch y una malteada'",
             "Quiero dos hamburguesas Mega Crunch y una malteada de Nutella"),
            ("🌱 'Algo sin gluten y una limonada'",
             "Busco algo sin gluten para comer y una limonada de frutos rojos"),
            ("🤔 'Recomiéndame algo rico'",
             "No sé qué pedir, recomiéndame algo rico de la carta"),
        ]
        for idx, (etiqueta, frase) in enumerate(ejemplos):
            if st.button(etiqueta, use_container_width=True, key=f"demo_{idx}"):
                st.session_state.pending_audio = None
                st.session_state.transcripcion_texto = frase
                st.session_state.texto_pedido = frase
                st.session_state.error_transcripcion = None
                interpretar_texto(frase)
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # COLUMNA CENTRAL: ASISTENTE VIRTUAL ZAMY + PEDIDO ENTENDIDO
    with col_dictamen:
        st.markdown(f"""
            <div class="voice-card">
                <div class="assistant-badge">
                    ⚙️ ATENCIÓN IA ASISTIDA
                </div>
                <div class="assistant-profile">
                    <div class="assistant-avatar">🤖</div>
                    <div>
                        <h3 style="margin: 0; color: {MCD_DARK};">Zamy Assistant <span style="color: #0D6EFD;">✓</span></h3>
                        <p style="margin: 2px 0 0 0; color: #6C757D; font-size: 0.9rem;">
                            Asistente Virtual de Pedidos · Voz IA
                        </p>
                    </div>
                </div>
                <hr style="border: none; border-top: 1px solid #EAEAEA; margin: 15px 0;">
                <div style="background-color: #F8F9FA; border-radius: 12px; padding: 18px; border-left: 4px solid {MCD_RED}; min-height: 120px;">
                    <p style="margin: 0; color: #495057; font-size: 0.95rem; line-height: 1.5;">
                        🎧 {html_seguro(st.session_state.zamy_response)}
                    </p>
                </div>
        """, unsafe_allow_html=True)

        if st.session_state.respuesta_audio:
            st.markdown(
                "<p style='font-weight:700; font-size:0.85rem; color:#6C757D; "
                "margin:12px 0 2px 0;'>🔊 Respuesta de Zamy en voz:</p>",
                unsafe_allow_html=True,
            )
            st.audio(
                st.session_state.respuesta_audio,
                format="audio/mp3",
                autoplay=st.session_state.voz_pendiente,
            )
            st.session_state.voz_pendiente = False

        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.error_ia:
            st.warning(st.session_state.error_ia)

        # --- Tarjeta del pedido interpretado por la IA ---
        res = st.session_state.interpretacion
        if res:
            menu_por_id = {p["id"]: p for p in menu_data}
            subtotal_ia = 0.0
            filas = ""
            for item in res["items"]:
                producto = menu_por_id.get(item["id"])
                if not producto:
                    continue
                linea_total = producto["precio"] * item["cantidad"]
                subtotal_ia += linea_total
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
                '<div style="display:flex; justify-content:space-between; margin-top:10px; font-size:0.9rem; color:#495057;">'
                f'<span>Subtotal</span><b>${subtotal_ia:.2f}</b>'
                '</div>'
                '<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#6C757D;">'
                f'<span>Impuesto 10%</span><span>${subtotal_ia * 0.10:.2f}</span>'
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

        if st.session_state.transcripcion_texto:
            st.caption(f"🗣️ **Audio transcrito:** «{st.session_state.transcripcion_texto}»")

    # COLUMNA DERECHA: CARRITO EDITABLE Y QR PAGO
    with col_cart:
        st.markdown(f"""
            <div style="background-color: {MCD_RED}; color: white; padding: 12px 15px; border-radius: 12px 12px 0 0; text-align: center;">
                <h3 style="margin: 0; color: white;">🛒 Carrito de Pedido</h3>
            </div>
            <div style="background-color: white; border: 1px solid #EAEAEA; border-top: none; border-radius: 0 0 12px 12px; padding: 15px;">
        """, unsafe_allow_html=True)

        if not st.session_state.carrito:
            st.info("El carrito está vacío. ¡Presiona el micrófono y habla para pedir!")
        else:
            st.caption("✏️ Edita cantidades, agrega notas o quita productos:")

            ids_eliminar = []
            for pos, item in enumerate(list(st.session_state.carrito)):
                c1, c2, c3 = st.columns([4.2, 1.6, 0.8])
                with c1:
                    st.markdown(
                        f"<div style='font-size:0.92rem; color:#27251F;'>"
                        f"{item['imagen']} <b>{html_seguro(item['nombre'])}</b></div>"
                        f"<div style='font-size:0.75rem; color:#6C757D;'>"
                        f"${item['precio']:.2f} c/u</div>",
                        unsafe_allow_html=True,
                    )
                    item["notas"] = st.text_input(
                        "Nota del producto",
                        value=item.get("notas", ""),
                        key=f"nota_{item['id']}_{pos}",
                        placeholder="Nota: sin cebolla, sin hielo...",
                        label_visibility="collapsed",
                    )
                with c2:
                    nueva_cant = st.number_input(
                        "Cantidad",
                        min_value=0,
                        max_value=20,
                        value=int(item["cantidad"]),
                        step=1,
                        key=f"cant_{item['id']}_{pos}",
                        label_visibility="collapsed",
                    )
                with c3:
                    st.markdown(
                        f"<div style='font-weight:800; font-size:0.9rem; color:{MCD_RED}; "
                        f"padding-top:6px;'>${item['precio'] * item['cantidad']:.2f}</div>",
                        unsafe_allow_html=True,
                    )

                if nueva_cant == 0:
                    ids_eliminar.append(item["id"])
                else:
                    item["cantidad"] = int(nueva_cant)

            if ids_eliminar:
                st.session_state.carrito = [
                    i for i in st.session_state.carrito if i["id"] not in ids_eliminar
                ]
                st.rerun()

            subtotal, impuesto, total = calcular_total()
            st.markdown("---")
            st.write(f"Subtotal: **${subtotal:.2f}**")
            st.write(f"Impuestos (10%): **${impuesto:.2f}**")
            st.markdown(
                f"<h3 style='color: {MCD_RED}; margin: 5px 0;'>Total: ${total:.2f}</h3>",
                unsafe_allow_html=True,
            )

            if st.button("🧹 Vaciar carrito", use_container_width=True, key="btn_vaciar"):
                st.session_state.carrito = []
                st.session_state.interpretacion = None
                st.session_state.pago_exitoso = False
                st.session_state.last_order_id = None
                responder_zamy("Carrito vacío. ¿Qué se te antoja ahora?", con_voz=False)
                st.rerun()

            if not st.session_state.pago_exitoso:
                if not st.session_state.last_order_id:
                    st.session_state.last_order_id = f"ORD-{random.randint(503, 999)}"

                order_id = st.session_state.last_order_id
                qr_img = generar_qr_pago(order_id, total)

                st.image(qr_img, caption=f"Escanea este QR para pagar orden {order_id}", width=180)

                if st.button("📱 Simular Escaneo y Pago de QR", type="primary", use_container_width=True):
                    progress_text = "🔄 Procesando simulación de pago con Zamy Pay... Por favor espere."
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
                            {"nombre": i["nombre"], "cant": i["cantidad"], "notas": i.get("notas", "")}
                            for i in st.session_state.carrito
                        ],
                        "total": round(total, 2),
                        "estado": "Pendiente",
                        "hora": time.strftime("%H:%M")
                    }
                    st.session_state.kitchen_orders.insert(0, nueva_comanda)
                    st.rerun()

            else:
                st.markdown(f"""
                    <div class="success-payment-box">
                        <h3 style="margin: 0; color: #155724;">✅ Pago realizado exitosamente</h3>
                        <p style="margin: 5px 0 0 0; font-size: 0.9rem;">
                            ¡Gracias por tu compra! Tu comanda ha sido notificada automáticamente a la cocina.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()

                if st.button("➕ Realizar Nuevo Pedido", use_container_width=True):
                    st.session_state.carrito = []
                    st.session_state.pago_exitoso = False
                    st.session_state.last_order_id = None
                    reiniciar_audio()
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------
# PESTAÑA 2: CARTA & MENÚ DIGITAL (ESTILO PEDIDOSYA)
# ------------------------------------------
with tab_menu:
    st.markdown("""
        <h2 style="font-size: 1.9rem; font-weight: 800; color: #27251F; margin-bottom: 5px;">
            Descubre estas opciones en Zamy 🍔
        </h2>
        <p style="color: #6C757D; font-size: 1rem; margin-bottom: 20px;">
            Explora nuestro menú especial estilo PedidosYa con imágenes de alta definición.
        </p>
    """, unsafe_allow_html=True)

    # Filtro por Categorías
    categorias = ["Todas"] + sorted(list(set(p["categoria"] for p in menu_data)))
    cat_sel = st.radio("Filtrar por categoría:", categorias, horizontal=True)

    prods_mostrar = menu_data if cat_sel == "Todas" else [p for p in menu_data if p["categoria"] == cat_sel]

    # Grid de tarjetas estilo PedidosYa (3 columnas)
    cols = st.columns(3, gap="medium")
    for idx, prod in enumerate(prods_mostrar):
        with cols[idx % 3]:
            badge_text = prod.get("badge", "Popular")
            st.markdown(f"""
                <div class="pedidosya-card">
                    <div class="pedidosya-img-box" style="background-image: url('{prod['imagen_url']}');">
                        <div class="pedidosya-badge-top">{badge_text}</div>
                    </div>
                    <div class="pedidosya-info-body">
                        <div class="pedidosya-header-row">
                            <h3 class="pedidosya-title">{prod['nombre']}</h3>
                            <div class="pedidosya-rating">★ {prod['rating']}</div>
                        </div>
                        <p style="font-size: 0.85rem; color: #666; margin: 6px 0 10px 0; line-height: 1.3;">
                            {prod['descripcion']}
                        </p>
                        <div class="pedidosya-sub-details">
                            <span>🕒 {prod['tiempo']}</span>
                            <span>🛵 Envío Gratis</span>
                        </div>
                        <div class="pedidosya-price-tag">${prod['precio']:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("🛒 Agregar al Pedido", key=f"btn_pya_{prod['id']}", use_container_width=True):
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
