import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="Descubre Arica", page_icon="🏔️")

# --- ESTILOS CSS (Para que se vea idéntico al diseño) ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    
    /* Estilos de Tarjetas Turísticas */
    .card {
        background-color: white;
        border-radius: 15px;
        padding: 0px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        overflow: hidden;
        border: 1px solid #eee;
    }
    .card-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
    .card-content { padding: 15px; }
    .card-tag {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: inline-block;
    }
    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #333; }
    .card-desc { font-size: 13px; color: #666; margin-bottom: 10px; height: 60px; overflow: hidden; }
    .card-meta { font-size: 12px; color: #888; display: flex; justify-content: space-between; }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070');
        background-size: cover; background-position: center;
        padding: 80px 40px; border-radius: 15px; color: white; margin-bottom: 30px;
    }
    
    /* Timeline del Planificador */
    .day-header { background-color: #0d8ca1; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-top: 20px; font-weight: bold;}
    .timeline-item { border-left: 2px solid #0d8ca1; margin-left: 20px; padding-left: 20px; padding-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- DATOS: LUGARES REALES DE ARICA ---
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Morro_de_arica_view.jpg", "desc": "Icono de la ciudad, ofrece una vista panorámica del océano y la ciudad.", "lat": -18.4802, "lon": -70.3250, "time": "2 horas"},
        {"id": 2, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://cl.kvnoticias.com/wp-content/uploads/2023/07/Arica.jpg", "desc": "Playa de aguas cálidas ideal para deportes acuáticos y caminatas.", "lat": -18.4550, "lon": -70.3000, "time": "3 horas"},
        {"id": 3, "name": "Valle de Azapa", "cat": "Arqueológico", "img": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0d/16/61/8b/valle-de-azapa.jpg?w=1200&h=-1&s=1", "desc": "Fértil valle famoso por sus aceitunas y el Museo San Miguel.", "lat": -18.5100, "lon": -70.1800, "time": "4 horas"},
        {"id": 4, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "img": "https://www.chile.travel/wp-content/uploads/2021/07/lago-chungara-parque-nacional-lauca-1.jpg", "desc": "Reserva de la biosfera con volcanes y el lago Chungará a 4.500m.", "lat": -18.2500, "lon": -69.2500, "time": "Full Day"},
        {"id": 5, "name": "Catedral San Marcos", "cat": "Cultural", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg/640px-Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg", "desc": "Diseñada por Gustave Eiffel, es Monumento Nacional.", "lat": -18.4779, "lon": -70.3207, "time": "1 hora"},
        {"id": 6, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://chileestuyo.cl/wp-content/uploads/2021/07/cuevas-de-anzota-arica.jpg", "desc": "Formaciones geológicas milenarias frente al mar.", "lat": -18.5500, "lon": -70.3300, "time": "3 horas"},
    ]

# Gestión de favoritos en memoria
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio'

# Funciones de Navegación
def set_page(page_name):
    st.session_state.page = page_name

# --- BARRA DE NAVEGACIÓN ---
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("### 🧭 Descubre Arica")
with col2:
    menu_c1, menu_c2, menu_c3 = st.columns(3)
    if menu_c1.button("🏠 Inicio", use_container_width=True): set_page('Inicio')
    if menu_c2.button("🧭 Explorar", use_container_width=True): set_page('Explorar')
    fav_count = len(st.session_state.favorites)
    if menu_c3.button(f"📅 Planificador ({fav_count})", use_container_width=True): set_page('Planificador')

st.divider()

# --- PÁGINA 1: INICIO ---
if st.session_state.page == 'Inicio':
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1 style='font-size:3.5rem;'>La magia del norte</h1>
        <p style='font-size:1.2rem;'>Playas, valles y altiplano en un solo destino.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Widget Clima (Simplificado)
    c1, c2 = st.columns(2)
    with c1:
        st.info("☁️ **Clima en Arica:** 22°C Soleado | 💧 Humedad: 65%")
    with c2:
        st.success("💲 **USD a CLP:** $1 USD = $935 CLP")
        
    st.subheader("🌟 Destacados de la Región")
    st.write("Continúa en la sección 'Explorar' para seleccionar tus favoritos.")
    
    # Mostrar 3 destacados estilo card
    cols = st.columns(3)
    for i, place in enumerate(st.session_state.places[:3]):
        with cols[i]:
            st.markdown(f"""
            <div class="card">
                <img src="{place['img']}" class="card-img">
                <div class="card-content">
                    <span class="card-tag">{place['cat']}</span>
                    <div class="card-title">{place['name']}</div>
                    <div class="card-desc">{place['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- PÁGINA 2: EXPLORAR (Selección) ---
elif st.session_state.page == 'Explorar':
    st.title("🧭 Atractivos Turísticos")
    st.write("Selecciona tus destinos favoritos marcando la casilla ✅")
    
    # Filtros
    search = st.text_input("🔍 Buscar destino...", "")
    cats = ["Todos", "Playa", "Histórico", "Naturaleza", "Cultural", "Aventura", "Arqueológico"]
    selected_cat = st.selectbox("Filtrar por categoría:", cats)
    
    # Lógica de filtrado
    filtered_places = st.session_state.places
    if search:
        filtered_places = [p for p in filtered_places if search.lower() in p['name'].lower()]
    if selected_cat != "Todos":
        filtered_places = [p for p in filtered_places if p['cat'] == selected_cat]
        
    # Grid de tarjetas con Checkbox
    cols = st.columns(3)
    for index, place in enumerate(filtered_places):
        col = cols[index % 3]
        with col:
            # Renderizar Imagen y Texto
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(f"{place['cat']} | ⏱ {place['time']}")
            
            # Checkbox para seleccionar
            is_fav = place['id'] in st.session_state.favorites
            if st.checkbox("Seleccionar", value=is_fav, key=f"chk_{place['id']}"):
                if place['id'] not in st.session_state.favorites:
                    st.session_state.favorites.append(place['id'])
            else:
                if place['id'] in st.session_state.favorites:
                    st.session_state.favorites.remove(place['id'])
            st.divider()

# --- PÁGINA 3: PLANIFICADOR ---
elif st.session_state.page == 'Planificador':
    st.title("📅 Planifica tu viaje")
    
    if not st.session_state.favorites:
        st.warning("⚠️ Aún no has seleccionado destinos. Ve a la sección 'Explorar'.")
    else:
        # 1. Configuración de días
        col_days, col_map = st.columns([1, 2])
        
        with col_days:
            st.markdown("##### ¿Cuántos días estarás de visita?")
            days = st.number_input("Días", min_value=1, max_value=7, value=3)
            
            # Obtener objetos completos de los favoritos
            my_places = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
            
            # Lógica simple de distribución
            import math
            items_per_day = math.ceil(len(my_places) / days)
            
            if st.button("✨ Generar Itinerario", type="primary"):
                st.session_state.generated = True
        
        with col_map:
            # Mapa con los puntos seleccionados
            df_map = pd.DataFrame(my_places)
            st.map(df_map, latitude='lat', longitude='lon', size=20, color='#0d8ca1')

        # 2. Mostrar Itinerario Generado
        if st.session_state.get('generated'):
            st.markdown("---")
            st.subheader("📋 Tu Itinerario Sugerido")
            
            pdf_text = "Itinerario Arica y Parinacota\n\n"
            
            for d in range(days):
                day_num = d + 1
                st.markdown(f"<div class='day-header'>Día {day_num}</div>", unsafe_allow_html=True)
                pdf_text += f"DIA {day_num}:\n"
                
                # Coger los items para este día
                start = d * items_per_day
                end = start + items_per_day
                day_places = my_places[start:end]
                
                if not day_places:
                    st.write("  *Día libre para descansar o recorrer el centro.*")
                    pdf_text += "  - Día Libre\n"
                
                for p in day_places:
                    st.markdown(f"""
                    <div class="timeline-item">
                        <strong>{p['name']}</strong><br>
                        <span style="color:gray">📍 {p['desc']} ({p['time']})</span>
                    </div>
                    """, unsafe_allow_html=True)
                    pdf_text += f"  - {p['name']} ({p['time']})\n"
                pdf_text += "\n"

            # 3. Botón descargar PDF
            st.markdown("---")
            
            # Generar PDF simple
            def create_pdf(text):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in text.split('\n'):
                    pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=1, align='L')
                return pdf.output(dest='S').encode('latin-1')

            pdf_bytes = create_pdf(pdf_text)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="mi_itinerario_arica.pdf" style="text-decoration:none; background-color:#ff4b4b; color:white; padding:10px 20px; border-radius:5px;">📥 Descargar Itinerario en PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
