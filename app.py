import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import requests
import tempfile
import os
import mimetypes

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Arica Smart Tour", page_icon="🦙")

# --- 2. ESTILOS CSS (DISEÑO) ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #2c3e50; }
    
    /* Tarjetas */
    .place-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1599933256241-7e8c33959957?w=1200&q=80');
        background-size: cover;
        background-position: center;
        padding: 60px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Botones */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATOS (Lugares con fotos reales de Unsplash) ---
if 'places' not in st.session_state:
    st.session_state.places = [
        {"id": 1, "name": "Morro de Arica", "cat": "Ciudad", "img": "https://images.unsplash.com/photo-1599933256241-7e8c33959957?w=800&q=80", "desc": "Vista panorámica y museo histórico.", "lat": -18.4811, "lon": -70.3253},
        {"id": 2, "name": "Lago Chungará", "cat": "Altiplano", "img": "https://images.unsplash.com/photo-1518182170546-0766ce6fec9d?w=800&q=80", "desc": "Uno de los lagos más altos del mundo.", "lat": -18.2497, "lon": -69.1750},
        {"id": 3, "name": "Cuevas de Anzota", "cat": "Costa", "img": "https://images.unsplash.com/photo-1534067783865-24b5d7d3d0f9?w=800&q=80", "desc": "Senderos geológicos frente al mar.", "lat": -18.5539, "lon": -70.3344},
        {"id": 4, "name": "Pueblo de Putre", "cat": "Altiplano", "img": "https://images.unsplash.com/photo-1544254471-294747d51939?w=800&q=80", "desc": "Capital de la provincia de Parinacota.", "lat": -18.1950, "lon": -69.5597},
        {"id": 5, "name": "Museo Momias Chinchorro", "cat": "Valle", "img": "https://images.unsplash.com/photo-1566417728795-0728c3104629?w=800&q=80", "desc": "Las momias más antiguas del mundo.", "lat": -18.5186, "lon": -70.1837},
        {"id": 6, "name": "Parque Nacional Lauca", "cat": "Altiplano", "img": "https://images.unsplash.com/photo-1465220183275-1faa863377e3?w=800&q=80", "desc": "Reserva de la biosfera y volcanes.", "lat": -18.1833, "lon": -69.2667},
        {"id": 7, "name": "Playa Chinchorro", "cat": "Costa", "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", "desc": "Playa de aguas cálidas.", "lat": -18.4556, "lon": -70.2980},
        {"id": 8, "name": "Termas de Jurasi", "cat": "Altiplano", "img": "https://images.unsplash.com/photo-1572506893693-e380f9cb650a?w=800&q=80", "desc": "Pozas termales medicinales.", "lat": -18.2081, "lon": -69.5694},
        {"id": 9, "name": "Presencias Tutelares", "cat": "Pampa", "img": "https://images.unsplash.com/photo-1623525283464-328639556394?w=800&q=80", "desc": "Esculturas en el desierto.", "lat": -18.5750, "lon": -70.2217},
        {"id": 10, "name": "Humedal Río Lluta", "cat": "Costa", "img": "https://images.unsplash.com/photo-1596483957297-c6b653457a4e?w=800&q=80", "desc": "Santuario de aves migratorias.", "lat": -18.4167, "lon": -70.3242},
    ]

if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'page' not in st.session_state: st.session_state.page = 'Inicio'

# --- 4. FUNCIONES AUXILIARES ---
def toggle_favorite(place_id):
    if place_id in st.session_state.favorites:
        st.session_state.favorites.remove(place_id)
    else:
        st.session_state.favorites.append(place_id)

def descargar_imagen(url):
    """Descarga imagen de forma segura para el PDF"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True, timeout=4, verify=False)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            ext = mimetypes.guess_extension(content_type)
            if not ext: ext = ".jpg"
            
            fd, path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(fd, 'wb') as tmp:
                for chunk in response.iter_content(1024):
                    tmp.write(chunk)
            return path
    except:
        return None
    return None

# --- 5. NAVEGACIÓN ---
col_nav1, col_nav2 = st.columns([1, 4])
with col_nav1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Parinacota.jpg/640px-Parinacota.jpg", width=100) # Logo simple
with col_nav2:
    b1, b2, b3 = st.columns(3)
    if b1.button("🏠 Inicio", use_container_width=True): st.session_state.page = 'Inicio'
    if b2.button("📷 Explorar Lugares", use_container_width=True): st.session_state.page = 'Explorar'
    
    count = len(st.session_state.favorites)
    label_plan = f"🗺️ Mi Ruta ({count})" if count > 0 else "🗺️ Mi Ruta"
    if b3.button(label_plan, use_container_width=True): st.session_state.page = 'Planificador'

st.divider()

# --- 6. PÁGINAS ---

# === PÁGINA INICIO ===
if st.session_state.page == 'Inicio':
    st.markdown("""
    <div class="hero">
        <h1>Bienvenido a Arica y Parinacota</h1>
        <h3>La ciudad de la Eterna Primavera te espera</h3>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("☀️ Clima Hoy")
        # Widget de clima embebido
        st.components.v1.html("""
        <a class="weatherwidget-io" href="https://forecast7.com/es/n18d48n70d31/arica/" data-label_1="ARICA" data-label_2="CLIMA" data-theme="pure" >ARICA CLIMA</a>
        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');</script>
        """, height=150)
    
    with c2:
        st.subheader("💰 Conversor (Referencial)")
        monto = st.number_input("Pesos Chilenos (CLP)", min_value=0, value=10000, step=1000)
        usd = monto / 950
        st.success(f"🇺🇸 ${usd:,.2f} USD aprox.")

# === PÁGINA EXPLORAR ===
elif st.session_state.page == 'Explorar':
    st.title("Descubre los Atractivos")
    
    # Filtro
    filtro = st.text_input("🔍 Buscar lugar...", "")
    
    # Grid de tarjetas
    cols = st.columns(3)
    idx = 0
    for place in st.session_state.places:
        if filtro.lower() in place['name'].lower():
            with cols[idx % 3]:
                # Tarjeta visual
                st.image(place['img'], use_container_width=True)
                st.subheader(place['name'])
                st.caption(f"📍 {place['cat']}")
                st.write(place['desc'])
                
                # Botón de favorito
                es_fav = place['id'] in st.session_state.favorites
                label = "✅ En mi ruta" if es_fav else "⬜ Agregar a ruta"
                if st.button(label, key=f"btn_{place['id']}"):
                    toggle_favorite(place['id'])
                    st.rerun()
                st.markdown("---")
            idx += 1

# === PÁGINA PLANIFICADOR ===
elif st.session_state.page == 'Planificador':
    st.title("🗺️ Tu Itinerario Inteligente")
    
    if not st.session_state.favorites:
        st.warning("⚠️ Aún no has seleccionado lugares. Ve a la pestaña 'Explorar' y agrega algunos.")
        if st.button("Ir a Explorar"):
            st.session_state.page = 'Explorar'
            st.rerun()
    else:
        mis_lugares = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        
        col_map, col_datos = st.columns([2, 1])
        
        with col_datos:
            st.subheader("Tus Selecciones")
            for p in mis_lugares:
                st.write(f"✅ **{p['name']}**")
            
            dias = st.slider("¿Cuántos días vienes?", 1, 7, 3)
        
        with col_map:
            st.subheader("Mapa de Ruta")
            # Mapa simple usando lat/lon
            df_map = pd.DataFrame(mis_lugares)
            st.map(df_map, latitude='lat', longitude='lon', zoom=9)

        st.divider()
        
        # --- GENERACIÓN DE PDF ---
        st.subheader("📥 Descargar Itinerario")
        
        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 10, "Mi Viaje a Arica y Parinacota", ln=True, align="C")
            pdf.ln(10)
            
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Duración del viaje: {dias} días", ln=True)
            pdf.ln(5)
            
            # Repartir lugares por días (lógica simple)
            import math
            lugares_por_dia = math.ceil(len(mis_lugares) / dias)
            
            for dia in range(dias):
                pdf.set_fill_color(200, 220, 255)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, f"Día {dia + 1}", ln=True, fill=True)
                pdf.ln(5)
                
                # Obtener lugares para este día
                inicio = dia * lugares_por_dia
                fin = inicio + lugares_por_dia
                lugares_dia = mis_lugares[inicio:fin]
                
                for p in lugares_dia:
                    y_antes = pdf.get_y()
                    
                    # Intentar poner imagen
                    img_path = descargar_imagen(p['img'])
                    if img_path:
                        try:
                            pdf.image(img_path, x=10, y=y_antes, w=30, h=20)
                        except:
                            pass # Si falla la imagen, sigue sin ella
                        # Borrar temporal
                        try: os.unlink(img_path) 
                        except: pass
                    
                    # Texto
                    pdf.set_xy(45, y_antes)
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 6, p['name'], ln=True)
                    
                    pdf.set_xy(45, y_antes + 6)
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(0, 5, p['desc'])
                    
                    pdf.ln(15) # Espacio entre items
                    
            return pdf.output(dest='S').encode('latin-1', 'replace')

        if st.button("📄 Generar PDF con fotos"):
            with st.spinner("Creando tu guía personalizada..."):
                pdf_bytes = generar_pdf()
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="Guia_Arica.pdf" style="text-decoration:none; color:white; background-color:#ff4b4b; padding:10px 20px; border-radius:5px; font-weight:bold;">⬇️ Clic para descargar PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
