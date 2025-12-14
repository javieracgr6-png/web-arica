import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# 1. Configuración de la página
st.set_page_config(layout="wide", page_title="Descubre Arica y Parinacota", page_icon="🏔️")

# 2. Estilos CSS (CORREGIDO PARA QUE SE VEAN LAS LETRAS)
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    
    /* Estilo de Tarjetas */
    .card {
        background-color: white; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px; overflow: hidden; border: 1px solid #eee; transition: transform 0.2s;
        height: 100%;
    }
    .card:hover { transform: scale(1.02); }
    
    /* Estilo Hero */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070');
        background-size: cover; background-position: center; padding: 80px 40px; border-radius: 15px; color: white; margin-bottom: 30px;
    }
    
    /* Cajas de Info (Clima/Divisas) - CORRECCIÓN DE COLOR DE TEXTO */
    .info-box {
        background-color: white; 
        padding: 20px; 
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
        border: 1px solid #e0e0e0; 
        height: 100%;
    }
    
    /* Forzamos que TODO el texto dentro de info-box sea oscuro */
    .info-box, .info-box h5, .info-box p, .info-box span, .info-box div {
        color: #333333 !important;
    }
    
    /* Texto específico del precio */
    .price-text { font-size: 24px; font-weight: bold; color: #0d8ca1 !important; }
</style>
""", unsafe_allow_html=True)

# 3. Datos Completos (CON IMÁGENES REPARADAS)
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://geositiosdechile.sernageomin.cl/wp-content/uploads/sites/4/2024/05/Morro-de-Arica.jpg", "desc": "Icono de la ciudad, vista panorámica.", "location": "Centro de Arica", "time_str": "2 horas", "hours": 2, "lat": -18.4802, "lon": -70.3250},
        {"id": 2, "name": "Lago Chungará", "cat": "Naturaleza", "img": "https://mayurutour.com/wp-content/uploads/2020/01/Lago-Chungara-Parque-Nacional-Lauca.png", "desc": "Uno de los lagos más altos del mundo.", "location": "Altiplano, Parque Lauca", "time_str": "Full Day", "hours": 8, "lat": -18.2500, "lon": -69.1667},
        {"id": 3, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://www.costachinchorro.cl/ccc23/wp-content/uploads/2023/04/DSF8586-1024x683.jpg", "desc": "Formaciones geológicas milenarias.", "location": "Sector sur, a 12 km del centro", "time_str": "3 horas", "hours": 3, "lat": -18.5500, "lon": -70.3300},
        {"id": 4, "name": "Pueblo de Putre", "cat": "Cultural", "img": "https://images.visitchile.com/destinos/364_putre.jpg", "desc": "Capital de la provincia de Parinacota.", "location": "Precordillera, a 145 km de Arica", "time_str": "4 horas", "hours": 4, "lat": -18.1950, "lon": -69.5600},
        {"id": 5, "name": "Museo Arqueológico Azapa", "cat": "Cultural", "img": "https://www.uta.cl/web/site/artic/20140814/imag/foto_0000000120140814095603.jpg", "desc": "Hogar de las momias Chinchorro.", "location": "Valle de Azapa, km 12", "time_str": "3 horas", "hours": 3, "lat": -18.5150, "lon": -70.1800},
        {"id": 6, "name": "Catedral San Marcos", "cat": "Histórico", "img": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/15/46/18/3f/img-20181023-141007-02.jpg?w=1200&h=1200&s=1", "desc": "Diseñada por Gustave Eiffel.", "location": "Plaza Colón, Centro", "time_str": "1 hora", "hours": 1, "lat": -18.4779, "lon": -70.3207},
        {"id": 7, "name": "Humedal Río Lluta", "cat": "Naturaleza", "img": "https://aricasiempreactiva.cl/wp-content/uploads/2021/06/Humedal-Rio-Lluta-grupo-de-aves-migratorias-II-Region-de-Arica-y-Parinacota.jpg", "desc": "Santuario de la naturaleza y aves.", "location": "Desembocadura Río Lluta", "time_str": "2 horas", "hours": 2, "lat": -18.4167, "lon": -70.3167},
        {"id": 8, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "img": "https://redturismochile.cl/wp-content/uploads/2024/01/Parque-Nacioanl-Lauca-Region-Arica-y-Parinacota-.jpg", "desc": "Reserva de la biosfera, volcanes y fauna.", "location": "Altiplano Andino", "time_str": "Full Day", "hours": 9, "lat": -18.1833, "lon": -69.2333},
        {"id": 9, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://aricasiempreactiva.cl/wp-content/uploads/2020/11/Playa-Chinchorro-vista-hacia-Morro-de-Arica-1900x785px-1.jpg", "desc": "Aguas cálidas y paseo costero.", "location": "Zona Norte de Arica", "time_str": "3 horas", "hours": 3, "lat": -18.4550, "lon": -70.3000},
        {"id": 10, "name": "Playa El Laucho", "cat": "Playa", "img": "https://www.costachinchorro.cl/ccc23/wp-content/uploads/2023/05/DSCF5033-1024x682.jpg", "desc": "Playa balneario con oleaje suave.", "location": "Av. Comandante San Martín", "time_str": "3 horas", "hours": 3, "lat": -18.4880, "lon": -70.3250},
        {"id": 11, "name": "Presencias Tutelares", "cat": "Cultural", "img": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg0Rbukx0WSTPWXz2r19DIVFS2Kk8ezLtmq1n8hWLT0G-cheXUERy1bl-kozPeLoc3wgHyzOHL1iScRqm1HHdcmZvAWerHJeFwJ-O3B_uQNeHEJ8wyfFUsk3O_-3wc4oi3X42nAC5ptimU/s1600/_MG_1207.JPG", "desc": "Esculturas gigantes en el desierto.", "location": "Pampa de Chaca, Panamericana", "time_str": "1 hora", "hours": 1, "lat": -18.6667, "lon": -70.1833},
        {"id": 12, "name": "Playa La Lisera", "cat": "Playa", "img": "https://aricasiempreactiva.cl/wp-content/uploads/2020/11/Playa-La-Lisera-Arica-Vista-Panoramica-1900x785-1.jpg", "desc": "Ideal para familias y natación.", "location": "Sur de Arica", "time_str": "3 horas", "hours": 3, "lat": -18.4950, "lon": -70.3280},
        {"id": 13, "name": "Termas de Jurasi", "cat": "Relax", "img": "https://chileestuyo.cl/wp-content/uploads/2015/07/termas-de-jurasi.jpg", "desc": "Aguas termales medicinales.", "location": "Cerca de Putre", "time_str": "3 horas", "hours": 3, "lat": -18.2000, "lon": -69.5800},
    ]

# Gestión de Estado
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'page' not in st.session_state: st.session_state.page = 'Inicio'

def toggle_favorite(place_id):
    if place_id in st.session_state.favorites: st.session_state.favorites.remove(place_id)
    else: st.session_state.favorites.append(place_id)

def set_page(page_name): st.session_state.page = page_name

# --- NAVEGACIÓN ---
c1, c2 = st.columns([1, 3])
with c1: st.markdown("### 🧭 Descubre Arica")
with c2:
    b1, b2, b3 = st.columns(3)
    if b1.button("🏠 Inicio", use_container_width=True): set_page('Inicio')
    if b2.button("🧭 Explorar", use_container_width=True): set_page('Explorar')
    count = len(st.session_state.favorites)
    if b3.button(f"📅 Planificador ({count})", use_container_width=True): set_page('Planificador')

st.divider()

# --- PÁGINA 1: INICIO ---
if st.session_state.page == 'Inicio':
    # Hero
    st.markdown("""<div class="hero"><h1>Descubre la magia del norte de Chile</h1><p>Playas infinitas, valles fértiles y cultura milenaria.</p></div>""", unsafe_allow_html=True)
    
    # Clima y Divisas
    col_clima, col_divisas = st.columns(2)
    with col_clima:
        # Usamos HTML puro para garantizar que el texto sea negro y no dependa del tema de Streamlit
        st.markdown("""
        <div class="info-box">
            <h5>☁️ Clima Actual - Arica</h5>
            <div style="display: flex; align-items: center; justify-content: space-around;">
                <div style="font-size: 40px;">☀️</div>
                <div style="text-align: center;">
                    <div style="font-size: 16px;">Soleado</div>
                    <div style="font-size: 32px; font-weight: bold;">22°C</div>
                </div>
                <div style="font-size: 14px; color: #555;">
                    💧 Humedad: 65%<br>
                    🍃 Viento: 12 km/h
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_divisas:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("<h5>💲 Conversor</h5>", unsafe_allow_html=True)
        
        # Inputs nativos de Streamlit (se adaptan, pero el fondo es blanco)
        amount = st.number_input("Monto", 1000, 100000, 1000)
        st.markdown(f"""
        <div style="margin-top: 10px;">
            Aprox: <span class="price-text">${amount/935:,.2f} USD</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # SECCIÓN DESTACADOS
    st.write("")
    st.subheader("🌟 Destacados de la Región")
    st.info("💡 **Tip:** Ve a la pestaña **'Explorar'** para seleccionar tus lugares favoritos y generar tu itinerario automático.")
    
    # Galería visual
    cols = st.columns(4)
    for i, place in enumerate(st.session_state.places):
        with cols[i % 4]:
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(place['cat'])

# --- PÁGINA 2: EXPLORAR ---
elif st.session_state.page == 'Explorar':
    st.title("🧭 Selecciona tus Favoritos")
    st.markdown("Marca los lugares que quieres visitar para armar tu plan.")
    
    search = st.text_input("🔍 Buscar lugar...", "")
    filtered = [p for p in st.session_state.places if search.lower() in p['name'].lower()]
    
    cols = st.columns(3)
    for i, place in enumerate(filtered):
        with cols[i % 3]:
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(f"{place['location']} | ⏱ {place['time_str']}")
            st.checkbox("Añadir al viaje", value=place['id'] in st.session_state.favorites, key=f"chk_{place['id']}", on_change=toggle_favorite, args=(place['id'],))
            st.divider()

# --- PÁGINA 3: PLANIFICADOR ---
elif st.session_state.page == 'Planificador':
    st.title("📅 Planifica tu viaje")
    
    if not st.session_state.favorites:
        st.warning("Primero selecciona lugares en la pestaña 'Explorar'.")
    else:
        my_places = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        days = st.number_input("Días de viaje", 1, 10, 3)
        
        c_list, c_map = st.columns([1, 2])
        with c_list:
            st.write("**Lugares elegidos:**")
            for p in my_places: st.write(f"- {p['name']}")
        with c_map:
            st.map(pd.DataFrame(my_places), latitude='lat', longitude='lon', size=20, color='#0d8ca1')
        
        # Generar PDF
        class PDF(FPDF):
            def header(self): pass

        def generate_pdf(places, n_days):
            pdf = PDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Itinerario Arica y Parinacota', ln=True, align='C')
            pdf.ln(10)
            
            import math
            items = math.ceil(len(places) / n_days)
            
            for d in range(n_days):
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f'Día {d+1}', ln=True)
                
                day_places = places[d*items : (d+1)*items]
                total_h = 0
                
                if not day_places:
                    pdf.set_font('Arial', 'I', 11)
                    pdf.cell(0, 8, "  Día libre", ln=True)
                
                for p in day_places:
                    total_h += p['hours']
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(5, 5, chr(149), ln=0)
                    pdf.cell(0, 5, p['name'], ln=True)
                    
                    pdf.set_font('Arial', '', 10)
                    pdf.set_x(15)
                    pdf.cell(0, 5, p['location'], ln=True)
                    pdf.set_x(15)
                    pdf.cell(0, 5, f"Tiempo: {p['time_str']}", ln=True)
                    pdf.ln(2)
                
                if day_places:
                    pdf.ln(2)
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 5, f"Total estimado: {total_h} horas", ln=True)
                pdf.ln(8)
            return pdf.output(dest='S').encode('latin-1', 'replace')

        st.markdown("---")
        pdf_data = generate_pdf(my_places, days)
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Itinerario_Arica.pdf" style="background-color:#0d8ca1; color:white; padding:10px 20px; border-radius:5px; text-decoration:none;">📥 Descargar PDF</a>', unsafe_allow_html=True)
