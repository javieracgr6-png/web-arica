import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# 1. Configuración de la página
st.set_page_config(layout="wide", page_title="Descubre Arica", page_icon="🏔️")

# 2. Estilos CSS mejorados
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    
    /* Estilos de Tarjetas Turísticas */
    .card {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        overflow: hidden;
        border: 1px solid #eee;
        transition: transform 0.2s;
    }
    .card:hover { transform: scale(1.02); }
    
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
    
    /* Hero Section */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070');
        background-size: cover; background-position: center;
        padding: 80px 40px; border-radius: 15px; color: white; margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Base de Datos de Lugares
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Morro_de_arica_view.jpg", "desc": "Icono de la ciudad, vista panorámica del océano.", "lat": -18.4802, "lon": -70.3250, "time": "2 horas"},
        {"id": 2, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://cl.kvnoticias.com/wp-content/uploads/2023/07/Arica.jpg", "desc": "Aguas cálidas ideales para deportes acuáticos.", "lat": -18.4550, "lon": -70.3000, "time": "3 horas"},
        {"id": 3, "name": "Valle de Azapa", "cat": "Arqueológico", "img": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0d/16/61/8b/valle-de-azapa.jpg?w=1200&h=-1&s=1", "desc": "Fértil valle, aceitunas y momias Chinchorro.", "lat": -18.5100, "lon": -70.1800, "time": "4 horas"},
        {"id": 4, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "img": "https://www.chile.travel/wp-content/uploads/2021/07/lago-chungara-parque-nacional-lauca-1.jpg", "desc": "Volcanes y lago Chungará a 4.500m.", "lat": -18.2500, "lon": -69.2500, "time": "Full Day"},
        {"id": 5, "name": "Catedral San Marcos", "cat": "Cultural", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg/640px-Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg", "desc": "Diseño de Gustave Eiffel, Monumento Nacional.", "lat": -18.4779, "lon": -70.3207, "time": "1 hora"},
        {"id": 6, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://chileestuyo.cl/wp-content/uploads/2021/07/cuevas-de-anzota-arica.jpg", "desc": "Formaciones geológicas milenarias frente al mar.", "lat": -18.5500, "lon": -70.3300, "time": "3 horas"},
    ]

# 4. Gestión de Estado (Favoritos)
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio'

# Función CRÍTICA: Callback para manejar la selección sin errores
def toggle_favorite(place_id):
    if place_id in st.session_state.favorites:
        st.session_state.favorites.remove(place_id)
    else:
        st.session_state.favorites.append(place_id)

# Función de navegación
def set_page(page_name):
    st.session_state.page = page_name

# --- BARRA DE NAVEGACIÓN SUPERIOR ---
col_logo, col_menu = st.columns([1, 3])
with col_logo:
    st.markdown("### 🧭 Descubre Arica")
with col_menu:
    b1, b2, b3 = st.columns(3)
    if b1.button("🏠 Inicio", use_container_width=True): set_page('Inicio')
    if b2.button("🧭 Explorar", use_container_width=True): set_page('Explorar')
    # El contador se actualiza automáticamente
    count = len(st.session_state.favorites)
    label_plan = f"📅 Planificador ({count})" if count > 0 else "📅 Planificador"
    if b3.button(label_plan, use_container_width=True): set_page('Planificador')

st.divider()

# --- PÁGINA 1: INICIO ---
if st.session_state.page == 'Inicio':
    st.markdown("""
    <div class="hero">
        <h1 style='font-size:3.5rem;'>La magia del norte</h1>
        <p style='font-size:1.2rem;'>Playas, valles y altiplano en un solo destino.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 **Tip:** Ve a la pestaña 'Explorar' para seleccionar los lugares que quieres visitar.")

    # Muestra rápida de lugares (solo visual)
    cols = st.columns(3)
    for i, place in enumerate(st.session_state.places[:3]):
        with cols[i]:
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(place['desc'])

# --- PÁGINA 2: EXPLORAR (Aquí estaba el error) ---
elif st.session_state.page == 'Explorar':
    st.title("🧭 Atractivos Turísticos")
    st.markdown("Marca la casilla **'Seleccionar'** para añadir al planificador.")
    
    # Filtros
    c_search, c_filter = st.columns([2, 1])
    with c_search:
        search = st.text_input("🔍 Buscar destino...", "")
    with c_filter:
        cats = ["Todos", "Playa", "Histórico", "Naturaleza", "Cultural", "Aventura", "Arqueológico"]
        selected_cat = st.selectbox("Categoría:", cats)
    
    # Lógica de filtrado
    filtered_places = st.session_state.places
    if search:
        filtered_places = [p for p in filtered_places if search.lower() in p['name'].lower()]
    if selected_cat != "Todos":
        filtered_places = [p for p in filtered_places if p['cat'] == selected_cat]
        
    # Grid de tarjetas
    cols = st.columns(3)
    for index, place in enumerate(filtered_places):
        col = cols[index % 3]
        with col:
            # Tarjeta visual
            st.image(place['img'], use_container_width=True)
            st.markdown(f"##### {place['name']}")
            st.caption(f"📍 {place['cat']} | ⏱ {place['time']}")
            
            # --- CORRECCIÓN CLAVE ---
            # Usamos on_change para que la selección sea instantánea y segura
            is_checked = place['id'] in st.session_state.favorites
            st.checkbox(
                "Añadir al viaje", 
                value=is_checked, 
                key=f"chk_{place['id']}",
                on_change=toggle_favorite,
                args=(place['id'],) # Pasamos el ID a la función
            )
            st.divider()

# --- PÁGINA 3: PLANIFICADOR ---
elif st.session_state.page == 'Planificador':
    st.title("📅 Tu Itinerario de Viaje")
    
    if not st.session_state.favorites:
        st.warning("⚠️ No has seleccionado ningún destino aún. Vuelve a 'Explorar'.")
        if st.button("⬅️ Ir a Explorar"):
            set_page('Explorar')
            st.rerun()
    else:
        # Recuperar los objetos completos de los IDs favoritos
        my_places = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        
        c_conf, c_map = st.columns([1, 2])
        
        with c_conf:
            st.markdown("#### Configuración")
            days = st.number_input("Días disponibles:", min_value=1, max_value=10, value=3)
            st.success(f"Has seleccionado {len(my_places)} lugares.")
            
            # Generar lista simple
            st.markdown("---")
            st.markdown("**Lugares elegidos:**")
            for p in my_places:
                st.markdown(f"- {p['name']}")

        with c_map:
            st.markdown("#### Mapa de Ruta")
            st.map(pd.DataFrame(my_places), latitude='lat', longitude='lon', size=20, color='#0d8ca1')
        
        st.markdown("---")
        st.subheader("📋 Itinerario Sugerido")
        
        # Algoritmo de distribución simple
        import math
        items_per_day = math.ceil(len(my_places) / days)
        
        pdf_text = f"Itinerario Arica - {days} Dias\n\n"
        
        cols_days = st.columns(days)
        
        for d in range(days):
            day_num = d + 1
            # Usar columnas si son pocos días, o filas si son muchos
            container = cols_days[d] if d < len(cols_days) else st.container()
            
            with container:
                st.markdown(f"#### Día {day_num}")
                pdf_text += f"DIA {day_num}:\n"
                
                start = d * items_per_day
                end = start + items_per_day
                day_places = my_places[start:end]
                
                if not day_places:
                    st.write("🌴 Día libre / Playa / Compras")
                    pdf_text += " - Dia Libre\n"
                
                for p in day_places:
                    st.info(f"**{p['name']}**\n\n⏱ {p['time']}")
                    pdf_text += f" - {p['name']} ({p['time']})\n"
                
                pdf_text += "\n"

        # Generar PDF
        def create_pdf(text):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in text.split('\n'):
                pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=1)
            return pdf.output(dest='S').encode('latin-1')

        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = create_pdf(pdf_text)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Itinerario_Arica.pdf" style="background-color:#ff4b4b; color:white; padding:15px 25px; text-decoration:none; border-radius:10px; font-weight:bold;">📥 Descargar Itinerario PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
