import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import tempfile
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Descubre Arica y Parinacota", page_icon="🧭")

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    :root { --primary-color: #008CBA; --bg-color: #0e1117; --text-color: #fafafa; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Títulos generales */
    h1, h2, h3 { color: #008CBA !important; }
    
    /* Botones */
    div.stButton > button { background-color: #008CBA; color: white; border-radius: 8px; border: none; font-weight: bold; }
    div.stButton > button:hover { background-color: #005f7f; transform: scale(1.02); }
    
    /* Tarjetas (Cards) - Fondo Azul y Letras Blancas */
    .card { 
        background-color: #008CBA; 
        color: white !important; 
        padding: 20px; 
        border-radius: 10px; 
        border: none; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        margin-bottom: 20px; 
    }
    .card h1, .card h2, .card h3, .card p, .card span { color: white !important; }
    
    .hero-text { font-size: 3rem; font-weight: bold; text-align: center; margin-bottom: 1rem; background: -webkit-linear-gradient(white, #aaaaaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    /* --- BARRA DE NAVEGACIÓN (NAVBAR) CORREGIDA --- */
    /* El contenedor principal (la caja) ahora es AZUL */
    div.stRadio > div[role="radiogroup"] { 
        justify-content: center; 
        background-color: #008CBA !important; /* FONDO AZUL */
        padding: 10px; 
        border-radius: 15px; 
        border: 2px solid #005f7f; 
        margin-bottom: 25px; 
    }
    
    /* El texto de las opciones (Inicio, Explorar...) ahora es BLANCO y NEGRITA */
    div.stRadio > div[role="radiogroup"] label { 
        color: white !important; /* LETRA BLANCA */
        font-weight: bold !important; /* LETRA NEGRITA */
        font-size: 1.1rem !important;
    }
    
    /* Asegurar que los párrafos internos también sean blancos */
    div.stRadio > div[role="radiogroup"] label p {
        color: white !important;
        font-weight: bold !important;
    }

    /* Efecto al pasar el mouse (hover) */
    div.stRadio > div[role="radiogroup"] > label:hover { 
        background-color: rgba(255,255,255,0.2) !important; 
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. DATOS DE LOS ATRACTIVOS ---
data_turismo = [
    {"id": 1, "nombre": "Morro de Arica", "categoria": "Histórico", "img": "https://www.elmorrocotudo.cl/sites/elmorrocotudo.cl/files/imagen_noticia/morro-de-arica-1.jpg", "desc": "Icono de la ciudad.", "ubicacion": "Centro de Arica", "duracion": 2},
    {"id": 2, "nombre": "Lago Chungará", "categoria": "Naturaleza", "img": "https://media.istockphoto.com/id/1210936595/es/foto/alpacas-graze-in-lauca-national-park-near-putre-chile.jpg?s=612x612&w=0&k=20&c=0BcUvoFlyaXc40jTaAm_hmmcpPTFteKLoCDhwXrJaWE=", "desc": "Lago de altura.", "ubicacion": "Altiplano, Parque Lauca", "duracion": 8},
    {"id": 3, "nombre": "Cuevas de Anzota", "categoria": "Aventura", "img": "https://www.costachinchorro.cl/ccc23/wp-content/uploads/2019/01/DSCF6574-e1548174607840-1200x600.jpg", "desc": "Formaciones geológicas.", "ubicacion": "Sector sur, a 12 km", "duracion": 3},
    {"id": 4, "nombre": "Pueblo de Putre", "categoria": "Cultural", "img": "https://laravel-production-storage1-oddrmnfoicay.s3.amazonaws.com/actividades/Putre%20%282%29.jpg", "desc": "Capital de Parinacota.", "ubicacion": "Precordillera", "duracion": 4},
    {"id": 5, "nombre": "Museo Arqueológico", "categoria": "Cultural", "img": "https://www.registromuseoschile.cl/663/articles-50828_imagen_portada.thumb_i_portada.jpg", "desc": "Momias Chinchorro.", "ubicacion": "Valle de Azapa", "duracion": 3},
    {"id": 6, "nombre": "Catedral San Marcos", "categoria": "Histórico", "img": "https://www.monumentos.gob.cl/sites/default/files/image-monumentos/00381_mh_15101-24.jpg", "desc": "Obra de Eiffel.", "ubicacion": "Plaza Colón", "duracion": 1},
    {"id": 7, "nombre": "Humedal Río Lluta", "categoria": "Naturaleza", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQAvTXRKiBi3FRCJgeetShO2TuwcY5CIq4zfg&s", "desc": "Santuario de aves.", "ubicacion": "Desembocadura", "duracion": 2},
    {"id": 8, "nombre": "Parque Nacional Lauca", "categoria": "Naturaleza", "img": "https://www.conaf.cl/wp-content/uploads/2024/01/Lago-Chungara-PArque-Nacional-Lauca-sernatur-ATR22-1.jpg", "desc": "Volcanes y fauna.", "ubicacion": "Altiplano", "duracion": 9},
    {"id": 9, "nombre": "Playa Chinchorro", "categoria": "Playa", "img": "https://www.aricaldia.cl/wp-content/uploads/2020/01/playa_chinchorro.jpg", "desc": "Aguas cálidas.", "ubicacion": "Zona Norte", "duracion": 3},
    {"id": 10, "nombre": "Playa El Laucho", "categoria": "Playa", "img": "https://www.revistagente.com/wp-content/uploads/2023/12/playa-el-laucho.jpeg.webp", "desc": "Oleaje suave.", "ubicacion": "Av. San Martín", "duracion": 3},
    {"id": 11, "nombre": "Presencias Tutelares", "categoria": "Cultural", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZNJLnQYD5CQe9PlS16g1dxgcjlOSj_6jj5A&s", "desc": "Esculturas gigantes.", "ubicacion": "Pampa de Chaca", "duracion": 1},
    {"id": 12, "nombre": "Playa La Lisera", "categoria": "Playa", "img": "https://aricasiempreactiva.cl/wp-content/uploads/elementor/thumbs/Playa-La-Lisera-Arica-Vista-Panoramica-1900x785-1-p46ftwempmah0fol2yf2f2g1pnxq4tium3jzc7g80w.jpg", "desc": "Familiar.", "ubicacion": "Sur de Arica", "duracion": 3},
    {"id": 13, "nombre": "Termas de Jurasi", "categoria": "Relax", "img": "https://chileestuyo.cl/wp-content/uploads/2015/07/termas-de-jurasi.jpg", "desc": "Aguas termales.", "ubicacion": "Cerca de Putre", "duracion": 3},
]

if 'seleccionados' not in st.session_state: st.session_state.seleccionados = []
if 'generado' not in st.session_state: st.session_state.generado = False

# --- 4. FUNCIÓN GENERADORA DE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.cell(0, 10, 'Itinerario Arica y Parinacota', 0, 1, 'C')
        self.ln(5)

def generar_pdf_estilo_tarjeta(itinerario_dias):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    headers = {'User-Agent': 'Mozilla/5.0'}

    for dia, items in itinerario_dias.items():
        pdf.set_fill_color(240, 240, 240) 
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"  Día {dia}", ln=1, fill=True)
        pdf.ln(4)

        for item in items:
            y_inicio = pdf.get_y()
            imagen_insertada = False
            try:
                response = requests.get(item['img'], headers=headers, stream=True, timeout=5)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        for chunk in response.iter_content(1024):
                            tmp_file.write(chunk)
                        tmp_img_path = tmp_file.name
                    try:
                        pdf.image(tmp_img_path, x=10, y=y_inicio, w=40, h=30)
                        imagen_insertada = True
                    except: pass
                    try: os.unlink(tmp_img_path)
                    except: pass
            except: pass

            if not imagen_insertada:
                pdf.set_fill_color(220, 220, 220)
                pdf.rect(10, y_inicio, 40, 30, 'F')
                pdf.set_xy(10, y_inicio + 12)
                pdf.set_font("Arial", "I", 8)
                pdf.cell(40, 5, "Sin Foto", align='C')

            pdf.set_xy(55, y_inicio)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, item['nombre'], ln=2)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 5, item['ubicacion'], ln=2)
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 5, f"Duración: {item['duracion']} horas", ln=2)
            pdf.set_text_color(0, 0, 0)
            pdf.set_y(y_inicio + 35)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFAZ ---
col_logo, col_nav = st.columns([1, 3])
with col_logo: st.markdown("### 🧭 Descubre Arica")
with col_nav:
    opcion = st.radio("Navegación", ["🏠 Inicio", "🗺️ Explorar Atractivos", "📅 Planificador Inteligente"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

if "Inicio" in opcion:
    st.markdown('<h1 class="hero-text">Descubre la magia del norte de Chile</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ccc;'>Playas infinitas, valles fértiles, altiplano andino y cultura milenaria.</h3>", unsafe_allow_html=True)
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0;">☁️ Clima Actual</h3>
            <h1 style="font-size:3rem; margin:0;">22°C</h1>
            <p>Soleado | Humedad 65%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0;">💲 Conversor</h3>
            <p style="font-size:1.2rem;">1000 CLP = 1.07 USD</p>
            <p style="font-size:0.9rem; opacity:0.8;">Dólar obs: $940</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.image("https://www.elmorrocotudo.cl/sites/elmorrocotudo.cl/files/imagen_noticia/morro-de-arica-1.jpg", use_container_width=True)
    st.info("💡 Tip: Ve a 'Explorar Atractivos' para comenzar.")

elif "Explorar" in opcion:
    col_title, col_count = st.columns([3, 1])
    with col_title: st.title("🗺️ Atractivos Turísticos")
    with col_count: st.metric(label="Seleccionados", value=len(st.session_state.seleccionados))
    
    filtro = st.selectbox("Filtrar por categoría:", ["Todos"] + sorted(list(set([x['categoria'] for x in data_turismo]))))
    items_mostrar = data_turismo if filtro == "Todos" else [x for x in data_turismo if x['categoria'] == filtro]
    
    cols = st.columns(3)
    for i, item in enumerate(items_mostrar):
        with cols[i % 3]:
            with st.container(border=True):
                st.image(item['img'], use_container_width=True)
                st.subheader(item['nombre'])
                st.caption(f"📍 {item['ubicacion']}") 
                st.write(f"_{item['desc']}_")
                
                is_selected = item['id'] in st.session_state.seleccionados
                if st.checkbox(f"Visitar {item['nombre']}", value=is_selected, key=f"chk_{item['id']}"):
                    if item['id'] not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(item['id'])
                        st.rerun()
                else:
                    if item['id'] in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(item['id'])
                        st.rerun()

elif "Planificador" in opcion:
    st.title("📅 Planificador Inteligente")
    if not st.session_state.seleccionados:
        st.warning("⚠️ Primero selecciona atractivos en la pestaña Explorar.")
        st.stop()

    col_config, col_resumen = st.columns([1, 2])
    with col_config:
        st.markdown("""<div class="card">""", unsafe_allow_html=True)
        st.subheader("⚙️ Configuración")
        dias = st.number_input("¿Días de visita?", min_value=1, max_value=7, value=3)
        st.write(f"**Lugares ({len(st.session
