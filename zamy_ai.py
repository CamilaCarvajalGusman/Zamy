"""Motor de IA de Zamy (Gemini).

Dos pasos, igual que en DiagnosticoAI:
1. ``transcribir_audio`` convierte la grabación de voz del cliente en texto.
2. ``interpretar_pedido`` lee ese texto (que el cliente puede corregir) y lo
   traduce a un pedido estructurado usando SOLO los productos del menú.

Si no hay ``GEMINI_API_KEY`` o la API falla, se usa un intérprete local por
palabras clave para que la demo nunca se quede sin responder.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any

MODELOS = (
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
)

_modelo_preferido: str | None = None
_cliente_cache: Any = None

NUMEROS = {
    "un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "par": 2, "docena": 12,
}

# Sinónimos extra para el intérprete local (respaldo sin API).
SINONIMOS_IDS: dict[str, list[str]] = {
    "zm1": ["mega crunch", "crunch", "hamburguesa", "burger", "doble carne"],
    "zm2": ["wrap", "pollo", "monster"],
    "zm3": ["smokey", "bacon", "bbq", "ahumada"],
    "za1": ["papas", "fries", "loaded", "cheddar"],
    "za2": ["tender", "tenders", "tiras", "nuggets", "crujiente"],
    "zb1": ["malteada", "shake", "batido", "nutella", "helado"],
    "zb2": ["limonada", "jugo", "frutos rojos", "refresco", "bebida"],
    "zp1": ["dona", "donas", "postre", "dulce"],
}

INSTRUCCIONES = """Eres Zamy, la asistente virtual de Zamy Fast Food (comida rápida: hamburguesas,
wraps, papas, malteadas, limonadas y postres). Atiendes pedidos por voz o por texto.

Reglas obligatorias:
- Usa EXCLUSIVAMENTE los productos del MENÚ entregado, referenciándolos por su "id".
  Nunca inventes productos, precios ni ids que no existan.
- Interpreta cantidades naturales ("dos", "un par", "para dos personas", "tres malteadas").
- Si el cliente pide algo que no está en el menú, ponlo en "no_disponibles" y en
  "sugerencias" ofrece la alternativa más parecida del menú.
- Si menciona alergias, restricciones o gustos (sin gluten, vegetariano, sin cebolla),
  respétalos: no agregues productos que contengan ese alérgeno y déjalo claro en "respuesta".
- Si pide personalizar (sin tocineta, sin hielo, extra salsa), escríbelo en "notas" del ítem.
- Si pide quitar algo que ya está en el carrito, usa "quitar".
- Si duda o pide recomendación ("algo rico", "recomiéndame", "qué me sugieres"), usa
  "sugerencias" y deja "items" vacío salvo que además esté pidiendo algo concreto.
- Si es solo una consulta del menú, responde la duda y deja "items" vacío.
- Si el texto es incomprensible, deja "items" vacío, explica en "aclaracion" y haz una
  pregunta corta y amable.
- "respuesta" debe ser un mensaje breve (máximo 45 palabras), cálido, en español neutro,
  sin listas ni markdown, mencionando lo que agregaste, quitaste, recomendaste o preguntaste.
- Los precios están en dólares y el impuesto es 10% (lo calcula la app, no lo inventes).

Devuelve SIEMPRE un JSON válido, sin texto adicional."""


# --------------------------------------------------------------------------
# Cliente Gemini
# --------------------------------------------------------------------------
def obtener_api_key() -> str | None:
    clave = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if clave:
        return clave
    try:
        import streamlit as st

        return (st.secrets.get("GEMINI_API_KEY") or "").strip() or None
    except Exception:
        return None


def ia_disponible() -> bool:
    return obtener_api_key() is not None


def _cliente():
    global _cliente_cache
    if _cliente_cache is None:
        from google import genai

        _cliente_cache = genai.Client(api_key=obtener_api_key())
    return _cliente_cache


def _generar(contents, config=None):
    """Prueba los modelos disponibles hasta que uno responda."""
    global _modelo_preferido

    cliente = _cliente()
    orden = ([_modelo_preferido] if _modelo_preferido else []) + [
        m for m in MODELOS if m != _modelo_preferido
    ]
    ultimo_error: Exception | None = None

    for modelo in orden:
        try:
            respuesta = cliente.models.generate_content(
                model=modelo, contents=contents, config=config
            )
            if respuesta is not None and (getattr(respuesta, "text", None) or "").strip():
                _modelo_preferido = modelo
                return respuesta
            ultimo_error = RuntimeError(f"{modelo} no devolvió texto")
        except Exception as exc:  # modelo inexistente, cuota, red, etc.
            ultimo_error = exc

    raise RuntimeError(f"No se pudo contactar a Gemini: {ultimo_error}")


def detectar_mime(audio_bytes: bytes, mime_declarado: str | None = None) -> str:
    """Adivina el formato real del audio por su firma de bytes."""
    if mime_declarado and mime_declarado.startswith("audio/"):
        return mime_declarado.split(";")[0].strip()
    if audio_bytes[:4] == b"RIFF":
        return "audio/wav"
    if audio_bytes[:4] == b"OggS":
        return "audio/ogg"
    if audio_bytes[:4] == b"\x1aE\xdf\xa3":
        return "audio/webm"
    if audio_bytes[:3] == b"ID3" or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3"):
        return "audio/mpeg"
    if audio_bytes[4:8] == b"ftyp":
        return "audio/mp4"
    return "audio/wav"


# --------------------------------------------------------------------------
# Paso 1: transcripción
# --------------------------------------------------------------------------
def transcribir_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribe literalmente el audio del cliente."""
    from google.genai import types

    prompt = (
        "Escucha este audio de un cliente en un restaurante de comida rápida. "
        "Transcribe literalmente, en español, todo lo que dice. No resumas, no interpretes "
        "y no agregues comentarios. Si no hay voz comprensible responde exactamente: "
        "(audio sin voz comprensible). Responde ÚNICAMENTE con la transcripción."
    )
    respuesta = _generar(
        [types.Part.from_bytes(data=audio_bytes, mime_type=mime_type), prompt]
    )
    return (respuesta.text or "").strip()


# --------------------------------------------------------------------------
# Paso 2: comprensión del pedido
# --------------------------------------------------------------------------
def _catalogo_texto(menu: list[dict]) -> str:
    lineas = []
    for p in menu:
        ingredientes = ", ".join(p.get("ingredientes", [])) or "n/d"
        alergenos = ", ".join(p.get("alergenos", [])) or "ninguno"
        lineas.append(
            f"- id={p['id']} | {p['nombre']} | categoría: {p.get('categoria', '')} | "
            f"${float(p.get('precio', 0)):.2f} | ingredientes: {ingredientes} | "
            f"alérgenos: {alergenos} | {p.get('descripcion', '')}"
        )
    return "\n".join(lineas)


def _carrito_texto(carrito: list[dict]) -> str:
    if not carrito:
        return "(vacío)"
    return "\n".join(
        f"- {i['cantidad']}x {i['nombre']} (id={i['id']})"
        + (f" | nota: {i['notas']}" if i.get("notas") else "")
        for i in carrito
    )


def validar_interpretacion(data: Any, menu: list[dict]) -> dict:
    """Normaliza y valida la respuesta del modelo contra el menú real."""
    if not isinstance(data, dict):
        data = {}

    menu_por_id = {p["id"]: p for p in menu}
    items: list[dict] = []

    for raw in data.get("items") or []:
        if not isinstance(raw, dict):
            continue
        pid = str(raw.get("id", "")).strip()
        if pid not in menu_por_id:
            continue
        try:
            cantidad = int(raw.get("cantidad", 1))
        except (TypeError, ValueError):
            cantidad = 1
        cantidad = max(1, min(cantidad, 20))
        notas = str(raw.get("notas") or "").strip()[:180]

        repetido = next(
            (i for i in items if i["id"] == pid and i["notas"] == notas), None
        )
        if repetido:
            repetido["cantidad"] = min(20, repetido["cantidad"] + cantidad)
        else:
            items.append({"id": pid, "cantidad": cantidad, "notas": notas})

    ids_pedidos = {i["id"] for i in items}
    quitar = [
        str(x)
        for x in (data.get("quitar") or [])
        if str(x) in menu_por_id and str(x) not in ids_pedidos
    ]
    sugerencias = []
    for x in data.get("sugerencias") or []:
        x = str(x)
        if x in menu_por_id and x not in ids_pedidos and x not in sugerencias:
            sugerencias.append(x)

    respuesta = str(data.get("respuesta") or "").strip()
    if not respuesta:
        respuesta = "Listo, ¿te agrego algo más a tu pedido?"

    return {
        "intencion": str(data.get("intencion") or "pedido").strip().lower(),
        "items": items,
        "quitar": quitar,
        "sugerencias": sugerencias[:3],
        "no_disponibles": [str(x)[:80] for x in (data.get("no_disponibles") or [])][:5],
        "respuesta": respuesta,
        "aclaracion": str(data.get("aclaracion") or "").strip()[:300],
    }


def interpretar_pedido(
    texto: str, menu: list[dict], carrito: list[dict] | None = None
) -> dict:
    """Convierte el texto libre del cliente en un pedido estructurado."""
    carrito = carrito or []

    if not ia_disponible():
        return interpretar_sin_ia(texto, menu, carrito)

    from google.genai import types

    prompt = f"""Pedido del cliente (texto escrito o transcripción de su voz):
\"\"\"{texto.strip()}\"\"\"

Carrito actual del cliente:
{_carrito_texto(carrito)}

MENÚ DISPONIBLE (usa solo estos ids):
{_catalogo_texto(menu)}

Responde SOLO con este JSON:
{{
  "intencion": "pedido | consulta | recomendacion | modificacion | saludo | otro",
  "items": [{{"id": "id_del_menu", "cantidad": 1, "notas": "sin cebolla"}}],
  "quitar": ["id_del_menu"],
  "sugerencias": ["id_del_menu"],
  "no_disponibles": ["producto pedido que no existe en el menú"],
  "respuesta": "mensaje breve y cálido para el cliente",
  "aclaracion": "qué faltó o supusiste, o cadena vacía"
}}"""

    config = types.GenerateContentConfig(
        system_instruction=INSTRUCCIONES,
        response_mime_type="application/json",
        temperature=0.2,
    )

    try:
        respuesta = _generar(prompt, config=config)
        data = json.loads(respuesta.text)
        resultado = validar_interpretacion(data, menu)
        resultado["modo"] = "gemini"
        return resultado
    except Exception as exc:
        resultado = interpretar_sin_ia(texto, menu, carrito)
        resultado["modo"] = "local"
        resultado["error_ia"] = str(exc)[:250]
        return resultado


# --------------------------------------------------------------------------
# Respaldo local (sin API): coincidencia por palabras clave
# --------------------------------------------------------------------------
def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


def _cantidad(texto_norm: str, posicion: int) -> int:
    previo = texto_norm[max(0, posicion - 32) : posicion]
    for palabra in reversed(previo.split()):
        if palabra.isdigit() and 1 <= int(palabra) <= 20:
            return int(palabra)
        if palabra in NUMEROS:
            return NUMEROS[palabra]
    return 1


def _nota(texto_norm: str) -> str:
    match = re.search(r"\bsin ([a-z ]{2,25})", texto_norm)
    if not match:
        return ""
    detalle = " ".join(match.group(1).split()[:3])
    return f"sin {detalle}"


SEPARADORES = re.compile(r"\s+y\s+|\s+con\s+|,|;|\s+tambien\s+|\s+mas\s+|\s+ademas\s+")
PALABRAS_QUITAR = ("quita", "quitar", "elimina", "borra", "saca", "remueve")


def _segmentos(texto_norm: str) -> list[str]:
    partes = [p.strip() for p in SEPARADORES.split(texto_norm)]
    return [p for p in partes if p]


def _claves_producto(producto: dict) -> set[str]:
    claves = set(SINONIMOS_IDS.get(producto["id"], []))
    nombre = _normalizar(producto["nombre"]).replace("zamy", "")
    claves.update(t for t in nombre.split() if len(t) > 3)
    claves.update(_normalizar(i) for i in producto.get("ingredientes", []))
    return {c for c in claves if c}


def _mejor_producto(segmento: str, menu: list[dict]) -> dict | None:
    mejor: tuple[int, int, int, dict] | None = None
    for producto in menu:
        coincidencias = [c for c in _claves_producto(producto) if c in segmento]
        if not coincidencias:
            continue
        candidato = (
            len(coincidencias),
            max(len(c) for c in coincidencias),
            -segmento.find(min(coincidencias, key=segmento.find)),
            producto,
        )
        if mejor is None or candidato[:3] > mejor[:3]:
            mejor = candidato
    return mejor[3] if mejor else None


def _productos_aptos(menu: list[dict], alergeno: str) -> list[dict]:
    return [
        p
        for p in menu
        if alergeno not in [_normalizar(a) for a in p.get("alergenos", [])]
    ]


def interpretar_sin_ia(
    texto: str, menu: list[dict], carrito: list[dict] | None = None
) -> dict:
    """Intérprete de respaldo: separa la frase por bloques y busca productos por palabras clave."""
    carrito = carrito or []
    texto_norm = _normalizar(texto or "")
    items: list[dict] = []
    quitar: list[str] = []
    pide_quitar = any(p in texto_norm for p in PALABRAS_QUITAR)

    for segmento in _segmentos(texto_norm):
        producto = _mejor_producto(segmento, menu)
        if not producto:
            continue

        if pide_quitar and any(p in segmento for p in PALABRAS_QUITAR):
            if any(i["id"] == producto["id"] for i in carrito):
                quitar.append(producto["id"])
            continue

        existente = next((i for i in items if i["id"] == producto["id"]), None)
        if existente:
            existente["cantidad"] = max(
                existente["cantidad"], _cantidad(segmento, len(segmento))
            )
            continue

        items.append(
            {
                "id": producto["id"],
                "cantidad": _cantidad(segmento, len(segmento)),
                "notas": _nota(segmento),
            }
        )

    # Restricciones alimenticias: ofrecer solo lo apto
    restriccion = next(
        (a for a in ("gluten", "lactosa", "lacteos") if a in texto_norm and "sin " + a in texto_norm),
        None,
    )
    if not items and restriccion:
        alergeno = "gluten" if restriccion == "gluten" else "lacteos"
        aptos = _productos_aptos(menu, alergeno)
        nombres = ", ".join(p["nombre"] for p in aptos[:3]) or "opciones de la carta"
        return {
            "intencion": "consulta",
            "items": [],
            "quitar": [],
            "sugerencias": [p["id"] for p in aptos[:3]],
            "no_disponibles": [],
            "respuesta": f"Sin {restriccion} puedes pedir: {nombres}. ¿Te agrego alguno?",
            "aclaracion": "Se filtraron los productos que contienen ese alérgeno.",
            "modo": "local",
        }

    sugerencias = [
        p["id"]
        for p in sorted(menu, key=lambda x: float(x.get("rating", 0)), reverse=True)
        if p["id"] not in {i["id"] for i in items}
    ][:2]

    if items:
        nombres = ", ".join(
            f"{i['cantidad']}x {next(p['nombre'] for p in menu if p['id'] == i['id'])}"
            for i in items
        )
        respuesta = f"Perfecto, entendí: {nombres}. Revisa tu carrito y confirma."
    elif quitar:
        respuesta = "Listo, quité esos productos de tu carrito."
    elif any(p in texto_norm for p in ("recomienda", "sugiere", "recomiendame", "opciones")):
        respuesta = "Te recomiendo la Mega Crunch Burger con Loaded Fries y una malteada de Nutella."
    else:
        respuesta = (
            "No encontré ese producto en el menú. Dime qué se te antoja y te sugiero "
            "algo parecido de la carta."
        )

    return {
        "intencion": "pedido" if items else ("modificacion" if quitar else "consulta"),
        "items": items,
        "quitar": quitar,
        "sugerencias": sugerencias,
        "no_disponibles": [],
        "respuesta": respuesta,
        "aclaracion": "",
        "modo": "local",
    }
