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
    /* Ajustes para modo oscuro/claro */
    .main { background-color: #0e1117; color: white; }
    h1, h2, h3, p, div { color: white; }
    
    /* Hero Section con imagen de fondo */
    .hero {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), url('https://images.unsplash.com/photo-1599933256241-7e8c33959957?w=1200&q=80');
        background-size: cover;
        background-position: center;
        padding: 60px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #333;
    }
    
    /* Estilo de los Botones */
    div.stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 5px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #007399;
        border-color: #007399;
        color: white;
    }
    
    /* Ajuste de imágenes en tarjetas */
    img {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATOS ---
if 'places' not in st.session_state:
    st.session_state.places = [
        {
            "id": 1, "name": "Morro de Arica", "cat": "HISTÓRICO", 
            "img": "https://images.unsplash.com/photo-1599933256241-7e8c33959957?w=800&q=80", 
            "desc": "El guardián de la ciudad. Ofrece una vista panorámica inigualable del océano y el puerto.", 
            "price": "Gratis", "ideal": "Familia, Historia", "lat": -18.4811, "lon": -70.3253
        },
        {
            "id": 2, "name": "Lago Chungará", "cat": "NATURALEZA", 
            "img": "https://images.unsplash.com/photo-1518182170546-0766ce6fec9d?w=800&q=80", 
            "desc": "Uno de los lagos más altos del mundo a 4.500 msnm. Rodeado de volcanes.", 
            "price": "Gratis", "ideal": "Aventura, Trekking", "lat": -18.2497, "lon": -69.1750
        },
        {
            "id": 3, "name": "Cuevas de Anzota", "cat": "AVENTURA", 
            "img": "https://images.unsplash.com/photo-1534067783865-24b5d7d3d0f9?w=800&q=80", 
            "desc": "Impresionantes formaciones geológicas con senderos frente al mar.", 
            "price": "Gratis", "ideal": "Caminata, Geología", "lat": -18.5539, "lon": -70.3344
        },
        {
            "id": 4, "name": "Pueblo de Putre", "cat": "CULTURAL", 
            "img": "https://images.unsplash.com/photo-1544254471-294747d51939?w=800&q=80", 
            "desc": "Capital de la provincia de Parinacota. Pueblo histórico colonial.", 
            "price": "Gratis", "ideal": "Cultura, Aclimatación", "lat": -18.1950, "lon": -69.5597
        },
        {
            "id": 5, "name": "Museo Arqueológico", "cat": "CULTURAL", 
            "img": "https://images.unsplash.com/photo-1566417728795-0728c3104629?w=800&q=80", 
            "desc": "Hogar de la cultura Chinchorro y sus momias artificiales.", 
            "price": "$3.000 CLP", "ideal": "Cultura, Historia", "lat": -18.5186, "lon": -70.1837
        },
        {
            "id": 6, "name": "Catedral San Marcos", "cat": "HISTÓRICO", 
            "img": "https://images.unsplash.com/photo-1596483957297-c6b653457a4e?w=800&q=80", 
            "desc": "Obra de Eiffel. Monumento Nacional frente a la plaza.", 
            "price": "Gratis", "ideal": "Fotografía, Religión", "lat": -18.4779, "lon": -70.3207
        },
        {
            "id": 7, "name": "Humedal Río Lluta", "cat": "NATURALEZA", 
            "img": "https://images.unsplash.com/photo-1596483957297-c6b653457a4e?w=800&q=80", 
            "desc": "Santuario de la naturaleza. Avistamiento de aves migratorias.", 
            "price": "Gratis", "ideal": "Aves, Naturaleza", "lat": -18.4167, "lon": -70.3242
        },
        {
            "id": 8, "name": "Parque Nacional Lauca", "cat": "NATURALEZA", 
            "img": "https://images.unsplash.com/photo-1465220183275-1faa863377e3?w=800&q=80", 
            "desc": "Reserva mundial de la biosfera. Volcanes nevados y vicuñas.", 
            "price": "Gratis", "ideal": "Fotografía, Relax", "lat": -18.1833, "lon": -69.2667
        },
        {
            "id": 9, "name": "Playa Chinchorro", "cat": "PLAYA", 
            "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", 
            "desc": "Extensa playa de aguas cálidas, ideal para bañarse.", 
            "price": "Gratis", "ideal": "Familia, Playa", "lat": -18.4556, "lon": -70.2980
        },
        {
            "id": 10, "name": "Playa El Laucho", "cat": "PLAYA", 
            "img": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80", 
            "desc": "Playa balneario protegida del viento, bares de playa.", 
            "price": "Gratis", "ideal": "Fiesta, Relax", "lat": -18.4880, "lon": -70.3250
        },
        {
            "id": 11, "name": "Presencias Tutelares", "cat": "CULTURAL", 
            "img": "https://images.unsplash.com/photo-1623525283464-328639556394?w=800&q=80", 
            "desc": "Esculturas monumentales en medio del desierto.", 
            "price": "Gratis", "ideal": "Arte, Astronomía", "lat": -18.5750, "lon": -70.2217
        },
        {
            "id": 12, "name": "Playa La Lisera", "cat": "PLAYA", 
            "img": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=800&q=80", 
            "desc": "Balneario de forma circular con aguas tranquilas.", 
            "price": "Gratis", "ideal": "Niños, Familia", "lat": -18.4933, "lon": -70.3238
        },
        {
            "id": 13, "name": "Termas de Jurasi", "cat": "RELAX", 
            "img": "https://images.unsplash.com/photo-1572506893693-e380f9cb650a?w=800&q=80", 
            "desc": "Aguas termales de origen volcánico.", 
            "price": "$2.000", "ideal": "Salud, Relax", "lat": -18.2081, "lon": -69.5694
        },
    ]

if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'page' not in st.session_state: st.session_state.page = 'Inicio'

# --- 4. FUNCIONES ---
def toggle_favorite(place_id):
    if place_id in st.session_state.favorites:
        st.session_state.favorites.remove(place_id)
    else:
        st.session_state.favorites.append(place_id)

@st.dialog("Detalles del Atractivo")
def mostrar_detalle(place):
    st.image(place['img'], use_container_width=True)
    st.header(place['name'])
    st.caption(f"📍 {place['cat']}")
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"**Precio:** {place['price']}")
    with c2: st.markdown(f"**Ideal:** {place['ideal']}")
    st.write(place['desc'])
    st.divider()
    
    es_fav = place['id'] in st.session_state.favorites
    if st.button("❌ Quitar de Ruta" if es_fav else "❤️ Agregar a Ruta", key=f"mod_{place['id']}"):
        toggle_favorite(place['id'])
        st.rerun()

def descargar_imagen(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=4, verify=False)
        if response.status_code == 200:
            ext = mimetypes.guess_extension(response.headers.get('content-type')) or ".jpg"
            fd, path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(fd, 'wb') as tmp:
                for chunk in response.iter_content(1024): tmp.write(chunk)
            return path
    except: return None
    return None

# --- 5. NAVEGACIÓN ---
c1, c2 = st.columns([1, 4])
with c1: st.markdown("## 🦙 Arica")
with c2:
    b1, b2, b3 = st.columns(3)
    if b1.button("Inicio", use_container_width=True): st.session_state.page = 'Inicio'
    if b2.button("Explorar", use_container_width=True): st.session_state.page = 'Explorar'
    count = len(st.session_state.favorites)
    if b3.button(f"Mi Ruta ({count})", use_container_width=True): st.session_state.page = 'Planificador'

st.divider()

# --- 6. PÁGINAS ---

# === INICIO ===
if st.session_state.page == 'Inicio':
    st.markdown("""<div class="hero"><h1>Descubre Arica y Parinacota</h1><h3>Región de la Eterna Primavera</h3></div>""", unsafe_allow_html=True)

    # Clima y Divisa
    col_clima, col_divisa = st.columns(2)
    with col_clima:
        st.subheader("☀️ Clima")
        st.components.v1.html("""<a class="weatherwidget-io" href="https://forecast7.com/es/n18d48n70d31/arica/" data-label_1="ARICA" data-label_2="CLIMA" data-theme="pure" >ARICA CLIMA</a><script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src='https://weatherwidget.io/js/widget.min.js';fjs.parentNode.insertBefore(js,fjs);}}(document,'script','weatherwidget-io-js');</script>""", height=100)
    with col_divisa:
        st.subheader("💰 Conversor")
        val = st.number_input("CLP a USD", value=10000, step=1000)
        st.info(f"${val:,.0f} CLP = ${val/950:.2f} USD")

    st.markdown("### 🌟 Destacados de la Región")
    st.markdown("---")

    # AQUI ESTA LA MAGIA PARA QUE SE VEA COMO GRID (FOTO 2)
    # Usamos columnas de 4 en 4 para simular el Grid
    cols = st.columns(4) 
    
    # Mostramos los primeros 8 lugares
    for index, place in enumerate(st.session_state.places[:8]):
        with cols[index % 4]:
            # El contenedor le da el borde tipo tarjeta
            with st.container(border=True):
                st.image(place['img'], use_container_width=True)
                st.markdown(f"**{place['name']}**")
                st.caption(place['cat'])
                
                # El botón azul abajo de la foto
                if st.button("ℹ️ Ver Info", key=f"home_{place['id']}", use_container_width=True):
                    mostrar_detalle(place)

# === EXPLORAR ===
elif st.session_state.page == 'Explorar':
    st.title("🧭 Todos los Atractivos")
    filtro = st.text_input("🔍 Buscar...", "")
    
    # Grid de 3 columnas para explorar
    cols = st.columns(3)
    filtrados = [p for p in st.session_state.places if filtro.lower() in p['name'].lower()]
    
    for index, place in enumerate(filtrados):
        with cols[index % 3]:
            with st.container(border=True):
                st.image(place['img'], use_container_width=True)
                st.subheader(place['name'])
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("Info", key=f"ex_info_{place['id']}", use_container_width=True):
                        mostrar_detalle(place)
                with c_btn2:
                    fav = place['id'] in st.session_state.favorites
                    if st.button("✅" if fav else "➕", key=f"ex_add_{place['id']}", use_container_width=True):
                        toggle_favorite(place['id'])
                        st.rerun()

# === PLANIFICADOR ===
elif st.session_state.page == 'Planificador':
    st.title("🗺️ Tu Ruta")
    
    if not st.session_state.favorites:
        st.warning("No hay lugares seleccionados.")
    else:
        mis_lugares = [p for p in st.session_state.places if p['id'] in st.session_state.favorites]
        c_map, c_list = st.columns([2, 1])
        
        with c_list:
            st.write("Tus lugares:")
            for p in mis_lugares: st.write(f"- {p['name']}")
            dias = st.slider("Días", 1, 7, 3)
            
        with c_map:
            st.map(pd.DataFrame(mis_lugares), latitude='lat', longitude='lon')

        # PDF GENERATOR
        def generar_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Itinerario Arica", ln=True, align="C")
            pdf.ln(10)
            
            import math
            per_day = math.ceil(len(mis_lugares)/dias)
            
            for d in range(dias):
                pdf.set_fill_color(230,230,230)
                pdf.cell(0, 10, f"Dia {d+1}", ln=True, fill=True)
                pdf.ln(5)
                for p in mis_lugares[d*per_day : (d+1)*per_day]:
                    y = pdf.get_y()
                    path = descargar_imagen(p['img'])
                    if path: 
                        try: pdf.image(path, x=10, y=y, w=25, h=20)
                        except: pass
                    pdf.set_xy(40, y)
                    pdf.set_font("Arial","B",12)
                    pdf.cell(0,6, p['name'], ln=True)
                    pdf.set_x(40)
                    pdf.set_font("Arial","",10)
                    pdf.multi_cell(0,5, p['desc'])
                    pdf.ln(10)
            return pdf.output(dest='S').encode('latin-1', 'replace')

        if st.button("Descargar PDF"):
            b64 = base64.b64encode(generar_pdf()).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="ruta.pdf">Descargar</a>', unsafe_allow_html=True)
