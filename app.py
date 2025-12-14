import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

# 1. Configuración de la página
st.set_page_config(layout="wide", page_title="Descubre Arica", page_icon="🏔️")

# 2. Estilos CSS
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .card {
        background-color: white; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px; overflow: hidden; border: 1px solid #eee; transition: transform 0.2s;
    }
    .card:hover { transform: scale(1.02); }
    .hero {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070');
        background-size: cover; background-position: center; padding: 80px 40px; border-radius: 15px; color: white; margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Datos Actualizados (Con ubicaciones reales para el PDF)
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 2, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://cl.kvnoticias.com/wp-content/uploads/2023/07/Arica.jpg", "desc": "Aguas cálidas ideales para deportes acuáticos.", "location": "Arica, a 2 km del centro", "time_str": "3 horas", "hours": 3, "lat": -18.4550, "lon": -70.3000},
        {"id": 5, "name": "Catedral de San Marcos", "cat": "Cultural", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg/640px-Catedral_de_San_Marcos%2C_Arica%2C_Chile%2C_2024-05-18%2C_DD_16.jpg", "desc": "Obra de Gustave Eiffel.", "location": "Centro de Arica", "time_str": "1 hora", "hours": 1, "lat": -18.4779, "lon": -70.3207},
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://upload.wikimedia.org/wikipedia/commons/e/e5/Morro_de_arica_view.jpg", "desc": "Vista panorámica de la ciudad.", "location": "Centro de Arica", "time_str": "2 horas", "hours": 2, "lat": -18.4802, "lon": -70.3250},
        {"id": 3, "name": "Valle de Azapa", "cat": "Arqueológico", "img": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0d/16/61/8b/valle-de-azapa.jpg?w=1200&h=-1&s=1", "desc": "Museo arqueológico y aceitunas.", "location": "Valle de Azapa, a 12 km de Arica", "time_str": "4 horas", "hours": 4, "lat": -18.5100, "lon": -70.1800},
        {"id": 4, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "img": "https://www.chile.travel/wp-content/uploads/2021/07/lago-chungara-parque-nacional-lauca-1.jpg", "desc": "Lago Chungará y volcanes.", "location": "Altiplano, a 165 km de Arica", "time_str": "8 horas", "hours": 8, "lat": -18.2500, "lon": -69.2500},
        {"id": 6, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://chileestuyo.cl/wp-content/uploads/2021/07/cuevas-de-anzota-arica.jpg", "desc": "Formaciones geológicas.", "location": "Sector sur, a 12 km del centro", "time_str": "3 horas", "hours": 3, "lat": -18.5500, "lon": -70.3300},
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

# --- VISTAS ---
if st.session_state.page == 'Inicio':
    st.markdown("""<div class="hero"><h1>Descubre la magia del norte de Chile</h1></div>""", unsafe_allow_html=True)
    st.write("Selecciona 'Explorar' para comenzar tu viaje.")

elif st.session_state.page == 'Explorar':
    st.title("🧭 Atractivos Turísticos")
    cols = st.columns(3)
    for i, place in enumerate(st.session_state.places):
        with cols[i % 3]:
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(f"{place['location']}")
            st.checkbox("Seleccionar", value=place['id'] in st.session_state.favorites, key=f"chk_{place['id']}", on_change=toggle_favorite, args=(place['id'],))
            st.divider()

elif st.session_state.page == 'Planificador':
    st.title("📅 Planifica tu viaje")
    
    if not st.session_state.favorites:
        st.warning("Selecciona destinos primero.")
    else:
        my_places = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        days = st.number_input("Días de visita", 1, 7, 3)
        
        # Mapa
        st.map(pd.DataFrame(my_places), latitude='lat', longitude='lon', size=20, color='#0d8ca1')
        
        # --- GENERACIÓN DEL PDF MEJORADO ---
        class PDF(FPDF):
            def header(self):
                # No ponemos nada aquí para controlar el título manualmente
                pass

        def create_styled_pdf(places_list, num_days):
            pdf = PDF()
            pdf.add_page()
            
            # Título Centrado
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Itinerario de Viaje - Arica y Parinacota', ln=True, align='C')
            pdf.ln(10) # Espacio
            
            # Algoritmo de distribución
            import math
            items_per_day = math.ceil(len(places_list) / num_days)
            
            for d in range(num_days):
                day_num = d + 1
                
                # Encabezado del Día (Negrita, Grande)
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, f'Día {day_num}', ln=True)
                
                # Obtener lugares del día
                start = d * items_per_day
                end = start + items_per_day
                day_places = places_list[start:end]
                
                daily_total_hours = 0
                
                if not day_places:
                    pdf.set_font('Arial', 'I', 11)
                    pdf.cell(0, 8, "  Día libre para recorrer la ciudad.", ln=True)
                
                for p in day_places:
                    daily_total_hours += p['hours']
                    
                    # Nombre del lugar (Negrita) con viñeta
                    pdf.set_font('Arial', 'B', 11)
                    # Usamos chr(149) para la viñeta redonda
                    pdf.cell(5, 5, chr(149), ln=0) 
                    pdf.cell(0, 5, p['name'], ln=True)
                    
                    # Ubicación (Normal, indentado)
                    pdf.set_font('Arial', '', 10)
                    pdf.set_x(15) # Mover a la derecha
                    pdf.cell(0, 5, p['location'], ln=True)
                    
                    # Tiempo (Normal, indentado)
                    pdf.set_x(15)
                    pdf.cell(0, 5, f"Tiempo estimado: {p['time_str']}", ln=True)
                    
                    pdf.ln(2) # Pequeño espacio entre items
                
                # Total del día (Cursiva)
                if day_places:
                    pdf.ln(2)
                    pdf.set_font('Arial', 'I', 10)
                    pdf.cell(0, 5, f"Total: {daily_total_hours} horas", ln=True)
                
                pdf.ln(8) # Espacio grande entre días

            return pdf.output(dest='S').encode('latin-1', 'replace')

        st.markdown("---")
        st.subheader("Tu Itinerario")
        
        # Previsualización en pantalla simple
        for p in my_places:
            st.write(f"• {p['name']} ({p['time_str']})")

        # Generar y descargar PDF
        pdf_bytes = create_styled_pdf(my_places, days)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Itinerario_Arica_Oficial.pdf" style="background-color:#0d8ca1; color:white; padding:12px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Descargar PDF Oficial</a>'
        st.markdown(href, unsafe_allow_html=True)
