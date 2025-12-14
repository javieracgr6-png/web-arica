import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import tempfile
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Descubre Arica y Parinacota", page_icon="🧭")

# --- 2. ESTILOS CSS (DISEÑO WEB & NAVBAR) ---
st.markdown("""
<style>
    /* Estilos generales modo oscuro/cian */
    :root {
        --primary-color: #008CBA;
        --bg-color: #0e1117;
        --text-color: #fafafa;
    }
    
    /* Ocultar el menú hamburguesa y el footer de Streamlit para un look más "web" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Títulos */
    h1, h2, h3 { color: #008CBA !important; }
    
    /* Botones */
    div.stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #005f7f;
        transform: scale(1.02);
    }

    /* Tarjetas personalizadas */
    .card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    .hero-text {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: -webkit-linear-gradient(white, #aaaaaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* --- ESTILOS PARA LA BARRA DE NAVEGACIÓN SUPERIOR --- */
    /* Centrar los radio buttons horizontales */
    div.stRadio > div[role="radiogroup"] {
        justify-content: center;
        background-color: #262730;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #444;
        margin-bottom: 25px;
    }
    
    /* Estilo de cada "botón" del menú */
    div.stRadio > div[role="radiogroup"] > label {
        background-color: transparent;
        border: 1px solid transparent;
        padding: 5px 20px;
        border-radius: 10px;
        transition: all 0.3s;
    }
    
    /* Efecto Hover en el menú */
    div.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #333;
        border-color: #555;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. DATOS DE LOS ATRACTIVOS ---
data_turismo = [
    {"id": 1, "nombre": "Morro de Arica", "categoria": "Cultural", "duracion": 2, "ubicacion": "Centro de Arica", "img": "https://www.elmorrocotudo.cl/sites/elmorrocotudo.cl/files/imagen_noticia/morro-de-arica-1.jpg"},
    {"id": 2, "nombre": "Lago Chungará", "categoria": "Naturaleza", "duracion": 8, "ubicacion": "Altiplano, Parque Lauca", "img": "https://media.istockphoto.com/id/1210936595/es/foto/alpacas-graze-in-lauca-national-park-near-putre-chile.jpg?s=612x612&w=0&k=20&c=0BcUvoFlyaXc40jTaAm_hmmcpPTFteKLoCDhwXrJaWE="},
    {"id": 3, "nombre": "Cuevas de Anzota", "categoria": "Naturaleza", "duracion": 3, "ubicacion": "Sector Sur, a 12km", "img": "https://www.costachinchorro.cl/ccc23/wp-content/uploads/2019/01/DSCF6574-e1548174607840-1200x600.jpg"},
    {"id": 4, "nombre": "Putre", "categoria": "Cultural", "duracion": 5, "ubicacion": "Precordillera", "img": "https://laravel-production-storage1-oddrmnfoicay.s3.amazonaws.com/actividades/Putre%20%282%29.jpg"},
    {"id": 5, "nombre": "Museo Arqueológico Azapa", "categoria": "Arqueológico", "duracion": 3, "ubicacion": "Valle de Azapa, km 12", "img": "https://www.registromuseoschile.cl/663/articles-50828_imagen_portada.thumb_i_portada.jpg"},
    {"id": 6, "nombre": "Catedral San Marcos", "categoria": "Cultural", "duracion": 1, "ubicacion": "Plaza Colón, Centro", "img": "https://www.monumentos.gob.cl/sites/default/files/image-monumentos/00381_mh_15101-24.jpg"},
    {"id": 7, "nombre": "Humedal Río Lluta", "categoria": "Naturaleza", "duracion": 2, "ubicacion": "Desembocadura Río Lluta", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQAvTXRKiBi3FRCJgeetShO2TuwcY5CIq4zfg&s"},
    {"id": 8, "nombre": "Parque Nacional Lauca", "categoria": "Naturaleza", "duracion": 8, "ubicacion": "Altiplano Andino", "img": "https://www.conaf.cl/wp-content/uploads/2024/01/Lago-Chungara-PArque-Nacional-Lauca-sernatur-ATR22-1.jpg"},
    {"id": 9, "nombre": "Playa Chinchorro", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Norte", "img": "https://www.aricaldia.cl/wp-content/uploads/2020/01/playa_chinchorro.jpg"},
    {"id": 10, "nombre": "Playa El Laucho", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Sur", "img": "https://www.revistagente.com/wp-content/uploads/2023/12/playa-el-laucho.jpeg.webp"},
    {"id": 11, "nombre": "Presencias Tutelares", "categoria": "Arqueológico", "duracion": 2, "ubicacion": "Pampa de Acha", "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRZNJLnQYD5CQe9PlS16g1dxgcjlOSj_6jj5A&s"},
    {"id": 12, "nombre": "Playa La Lisera", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Sur", "img": "https://aricasiempreactiva.cl/wp-content/uploads/elementor/thumbs/Playa-La-Lisera-Arica-Vista-Panoramica-1900x785-1-p46ftwempmah0fol2yf2f2g1pnxq4tium3jzc7g80w.jpg"},
    {"id": 13, "nombre": "Termas de Jurasi", "categoria": "Naturaleza", "duracion": 4, "ubicacion": "Cercano a Putre", "img": "https://chileestuyo.cl/wp-content/uploads/2015/07/termas-de-jurasi.jpg"},
]

# Inicializar estado
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []
if 'generado' not in st.session_state:
    st.session_state.generado = False

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

    for dia, items in itinerario_dias.items():
        pdf.set_fill_color(240, 240, 240) 
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"  Día {dia}", ln=1, fill=True)
        pdf.ln(4)

        for item in items:
            y_inicio = pdf.get_y()
            try:
                response = requests.get(item['img'], stream=True)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                        for chunk in response.iter_content(1024):
                            tmp_file.write(chunk)
                        tmp_img_path = tmp_file.name
                    pdf.image(tmp_img_path, x=10, y=y_inicio, w=40, h=30)
                    os.unlink(tmp_img_path)
                else:
                    pdf.rect(10, y_inicio, 40, 30)
            except:
                pdf.rect(10, y_inicio, 40, 30)

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

# --- 5. ENCABEZADO Y NAVEGACIÓN SUPERIOR (NAVBAR) ---

# Título de la App arriba a la izquierda
col_logo, col_nav = st.columns([1, 3])
with col_logo:
    st.markdown("### 🧭 Descubre Arica")

# Menú de navegación Horizontal (Navbar)
with col_nav:
    # Usamos label_visibility="collapsed" para que no se vea el título "Navegación"
    opcion = st.radio(
        "Navegación", 
        ["🏠 Inicio", "🗺️ Explorar Atractivos", "📅 Planificador Inteligente"], 
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("---") # Línea separadora debajo del menú

# --- 6. LÓGICA DE LAS PÁGINAS ---

if "Inicio" in opcion:
    # --- PÁGINA DE INICIO ---
    st.markdown('<h1 class="hero-text">Descubre la magia del norte de Chile</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ccc;'>Playas infinitas, valles fértiles, altiplano andino y cultura milenaria.</h3>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0;">☁️ Clima Actual - Arica</h3>
            <h1 style="color:white !important; font-size: 3rem; margin: 10px 0;">22°C</h1>
            <p style="color:#aaa;">☀️ Soleado | 💧 Humedad 65%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="margin-top:0;">💲 Conversor (Ref.)</h3>
            <div style="background:#333; padding:10px; border-radius:5px; margin-top:10px;">
                <p style="margin:0; font-size:0.9rem; color:#aaa;">Monto a convertir</p>
                <p style="margin:0; font-size:1.5rem; font-weight:bold;">1000 CLP</p>
            </div>
            <p style="margin-top:10px; color:#008CBA; font-weight:bold;">= 1.07 USD</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Imagen destacada grande
    st.image("https://placehold.co/1200x500/005f7f/ffffff?text=Bienvenido+a+Arica", use_container_width=True)
    
    # Mensaje Tip (como en tu foto)
    st.info("💡 **Tip:** Ve a la pestaña **'Explorar Atractivos'** para seleccionar tus lugares favoritos y generar tu itinerario automático.")

elif "Explorar" in opcion:
    # --- PÁGINA EXPLORAR ---
    col_title, col_count = st.columns([3, 1])
    with col_title:
        st.title("🗺️ Atractivos Turísticos")
        st.write("Selecciona tus destinos favoritos haciendo clic en la casilla.")
    with col_count:
        st.metric(label="Seleccionados", value=len(st.session_state.seleccionados))

    
    categorias = ["Todos"] + sorted(list(set([x['categoria'] for x in data_turismo])))
    filtro = st.selectbox("Filtrar por categoría:", categorias)
    items_mostrar = data_turismo if filtro == "Todos" else [x for x in data_turismo if x['categoria'] == filtro]
    
    # Grid de 3 columnas
    cols = st.columns(3)
    for i, item in enumerate(items_mostrar):
        with cols[i % 3]:
            # Usamos st.container con borde para simular la tarjeta
            with st.container(border=True):
                st.image(item['img'], use_container_width=True)
                st.subheader(item['nombre'])
                st.caption(f"📍 {item['ubicacion']}") 
                
                # Checkbox con lógica de estado
                is_selected = item['id'] in st.session_state.seleccionados
                
                # Botón de selección más visible
                if st.checkbox(f"Visitar {item['nombre']}", value=is_selected, key=f"chk_{item['id']}"):
                    if item['id'] not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(item['id'])
                        st.rerun() # Recargar para actualizar contador
                else:
                    if item['id'] in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(item['id'])
                        st.rerun()

elif "Planificador" in opcion:
    # --- PÁGINA PLANIFICADOR ---
    st.title("📅 Planificador Inteligente")
    
    if not st.session_state.seleccionados:
        st.warning("⚠️ Aún no has seleccionado atractivos. Ve a la pestaña **Explorar Atractivos** y elige tus favoritos.")
        st.stop()

    col_config, col_resumen = st.columns([1, 2])
    with col_config:
        st.markdown("""<div class="card">""", unsafe_allow_html=True)
        st.subheader("⚙️ Configuración")
        dias = st.number_input("¿Días de visita?", min_value=1, max_value=7, value=3)
        
        st.write(f"**Lugares elegidos ({len(st.session_state.seleccionados)}):**")
        sel_items = [d for d in data_turismo if d['id'] in st.session_state.seleccionados]
        for item in sel_items:
            st.write(f"- {item['nombre']}")
            
        if st.button("✨ Generar Itinerario", use_container_width=True):
            st.session_state.generado = True
        st.markdown("</div>", unsafe_allow_html=True)

    with col_resumen:
        if st.session_state.get('generado'):
            st.markdown("## 📋 Tu Itinerario Sugerido")
            
            items_obj = [d for d in data_turismo if d['id'] in st.session_state.seleccionados]
            import math
            items_por_dia = math.ceil(len(items_obj) / dias)
            
            itinerario_final = {}
            idx_item = 0
            
            for dia in range(1, dias + 1):
                itinerario_final[dia] = []
                with st.expander(f"📅 Día {dia}", expanded=True):
                    for _ in range(items_por_dia):
                        if idx_item < len(items_obj):
                            act = items_obj[idx_item]
                            itinerario_final[dia].append(act)
                            
                            c1, c2 = st.columns([1, 4])
                            c1.image(act['img'], use_container_width=True)
                            c2.markdown(f"**{act['nombre']}**")
                            c2.caption(f"📍 {act['ubicacion']} | ⏱️ {act['duracion']}h")
                            idx_item += 1

            pdf_bytes = generar_pdf_estilo_tarjeta(itinerario_final)
            
            st.success("✅ ¡Itinerario listo para descargar!")
            st.download_button(
                label="📥 Descargar PDF (Diseño Tarjeta)",
                data=pdf_bytes,
                file_name="Itinerario_Arica.pdf",
                mime="application/pdf",
                use_container_width=True
            )
