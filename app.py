import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import requests
import tempfile
import os

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(layout="wide", page_title="Descubre Arica y Parinacota", page_icon="🧭")

# Estilos CSS personalizados para imitar el diseño de tus capturas (Modo Oscuro/Cian)
st.markdown("""
<style>
    /* Colores Globales */
    :root {
        --primary-color: #008CBA;
        --bg-color: #0e1117;
        --text-color: #fafafa;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #008CBA !important;
    }
    
    /* Botones */
    div.stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #005f7f;
        border-color: #005f7f;
        color: white;
    }

    /* Tarjetas personalizadas (Simulación en Markdown) */
    .card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Hero Section Text */
    .hero-text {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: -webkit-linear-gradient(white, #aaaaaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Checkbox hack para que se vean más grandes */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATOS DE LOS ATRACTIVOS ---
# NOTA: Para las imágenes, estoy usando placeholders. 
# Si quieres tus propias fotos, sube una carpeta 'img' a tu repo y cambia las URLs por rutas locales o URLs públicas.

data_turismo = [
    {"id": 1, "nombre": "Morro de Arica", "categoria": "Cultural", "duracion": 2, "img": "https://placehold.co/400x300/png?text=Morro+de+Arica"},
    {"id": 2, "nombre": "Lago Chungará", "categoria": "Naturaleza", "duracion": 8, "img": "https://placehold.co/400x300/png?text=Lago+Chungara"},
    {"id": 3, "nombre": "Cuevas de Anzota", "categoria": "Naturaleza", "duracion": 3, "img": "https://placehold.co/400x300/png?text=Cuevas+Anzota"},
    {"id": 4, "nombre": "Putre", "categoria": "Cultural", "duracion": 5, "img": "https://placehold.co/400x300/png?text=Putre"},
    {"id": 5, "nombre": "Museo Arqueológico San Miguel de Azapa", "categoria": "Arqueológico", "duracion": 3, "img": "https://placehold.co/400x300/png?text=Museo+Azapa"},
    {"id": 6, "nombre": "Catedral San Marcos", "categoria": "Cultural", "duracion": 1, "img": "https://placehold.co/400x300/png?text=Catedral+San+Marcos"},
    {"id": 7, "nombre": "Humedal Río Lluta", "categoria": "Naturaleza", "duracion": 2, "img": "https://placehold.co/400x300/png?text=Humedal+Lluta"},
    {"id": 8, "nombre": "Parque Nacional Lauca", "categoria": "Naturaleza", "duracion": 8, "img": "https://placehold.co/400x300/png?text=PN+Lauca"},
    {"id": 9, "nombre": "Playa Chinchorro", "categoria": "Playa", "duracion": 3, "img": "https://placehold.co/400x300/png?text=Playa+Chinchorro"},
    {"id": 10, "nombre": "Playa El Laucho", "categoria": "Playa", "duracion": 3, "img": "https://placehold.co/400x300/png?text=Playa+El+Laucho"},
    {"id": 11, "nombre": "Presencias Tutelares", "categoria": "Arqueológico", "duracion": 2, "img": "https://placehold.co/400x300/png?text=Presencias+Tutelares"},
    {"id": 12, "nombre": "Playa La Lisera", "categoria": "Playa", "duracion": 3, "img": "https://placehold.co/400x300/png?text=Playa+La+Lisera"},
    {"id": 13, "nombre": "Termas de Jurasi", "categoria": "Naturaleza", "duracion": 4, "img": "https://placehold.co/400x300/png?text=Termas+Jurasi"},
]

# Inicializar estado de selección
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- 3. FUNCIONES AUXILIARES ---

def generar_pdf(itinerario_dias):
    """Genera un PDF con imágenes descargadas temporalmente"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Itinerario Arica y Parinacota", ln=True, align="C")
    pdf.ln(10)

    for dia, items in itinerario_dias.items():
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 140, 186) # Azul Cyan
        pdf.cell(0, 10, f"Día {dia}", ln=True)
        pdf.set_text_color(0, 0, 0) # Negro
        
        for item in items:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, item['nombre'], ln=True)
            
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, f"Categoría: {item['categoria']} | Duración: {item['duracion']} horas", ln=True)
            
            # Manejo de Imagen
            try:
                # Descargar imagen temporalmente para insertarla en el PDF
                response = requests.get(item['img'], stream=True)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                        for chunk in response.iter_content(1024):
                            tmp_file.write(chunk)
                        tmp_img_path = tmp_file.name
                    
                    # Insertar imagen (x, y, w, h)
                    pdf.image(tmp_img_path, x=10, w=50) # Ancho 50mm
                    pdf.ln(40) # Mover cursor abajo (altura img aprox)
                    os.unlink(tmp_img_path) # Borrar archivo temporal
                else:
                    pdf.ln(5)
            except Exception as e:
                pdf.cell(0, 5, "(Imagen no disponible)", ln=True)
                pdf.ln(5)
                
            pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Línea separadora
            pdf.ln(5)
            
        pdf.add_page() # Salto de página por día (opcional)

    return pdf.output(dest='S').encode('latin-1')

# --- 4. BARRA DE NAVEGACIÓN ---
# Usamos un menú simple en el sidebar
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Explorar Atractivos", "Planificador Inteligente"])

st.sidebar.markdown("---")
st.sidebar.info(f"📍 Atractivos seleccionados: **{len(st.session_state.seleccionados)}**")

# --- 5. LÓGICA DE LAS PÁGINAS ---

if opcion == "Inicio":
    # --- PÁGINA DE INICIO ---
    st.markdown('<h1 class="hero-text">Descubre la magia del norte de Chile</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Playas infinitas, valles fértiles, altiplano andino y milenaria cultura.</h3>", unsafe_allow_html=True)
    
    # Espaciador
    st.write("")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>☁️ Clima Actual - Arica</h3>
            <h1 style="color:white !important;">22°C</h1>
            <p>Soleado - Humedad 65%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="card">
            <h3>💲 Conversor de Divisas</h3>
            <p><b>1000 CLP</b> = 1.10 USD</p>
            <p>Dolar observado: $940 CLP</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.image("https://placehold.co/1200x400/005f7f/ffffff?text=Paisaje+Arica", use_container_width=True)

elif opcion == "Explorar Atractivos":
    # --- PÁGINA EXPLORAR ---
    st.title("🗺️ Atractivos Turísticos")
    st.write("Selecciona tus destinos favoritos para armar tu itinerario.")
    
    # Filtros
    categorias = ["Todos"] + sorted(list(set([x['categoria'] for x in data_turismo])))
    filtro = st.selectbox("Filtrar por categoría:", categorias)
    
    # Grid de atractivos
    items_mostrar = data_turismo if filtro == "Todos" else [x for x in data_turismo if x['categoria'] == filtro]
    
    cols = st.columns(3) # 3 columnas por fila
    
    for i, item in enumerate(items_mostrar):
        with cols[i % 3]:
            # Contenedor estilo tarjeta
            with st.container(border=True):
                st.image(item['img'], use_container_width=True)
                st.subheader(item['nombre'])
                st.caption(f"📍 {item['categoria']} | ⏱️ {item['duracion']} hrs")
                
                # Checkbox para seleccionar
                # Verificamos si ya estaba seleccionado
                is_selected = item['id'] in st.session_state.seleccionados
                
                if st.checkbox(f"Seleccionar {item['nombre']}", value=is_selected, key=f"chk_{item['id']}"):
                    if item['id'] not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(item['id'])
                else:
                    if item['id'] in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(item['id'])

elif opcion == "Planificador Inteligente":
    # --- PÁGINA PLANIFICADOR ---
    st.title("📅 Planifica tu viaje")
    
    col_config, col_resumen = st.columns([1, 2])
    
    with col_config:
        st.markdown("### Configuración")
        dias = st.number_input("¿Cuántos días estarás de visita?", min_value=1, max_value=7, value=3)
        
        st.markdown("### Tus Selecciones")
        if not st.session_state.seleccionados:
            st.warning("No has seleccionado atractivos aún. Ve a la pestaña 'Explorar'.")
        else:
            nombres_selec = [d['nombre'] for d in data_turismo if d['id'] in st.session_state.seleccionados]
            for nombre in nombres_selec:
                st.write(f"- {nombre}")
                
        if st.button("✨ Generar Itinerario", use_container_width=True):
            st.session_state.generado = True

    with col_resumen:
        if st.session_state.get('generado') and st.session_state.seleccionados:
            st.markdown("## 📋 Tu Itinerario Sugerido")
            
            # Obtener objetos completos de los IDs seleccionados
            items_obj = [d for d in data_turismo if d['id'] in st.session_state.seleccionados]
            
            # Algoritmo simple de distribución
            import math
            items_por_dia = math.ceil(len(items_obj) / dias)
            
            itinerario_final = {}
            
            # Mostrar itinerario en pantalla
            idx_item = 0
            for dia in range(1, dias + 1):
                itinerario_final[dia] = []
                with st.expander(f"Día {dia}", expanded=True):
                    for _ in range(items_por_dia):
                        if idx_item < len(items_obj):
                            act = items_obj[idx_item]
                            itinerario_final[dia].append(act)
                            
                            # Diseño de fila de itinerario
                            col_img, col_info = st.columns([1, 3])
                            with col_img:
                                st.image(act['img'], width=100)
                            with col_info:
                                st.subheader(act['nombre'])
                                st.write(f"⏱️ {act['duracion']} horas | {act['categoria']}")
                            st.divider()
                            idx_item += 1
            
            # Generar PDF
            st.success("¡Itinerario generado con éxito!")
            pdf_bytes = generar_pdf(itinerario_final)
            
            st.download_button(
                label="📥 Descargar PDF con Fotos",
                data=pdf_bytes,
                file_name="mi_itinerario_arica.pdf",
                mime="application/pdf",
                use_container_width=True
            )
