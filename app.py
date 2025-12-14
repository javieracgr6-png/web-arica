import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import requests
import tempfile
import os

# 1. Configuración de la página y Estilos CSS
st.set_page_config(layout="wide", page_title="Descubre Arica", page_icon="🏔️")

# CSS personalizado para darle el look moderno de las fotos
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    /* Estilos para el Hero Section (Portada) */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        padding: 100px 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .hero h1 { font-size: 3.5rem; font-weight: 800; }
    
    /* Estilos para Tarjetas de Atractivos */
    .card-container {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .card-container:hover { transform: translateY(-5px); }
    .card-img { width: 100%; height: 200px; object-fit: cover; }
    .card-content { padding: 20px; }
    .card-cat { color: #ff6b6b; font-weight: bold; font-size: 0.9rem; text-transform: uppercase; }
    .card-title { font-size: 1.2rem; font-weight: bold; margin: 10px 0; color: #333; }
    .card-desc { color: #666; font-size: 0.9rem; }

    /* Widgets de clima y moneda */
    .widget-box {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 2. Datos de los Atractivos Turísticos (Base de Datos Local)
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Morro_de_arica_view.jpg", "desc": "Peñón costero y mirador natural, ícono de la ciudad y sitio histórico de la Guerra del Pacífico.", "time": "2 horas"},
        {"id": 2, "name": "Lago Chungará", "cat": "Naturaleza", "img": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Parinacota.jpg", "desc": "Uno de los lagos más altos del mundo, ubicado a 4.500 msnm frente al volcán Parinacota.", "time": "Full Day"},
        {"id": 3, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Cuevas_de_Anzota.jpg/640px-Cuevas_de_Anzota.jpg", "desc": "Impresionantes formaciones geológicas costeras con senderos habilitados para caminar junto al mar.", "time": "3 horas"},
        {"id": 4, "name": "Pueblo de Putre", "cat": "Cultural", "img": "https://upload.wikimedia.org/wikipedia/commons/c/c2/Putre_church.jpg", "desc": "Pueblo histórico de la precordillera, puerta de entrada al Altiplano y su cultura ancestral.", "time": "4 horas"},
        {"id": 5, "name": "Museo Arqueológico San Miguel", "cat": "Cultural", "img": "https://upload.wikimedia.org/wikipedia/commons/2/23/Museo_Arqueol%C3%B3gico_San_Miguel_de_Azapa.jpg", "desc": "Hogar de las Momias Chinchorro, las más antiguas del mundo, en el fértil Valle de Azapa.", "time": "3 horas"},
        {"id": 6, "name": "Catedral de San Marcos", "cat": "Arquitectura", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg/640px-Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg", "desc": "Icónica iglesia de hierro diseñada en los talleres de Gustave Eiffel, ubicada frente a la Plaza Colón.", "time": "1 hora"},
        {"id": 7, "name": "Humedal Río Lluta", "cat": "Naturaleza", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Desembocadura_del_rio_Lluta.jpg/640px-Desembocadura_del_rio_Lluta.jpg", "desc": "Santuario de la naturaleza en la desembocadura del río, vital para aves migratorias.", "time": "2 horas"},
        {"id": 8, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Lauca_National_Park.jpg/640px-Lauca_National_Park.jpg", "desc": "Reserva de la Biosfera con paisajes de volcanes, bofedales y fauna como vicuñas y flamencos.", "time": "Full Day"},
        {"id": 9, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Playa_Chinchorro%2C_Arica.jpg/640px-Playa_Chinchorro%2C_Arica.jpg", "desc": "Extensa playa de aguas cálidas en la zona norte de la ciudad, ideal para familias.", "time": "3 horas"},
        {"id": 10, "name": "Playa El Laucho", "cat": "Playa", "img": "https://upload.wikimedia.org/wikipedia/commons/1/18/Playa_El_Laucho_-_Arica.jpg", "desc": "Balneario popular protegido del viento, con bares y ambiente relajado.", "time": "3 horas"},
        {"id": 11, "name": "Presencias Tutelares", "cat": "Arte/Cultura", "img": "https://upload.wikimedia.org/wikipedia/commons/8/87/Presencias_Tutelares.jpg", "desc": "Conjunto de grandes esculturas ubicadas en medio de la pampa desértica.", "time": "1 hora"},
        {"id": 12, "name": "Playa La Lisera", "cat": "Playa", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Playa_La_Lisera_-_Arica.jpg/640px-Playa_La_Lisera_-_Arica.jpg", "desc": "Playa circular de aguas extremadamente tranquilas, perfecta para niños pequeños.", "time": "3 horas"},
        {"id": 13, "name": "Termas de Jurasi", "cat": "Relax", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Termas_de_Jurasi.jpg/640px-Termas_de_Jurasi.jpg", "desc": "Aguas termales rústicas de origen volcánico ubicadas cerca de Putre.", "time": "3 horas"},
    ]

# Manejo de estado para favoritos y navegación
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'page' not in st.session_state: st.session_state.page = 'Inicio'

# Función para añadir/quitar favoritos
def toggle_favorite(place_id):
    if place_id in st.session_state.favorites:
        st.session_state.favorites.remove(place_id)
    else:
        st.session_state.favorites.append(place_id)

# --- BARRA LATERAL DE NAVEGACIÓN ---
with st.sidebar:
    st.title("🧭 Navegación")
    if st.button("🏠 Inicio", use_container_width=True): st.session_state.page = 'Inicio'
    if st.button("📍 Atracciones", use_container_width=True): st.session_state.page = 'Atracciones'
    
    fav_count = len(st.session_state.favorites)
    plan_label = f"📅 Planificador ({fav_count})" if fav_count > 0 else "📅 Planificador"
    if st.button(plan_label, use_container_width=True): st.session_state.page = 'Planificador'
    
    st.divider()
    st.info("Desarrollado para el turismo en Arica y Parinacota.")


# ================= PÁGINA 1: INICIO =================
if st.session_state.page == 'Inicio':
    # Hero Section
    st.markdown("""
        <div class="hero">
            <h1>Arica y Parinacota</h1>
            <p style="font-size: 1.5rem;">Donde el desierto se encuentra con el mar y la historia vive.</p>
        </div>
    """, unsafe_allow_html=True)

    # Widgets de Clima y Moneda
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="widget-box"><h3>🌤️ Clima en Tiempo Real (Arica)</h3>', unsafe_allow_html=True)
        # Widget embed de weatherwidget.io
        st.components.v1.html("""
<a class="weatherwidget-io" href="https://forecast7.com/es/n18d48n70d31/arica/" data-label_1="ARICA" data-label_2="CLIMA ACTUAL" data-font="Roboto" data-icons="Climacons Animated" data-mode="Current" data-theme="pure" >ARICA CLIMA ACTUAL</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');</script>
        """, height=200)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="widget-box"><h3>💱 Conversor de Divisas (Ref.)</h3>', unsafe_allow_html=True)
        clp_amount = st.number_input("Monto en Pesos Chilenos (CLP)", min_value=0, value=10000, step=1000)
        # Tasa de cambio fija referencial (se podría conectar a una API real)
        usd_rate = 940 
        usd_amount = clp_amount / usd_rate
        st.metric(label="Aproximado en Dólares (USD)", value=f"${usd_amount:,.2f}")
        st.caption(f"Tasa referencial: 1 USD ≈ ${usd_rate} CLP")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🌟 Atractivos Destacados")
    
    # Grid de atractivos (Mostrando los primeros 6 como ejemplo)
    cols = st.columns(3)
    for i, place in enumerate(st.session_state.places[:6]):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card-container">
                <img src="{place['img']}" class="card-img">
                <div class="card-content">
                    <div class="card-cat">{place['cat']}</div>
                    <div class="card-title">{place['name']}</div>
                    <div class="card-desc">{place['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ================= PÁGINA 2: ATRACCIONES (SELECCIÓN) =================
elif st.session_state.page == 'Atracciones':
    st.title("📍 Explora y Selecciona tus Destinos")
    st.write("Marca las casillas de los lugares que deseas incluir en tu itinerario.")
    
    # Filtro de categoría
    categories = ["Todas"] + sorted(list(set([p['cat'] for p in st.session_state.places])))
    cat_filter = st.selectbox("Filtrar por tipo:", categories)

    filtered_places = st.session_state.places
    if cat_filter != "Todas":
        filtered_places = [p for p in st.session_state.places if p['cat'] == cat_filter]

    # Grid de selección usando st.columns y st.checkbox
    cols = st.columns(3)
    for i, place in enumerate(filtered_places):
        with cols[i % 3]:
            # Usamos un contenedor estándar de Streamlit aquí para el checkbox
            with st.container(border=True):
                st.image(place['img'], use_container_width=True, height=200)
                st.subheader(place['name'])
                st.caption(f"⏱️ Duración sugerida: {place['time']}")
                
                # Checkbox conectado al estado
                is_selected = place['id'] in st.session_state.favorites
                if st.checkbox(f"Visitar {place['name']}", value=is_selected, key=f"chk_{place['id']}"):
                    if place['id'] not in st.session_state.favorites:
                        st.session_state.favorites.append(place['id'])
                else:
                    if place['id'] in st.session_state.favorites:
                        st.session_state.favorites.remove(place['id'])


# ================= PÁGINA 3: PLANIFICADOR Y PDF =================
elif st.session_state.page == 'Planificador':
    st.title("📅 Tu Planificador de Viaje")

    selected_places_data = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
    num_selected = len(selected_places_data)

    if num_selected == 0:
        st.warning("⚠️ Aún no has seleccionado ningún atractivo. Ve a la página 'Atracciones' para elegir tus favoritos.")
        if st.button("Ir a seleccionar Atracciones"):
            st.session_state.page = 'Atracciones'
            st.rerun()
    else:
        st.success(f"Has seleccionado {num_selected} lugares para visitar.")
        
        # Input de días
        days = st.number_input("¿Cuántos días estarás de visita?", min_value=1, max_value=14, value=3)
        
        st.divider()
        st.subheader("Vista Previa del Itinerario Generado")

        # Lógica simple de distribución del itinerario
        import math
        items_per_day = math.ceil(num_selected / days)
        
        itinerary = {}
        for i in range(days):
            start_idx = i * items_per_day
            end_idx = start_idx + items_per_day
            itinerary[i+1] = selected_places_data[start_idx:end_idx]

        # Mostrar vista previa en pantalla
        for day, places in itinerary.items():
            with st.expander(f"Día {day}", expanded=True):
                if not places:
                    st.write("Día libre para descansar o explorar la ciudad.")
                for p in places:
                    c1, c2 = st.columns([1, 4])
                    with c1: st.image(p['img'], width=100)
                    with c2:
                        st.markdown(f"**{p['name']}** ({p['time']})")
                        st.caption(p['desc'])

        # --- GENERACIÓN DE PDF ---
        st.divider()
        st.subheader("Descargar Itinerario")

        # Función auxiliar para descargar imágenes de la web a un archivo temporal
        # (FPDF necesita archivos locales o accesibles directamente)
        def download_image_to_temp(url):
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=5)
                if response.status_code == 200:
                    # Crear archivo temporal
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    for chunk in response.iter_content(1024):
                        temp_file.write(chunk)
                    temp_file.close()
                    return temp_file.name
            except Exception as e:
                print(f"Error descargando imagen {url}: {e}")
                return None
            return None

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'Itinerario de Viaje - Arica y Parinacota', 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        def generate_pdf_with_images(itinerary_data):
            pdf = PDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            for day, places in itinerary_data.items():
                pdf.set_font('Arial', 'B', 14)
                pdf.set_fill_color(200, 220, 255)
                pdf.cell(0, 10, f'Día {day}', 1, 1, 'L', fill=True)
                pdf.ln(5)

                if not places:
                     pdf.set_font('Arial', '', 12)
                     pdf.cell(0, 10, 'Día libre.', 0, 1)
                     pdf.ln(10)
                     continue

                for p in places:
                    # Guardar posición Y actual
                    current_y = pdf.get_y()
                    
                    # 1. Manejo de la Imagen (lado izquierdo)
                    img_path = download_image_to_temp(p['img'])
                    if img_path:
                        # x, y, w, h (ajusta w y h según necesites)
                        pdf.image(img_path, x=10, y=current_y, w=40, h=30) 
                        
                    # 2. Manejo del Texto (lado derecho de la imagen)
                    # Mover el cursor a la derecha de la imagen (x=10 margen + 40 ancho + 5 espacio = 55)
                    pdf.set_xy(55, current_y) 
                    
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 8, p['name'], 0, 1)
                    
                    pdf.set_xy(55, pdf.get_y()) # Mantener alineación X
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 6, f"Duración sugerida: {p['time']}", 0, 1)
                    
                    pdf.set_xy(55, pdf.get_y()) # Mantener alineación X
                    pdf.set_font('Arial', '', 10)
                    # Multi_cell para descripción larga, ancho ajustado
                    pdf.multi_cell(130, 5, p['desc']) 
                    
                    # Asegurar espacio suficiente para el siguiente item, 
                    # considerando la altura de la imagen (30) y un margen (10)
                    next_y = current_y + 40 
                    if pdf.get_y() < next_y:
                         pdf.set_y(next_y)
                    
                    pdf.ln(5) # Espacio extra entre items
                    
                    # Limpiar archivo temporal
                    if img_path and os.path.exists(img_path):
                        os.remove(img_path)

                pdf.ln(10) # Espacio entre días
            
            return pdf.output(dest='S').encode('latin-1', 'replace') # Retorna bytes

        # Botón para generar y descargar
        if st.button("🖨️ Generar PDF con Imágenes"):
            with st.spinner("Generando tu PDF personalizado (descargando imágenes)..."):
                pdf_bytes = generate_pdf_with_images(itinerary)
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Itinerario_Arica.pdf" style="text-decoration:none; color:white; background-color:#FF4B4B; padding:12px 24px; border-radius:8px; font-weight:bold; display:inline-block;">⬇️ Descargar PDF Final</a>'
                st.markdown(href, unsafe_allow_html=True)
