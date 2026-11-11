# Zamy 🍔 — Atención y pedidos por voz con IA

MVP de auto-atención para fast food: el cliente **habla**, Gemini **transcribe** su audio,
**entiende** el pedido y lo arma usando el menú real (sin inventar productos). Luego el
cliente revisa el texto transcrito y **ajusta el pedido por escrito en el carrito**.

## Cómo funciona

```
🎙️ Audio del cliente
      │  Gemini (zamy_ai.transcribir_audio)
      ▼
🗣️ Texto transcrito (editable por el cliente)
      │  Gemini (zamy_ai.interpretar_pedido) + menu.json
      ▼
🧠 Pedido estructurado  →  {items, cantidades, notas, quitar, sugerencias, respuesta}
      ▼
🛒 Carrito editable  →  cambiar cantidades, notas, quitar productos
      ▼
📱 Pago QR simulado  →  👨‍🍳 comanda en cocina
```

Reglas que la IA respeta (system prompt en `zamy_ai.py`):

- Solo usa `id` reales del menú; nunca inventa productos ni precios.
- Interpreta cantidades naturales ("dos", "un par", "para dos personas").
- Si piden algo que no existe (ej. pizza), lo reporta y sugiere la alternativa más cercana.
- Respeta alergias y restricciones (sin gluten, sin cebolla, sin guacamole...).
- Si el cliente duda, recomienda; si pide quitar algo, lo quita del carrito.

## Instalación y ejecución

```powershell
py -m pip install -r requirements.txt
```

Crea un `.env` en la raíz del proyecto con tu clave de Gemini:

```
GEMINI_API_KEY=tu_clave_aqui
```

Y ejecuta:

```powershell
py -m streamlit run app.py
```

> Sin `GEMINI_API_KEY` la app sigue funcionando con un intérprete local por palabras clave
> (modo de respaldo), pero sin transcripción de audio real.

## Estructura

| Archivo | Rol |
| --- | --- |
| `app.py` | Interfaz Streamlit: pestañas Voz, Carta y Cocina; carrito editable; QR. |
| `zamy_ai.py` | Cliente Gemini: transcripción de audio + interpretación del pedido. |
| `menu.json` | Catálogo real (precios, ingredientes, alérgenos, imágenes). |
| `.streamlit/config.toml` | Tema visual (rojo Zamy). |

## Demo en 3 pasos

1. Pestaña **Atención & Pedidos por Voz** → micrófono → "quiero dos Mega Crunch y una malteada".
2. Corrige la transcripción si hace falta y presiona **Interpretar pedido**.
3. Revisa el pedido entendido, agrégalo al carrito, ajusta cantidades/notas y paga el QR.

Si no hay micrófono disponible, usa los botones de **Prueba rápida**.
