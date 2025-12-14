import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import requests
import tempfile
import os

# 1. Configuración de la página
st.set_page_config(layout="wide", page_title="Descubre Arica", page_icon="🏔️")

# 2. Estilos CSS
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    
    /* Estilos Generales */
    .card { background-color: white; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #eee; }
    .hero { background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070'); background-size: cover; padding: 80px 40px; border-radius: 15px; color: white; margin-bottom: 30px; }
    .info-box { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; color: #333; }
    .info-box h5, .info-box p, .info-box div { color: #333 !important; }
    .price-text { font-size: 24px; font-weight: bold; color: #0d8ca1 !important; }
    
    /* Destacados con Fondo */
    .destacados-container {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Morro_de_arica_view.jpg/1280px-Morro_de_arica_view.jpg');
        background-size: cover; background-position: center; padding: 30px; border-radius: 15px; margin-top: 30px; color: white !important;
    }
    .custom-alert { background-color: rgba(255, 255, 255, 0.15); border-left: 5px solid #0d8ca1; padding: 15px; border-radius: 5px; margin-bottom: 25px; }
    .places-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
    .place-item { background-color: rgba(0,0,0,0.4); border-radius: 10px; overflow: hidden; text-align: center; padding-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
    .place-item img { width: 100%; height: 140px; object-fit: cover; border-bottom: 3px solid #0d8ca1; }
    .place-item-name { font-weight: bold; margin: 10px 0 5px 0; font-size: 15px; }
    .place-item-cat { font-size: 13px; color: #ddd; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# 3. Datos
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Histórico", "img": "https://www.elmorrocotudo.cl/sites/elmorrocotudo.cl/files/imagen_noticia/morro-de-arica-1.jpg", "desc": "Icono de la ciudad.", "location": "Centro de Arica", "time_str": "2 horas", "hours": 2, "lat": -18.4802, "lon": -70.3250},
        {"id": 2, "name": "Lago Chungará", "cat": "Naturaleza", "img": "https://media.istockphoto.com/id/1210936595/es/foto/alpacas-graze-in-lauca-national-park-near-putre-chile.jpg?s=612x612&w=0&k=20&c=0BcUvoFlyaXc40jTaAm_hmmcpPTFteKLoCDhwXrJaWE=", "desc": "Lago de altura.", "location": "Altiplano, Parque Lauca", "time_str": "Full Day", "hours": 8, "lat": -18.2500, "lon": -69.1667},
        {"id": 3, "name": "Cuevas de Anzota", "cat": "Aventura", "img": "https://www.costachinchorro.cl/ccc23/wp-content/uploads/2019/01/DSCF6574-e1548174607840-1200x600.jpg", "desc": "Formaciones geológicas.", "location": "Sector sur, a 12 km", "time_str": "3 horas", "hours": 3, "lat": -18.5500, "lon": -70.3300},
        {"id": 4, "name": "Pueblo de Putre", "cat": "Cultural", "img": "https://laravel-production-storage1-oddrmnfoicay.s3.amazonaws.com/actividades/Putre%20%282%29.jpg", "desc": "Capital de Parinacota.", "location": "Precordillera", "time_str": "4 horas", "hours": 4, "lat": -18.1950, "lon": -69.5600},
        {"id": 5, "name": "Museo Arqueológico", "cat": "Cultural", "https://www.registromuseoschile.cl/663/articles-50828_imagen_portada.thumb_i_portada.jpg", "desc": "Momias Chinchorro.", "location": "Valle de Azapa", "time_str": "3 horas", "hours": 3, "lat": -18.5150, "lon": -70.1800},
        {"id": 6, "name": "Catedral San Marcos", "cat": "Histórico", "https://www.monumentos.gob.cl/sites/default/files/image-monumentos/00381_mh_15101-24.jpg", "desc": "Obra de Eiffel.", "location": "Plaza Colón", "time_str": "1 hora", "hours": 1, "lat": -18.4779, "lon": -70.3207},
        {"id": 7, "name": "Humedal Río Lluta", "cat": "Naturaleza", "https://aricasiempreactiva.cl/wp-content/uploads/2021/06/Lagunas-II-Humedal-Rio-Lluta-Region-de-Arica-y-Parinacota.jpg", "desc": "Santuario de aves.", "location": "Desembocadura", "time_str": "2 horas", "hours": 2, "lat": -18.4167, "lon": -70.3167},
        {"id": 8, "name": "Parque Nacional Lauca", "cat": "Naturaleza", "https://www.conaf.cl/wp-content/uploads/2024/01/Lago-Chungara-PArque-Nacional-Lauca-sernatur-ATR22-1.jpg", "desc": "Volcanes y fauna.", "location": "Altiplano", "time_str": "Full Day", "hours": 9, "lat": -18.1833, "lon": -69.2333},
        {"id": 9, "name": "Playa Chinchorro", "cat": "Playa", "img": "https://www.aricaldia.cl/wp-content/uploads/2020/01/playa_chinchorro.jpg", "desc": "Aguas cálidas.", "location": "Zona Norte", "time_str": "3 horas", "hours": 3, "lat": -18.4550, "lon": -70.3000},
        {"id": 10, "name": "Playa El Laucho", "cat": "Playa", "https://aricasiempreactiva.cl/wp-content/uploads/2020/11/Playa-El-Laucho-Arica-Vista-Panoramica-1900x785-1.jpg", "desc": "Oleaje suave.", "location": "Av. San Martín", "time_str": "3 horas", "hours": 3, "lat": -18.4880, "lon": -70.3250},
        {"id": 11, "name": "Presencias Tutelares", "cat": "Cultural", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZNJLnQYD5CQe9PlS16g1dxgcjlOSj_6jj5A&s", "desc": "Esculturas gigantes.", "location": "Pampa de Chaca", "time_str": "1 hora", "hours": 1, "lat": -18.6667, "lon": -70.1833},
        {"id": 12, "name": "Playa La Lisera", "cat": "Playa", "img": "https://aricasiempreactiva.cl/wp-content/uploads/2020/11/Playa-La-Lisera-Arica-Vista-Panoramica-1900x785-1.jpg", "desc": "Familiar.", "location": "Sur de Arica", "time_str": "3 horas", "hours": 3, "lat": -18.4950, "lon": -70.3280},
        {"id": 13, "name": "Termas de Jurasi", "cat": "Relax", "img": "https://chileestuyo.cl/wp-content/uploads/2015/07/termas-de-jurasi.jpg", "desc": "Aguas termales.", "location": "Cerca de Putre", "time_str": "3 horas", "hours": 3, "lat": -18.2000, "lon": -69.5800},
    ]

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

# --- FUNCIONES DE AYUDA ---
def descargar_imagen(url):
    """Descarga imagen simulando ser un navegador y devuelve la ruta temporal"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, stream=True, timeout=3)
        if response.status_code == 200:
            # Crear archivo temporal
            fd, path = tempfile.mkstemp(suffix=".jpg")
            with os.fdopen(fd, 'wb') as tmp:
                for chunk in response.iter_content(1024):
                    tmp.write(chunk)
            return path
    except Exception as e:
        return None
    return None

# --- PÁGINAS ---
if st.session_state.page == 'Inicio':
    st.markdown("""<div class="hero"><h1>Descubre la magia del norte de Chile</h1><p>Playas infinitas, valles fértiles y cultura milenaria.</p></div>""", unsafe_allow_html=True)
    
    col_clima, col_divisas = st.columns(2)
    with col_clima:
        st.markdown("""
        <div class="info-box">
            <h5 style="margin-bottom:15px;">☁️ Clima Actual - Arica</h5>
            <div style="display: flex; align-items: center; justify-content: space-around;">
                <div style="font-size: 45px;">☀️</div>
                <div style="text-align: center;">
                    <div style="font-size: 16px;">Soleado</div>
                    <div style="font-size: 36px; font-weight: bold;">22°C</div>
                </div>
                <div style="font-size: 14px; color: #555; border-left: 2px solid #eee; padding-left: 15px;">
                    <div>💧 Humedad: 65%</div>
                    <div style="margin-top:5px;">🍃 Viento: 12 km/h</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_divisas:
        st.markdown('<div class="info-box"><h5 style="color:#333;">💲 Conversor</h5><span class="custom-label">Monto (CLP)</span>', unsafe_allow_html=True)
        amount = st.number_input("Monto", 1000, 1000000, 1000, label_visibility="collapsed")
        res_usd = amount / 935
        st.markdown(f"""<div style="margin-top: 10px; text-align: right;"><span style="color:#555; font-size:14px;">Son aprox:</span><br><span class="price-text">${res_usd:,.2f} USD</span></div></div>""", unsafe_allow_html=True)

    st.write("")
    
    # Destacados
    places_html = ""
    for place in st.session_state.places:
        places_html += f"""<div class="place-item"><img src="{place['img']}"><div class="place-item-name">{place['name']}</div><div class="place-item-cat">{place['cat']}</div></div>"""
    
    st.markdown(f"""
    <div class="destacados-container">
        <h3 style="color:white; margin-bottom: 20px;">🌟 Destacados de la Región</h3>
        <div class="custom-alert">💡 <strong>Tip:</strong> Ve a 'Explorar' para armar tu viaje.</div>
        <div class="places-grid">{places_html}</div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == 'Explorar':
    st.title("🧭 Selecciona tus Favoritos")
    search = st.text_input("🔍 Buscar lugar...", "")
    filtered = [p for p in st.session_state.places if search.lower() in p['name'].lower()]
    cols = st.columns(3)
    for i, place in enumerate(filtered):
        with cols[i % 3]:
            st.image(place['img'], use_container_width=True)
            st.markdown(f"**{place['name']}**")
            st.caption(f"{place['location']} | {place['time_str']}")
            st.checkbox("Añadir", value=place['id'] in st.session_state.favorites, key=f"chk_{place['id']}", on_change=toggle_favorite, args=(place['id'],))
            st.divider()

elif st.session_state.page == 'Planificador':
    st.title("📅 Planifica tu viaje")
    if not st.session_state.favorites:
        st.warning("Selecciona lugares en 'Explorar' primero.")
    else:
        my_places = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        days = st.number_input("Días de viaje", 1, 10, 3)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write(f"**{len(my_places)} lugares seleccionados:**")
            for p in my_places: st.write(f"• {p['name']}")
        with c2:
            st.map(pd.DataFrame(my_places), latitude='lat', longitude='lon', size=20, color='#0d8ca1')
            
        class PDF(FPDF):
            def header(self): pass

        def generate_pdf_ok(places, n_days):
            pdf = PDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Itinerario Arica y Parinacota', ln=True, align='C')
            pdf.ln(10)
            
            import math
            items = math.ceil(len(places) / n_days)
            
            for d in range(n_days):
                pdf.set_font('Arial', 'B', 14)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 10, f'  Día {d+1}', ln=True, fill=True)
                pdf.ln(5)
                
                day_places = places[d*items : (d+1)*items]
                if not day_places:
                    pdf.set_font('Arial', 'I', 11)
                    pdf.cell(0, 10, "  Día libre", ln=True)
                
                total_h = 0
                for p in day_places:
                    total_h += p['hours']
                    y_start = pdf.get_y()
                    
                    # 1. Intentar descargar y poner imagen
                    img_path = descargar_imagen(p['img'])
                    if img_path:
                        pdf.image(img_path, x=10, y=y_start, w=25, h=25)
                        try: os.unlink(img_path) # Borrar temporal
                        except: pass
                    else:
                        # Si falla, cuadro gris
                        pdf.set_fill_color(200, 200, 200)
                        pdf.rect(10, y_start, 25, 25, 'F')
                    
                    # 2. Texto
                    pdf.set_xy(40, y_start)
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 6, p['name'], ln=True)
                    pdf.set_x(40)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 5, p['location'], ln=True)
                    pdf.set_x(40)
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 5, f"Duración: {p['time_str']}", ln=True)
                    
                    # Espacio para el siguiente
                    next_y = max(pdf.get_y(), y_start + 30)
                    pdf.set_y(next_y)
                    pdf.set_draw_color(230,230,230)
                    pdf.line(10, next_y-2, 200, next_y-2)
                
                pdf.ln(5)

            return pdf.output(dest='S').encode('latin-1', 'replace')

        st.markdown("---")
        with st.spinner("Generando PDF con imágenes..."):
            pdf_bytes = generate_pdf_ok(my_places, days)
        
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Itinerario_Arica.pdf" style="background-color:#0d8ca1; color:white; padding:15px; border-radius:10px; text-decoration:none; font-weight:bold; display:block; text-align:center;">📥 Descargar PDF con Fotos</a>', unsafe_allow_html=True)
