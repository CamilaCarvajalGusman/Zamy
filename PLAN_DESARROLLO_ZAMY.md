# Plan de Desarrollo Zamy (MVP Estilo Hackathon)

## 🎯 Visión General
**Zamy** es un servicio de pago y atención inteligente para restaurantes y negocios. Resuelve los problemas de inconsistencia y deficiencia en la atención al cliente tradicional ofreciendo una experiencia constante, amable y automatizada.

## 🏗️ Arquitectura Técnica
- **Frontend / UI**: Streamlit (Python) con vistas diferenciadas por rol (Cliente, Cocina y Administración).
- **Motor de IA / Chatbot**: Python + Google Gemini (`google-genai`): transcripción del audio del cliente, comprensión del pedido y system prompt especializado con el menú estructurado en JSON y gestión de carrito.
- **Pagos & QR**: Módulo en Python con la librería `qrcode` para generación y simulación de cobro dinámico.
- **Persistencia & Estado**: `st.session_state` / SQLite para sincronizar cliente y cocina en tiempo real.

---

## 🚀 Plan Paso a Paso

### Paso 1: Configuración de Datos y Motor de IA (`backend`)
- **Menú Estructurado (`menu.json`)**: Definición del catálogo de platos, precios, ingredientes, alérgenos y sugerencias de maridaje/combos.
- **System Prompt de Zamy**: Configuración del rol de la IA: tono cordial, respuesta a dudas del menú, recomendaciones personalizadas y venta cruzada (upselling).
- **Gestor de Carrito y Comandas**: Extracción estructurada de ítems seleccionados por el cliente durante la conversación para agregarlos automáticamente al pedido.

### Paso 2: Interfaz del Cliente (`Streamlit - Vista Cliente`)
- **Chat Interactivo (`st.chat_input` / `st.chat_message`)**: Diálogo natural con Zamy para consultas de la carta, filtros por restricciones alimenticias y armado de pedidos.
- **Sidebar de Menú y Carrito**: Visualización rápida del catálogo y resumen interactivo de la cuenta en tiempo real.
- **Checkout y Código QR Dinámico**: Generación de código QR para simulación de pago instantáneo y confirmación directa del pedido.

### Paso 3: Pantalla de Cocina y Dashboard Admin (`Streamlit - Vista Cocina / Admin`)
- **Navegación por Roles/Pestañas**: Uso de `st.tabs` o barra lateral para cambiar entre la vista de cliente, la cocina y el panel de administración.
- **Comanda en Vivo para Cocina**: Recepción automatizada de pedidos pagados/confirmados con actualización de estado (*Pendiente*, *En preparación*, *Listo / Entregado*).
- **Panel Admin & Demostración de Planes**: Dashboard con métricas clave (ventas del día, platos más vendidos) y selector para activar funciones de los planes *Básico*, *Premium* y *Extra Premium*.

### Paso 4: Polish, Script de Demo y Pitch (`Hackathon Ready`)
- **Carga de Datos de Prueba**: Menú atractivo con imágenes y descripciones reales.
- **Script del Pitch (Demo en Vivo de 3 Minutos)**:
  1. Muestra del problema (atención humana lenta/deficiente).
  2. Demostración de interacción fluida con Zamy (resolución de dudas alimenticias + pedido).
  3. Pago mediante QR y recepción instantánea del ticket en la pantalla de cocina.
  4. Explicación del modelo de suscripción y escalabilidad.

---

## 🛠️ Stack Tecnológico
- **Lenguaje**: Python 3.10+
- **Interfaz de Usuario**: Streamlit
- **IA / LLM**: Google Gemini API (`gemini-3.7-flash` con respaldo a `gemini-2.5-flash`) para voz y texto
- **Librerías principales**: `streamlit`, `qrcode`, `pillow`, `pydantic`
