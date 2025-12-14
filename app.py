import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import tempfile
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="Descubre Arica y Parinacota", page_icon="🧭")

# --- 2. ESTILOS CSS (DISEÑO WEB) ---
st.markdown("""
<style>
    /* Estilos generales modo oscuro/cian */
    :root {
        --primary-color: #008CBA;
        --bg-color: #0e1117;
        --text-color: #fafafa;
    }
    h1, h2, h3 { color: #008CBA !important; }
    div.stButton > button {
        background-color: #008CBA;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #005f7f;
        color: white;
    }
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
</style>
""", unsafe_allow_html=True)

# --- 3. DATOS DE LOS ATRACTIVOS ---
# Nota: He añadido el campo 'ubicacion' que faltaba para que coincida con tu PDF
data_turismo = [
    {"id": 1, "nombre": "Morro de Arica", "categoria": "Cultural", "duracion": 2, "ubicacion": "Centro de Arica", "img": "https://placehold.co/400x300/png?text=Morro+de+Arica"},
    {"id": 2, "nombre": "Lago Chungará", "categoria": "Naturaleza", "duracion": 8, "ubicacion": "Altiplano, Parque Lauca", "img": "https://placehold.co/400x300/png?text=Lago+Chungara"},
    {"id": 3, "nombre": "Cuevas de Anzota", "categoria": "Naturaleza", "duracion": 3, "ubicacion": "Sector Sur, a 12km", "img": "https://placehold.co/400x300/png?text=Cuevas+Anzota"},
    {"id": 4, "nombre": "Putre", "categoria": "Cultural", "duracion": 5, "ubicacion": "Precordillera", "img": "https://placehold.co/400x300/png?text=Putre"},
    {"id": 5, "nombre": "Museo Arqueológico Azapa", "categoria": "Arqueológico", "duracion": 3, "ubicacion": "Valle de Azapa, km 12", "img": "https://placehold.co/400x300/png?text=Museo+Azapa"},
    {"id": 6, "nombre": "Catedral San Marcos", "categoria": "Cultural", "duracion": 1, "ubicacion": "Plaza Colón, Centro", "img": "https://placehold.co/400x300/png?text=Catedral+San+Marcos"},
    {"id": 7, "nombre": "Humedal Río Lluta", "categoria": "Naturaleza", "duracion": 2, "ubicacion": "Desembocadura Río Lluta", "img": "https://placehold.co/400x300/png?text=Humedal+Lluta"},
    {"id": 8, "nombre": "Parque Nacional Lauca", "categoria": "Naturaleza", "duracion": 8, "ubicacion": "Altiplano Andino", "img": "https://placehold.co/400x300/png?text=PN+Lauca"},
    {"id": 9, "nombre": "Playa Chinchorro", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Norte", "img": "https://placehold.co/400x300/png?text=Playa+Chinchorro"},
    {"id": 10, "nombre": "Playa El Laucho", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Sur", "img": "https://placehold.co/400x300/png?text=Playa+El+Laucho"},
    {"id": 11, "nombre": "Presencias Tutelares", "categoria": "Arqueológico", "duracion": 2, "ubicacion": "Pampa de Acha", "img": "https://placehold.co/400x300/png?text=Presencias+Tutelares"},
    {"id": 12, "nombre": "Playa La Lisera", "categoria": "Playa", "duracion": 3, "ubicacion": "Arica Sur", "img": "https://placehold.co/400x300/png?text=Playa+La+Lisera"},
    {"id": 13, "nombre": "Termas de Jurasi", "categoria": "Naturaleza", "duracion": 4, "ubicacion": "Cercano a Putre", "img": "https://placehold.co/400x300/png?text=Termas+Jurasi"},
]

# Inicializar estado
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- 4. FUNCIÓN GENERADORA DE PDF MEJORADA ---
class PDF(FPDF):
    def header(self):
        # Título del documento centrado
        self.set_font('Arial', 'B', 18)
        self.cell(0, 10, 'Itinerario Arica y Parinacota', 0, 1, 'C')
        self.ln(5)

def generar_pdf_estilo_tarjeta(itinerario_dias):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for dia, items in itinerario_dias.items():
        # --- ENCABEZADO DEL DÍA (Barra gris) ---
        pdf.set_fill_color(240, 240, 240) # Gris claro
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"  Día {dia}", ln=1, fill=True)
        pdf.ln(4) # Pequeño espacio tras el título del día

        for item in items:
            # Posición Y actual para alinear imagen y texto
            y_inicio = pdf.get_y()
            
            # --- 1. IMAGEN (Izquierda) ---
            # Descargamos la imagen temporalmente
            try:
                response = requests.get(item['img'], stream=True)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                        for chunk in response.iter_content(1024):
                            tmp_file.write(chunk)
                        tmp_img_path = tmp_file.name
                    
                    # Insertamos imagen: x=10 (margen izq), w=40 (ancho), h=30 (alto)
                    pdf.image(tmp_img_path, x=10, y=y_inicio, w=40, h=30)
                    os.unlink(tmp_img_path)
                else:
                    # Si falla, dibujamos un recuadro vacío
                    pdf.rect(10, y_inicio, 40, 30)
                    pdf.set_xy(15, y_inicio + 10)
                    pdf.set_font("Arial", "I", 8)
                    pdf.cell(30, 10, "Sin Imagen")
            except:
                # Si hay error de red, recuadro vacío
                pdf.rect(10, y_inicio, 40, 30)

            # --- 2. TEXTO (Derecha) ---
            # Movemos el cursor a la derecha de la imagen (x=55)
            pdf.set_xy(55, y_inicio)
            
            # Título del atractivo
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 6, item['nombre'], ln=2)
            
            # Ubicación
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(80, 80, 80) # Gris oscuro para detalles
            pdf.cell(0, 5, item['ubicacion'], ln=2)
            
            # Duración con icono simulado (texto)
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 5, f"Duración: {item['duracion']} horas", ln=2)
            
            # Resetear color a negro
            pdf.set_text_color(0, 0, 0)

            # Mover cursor hacia abajo para el siguiente item
            # La altura debe ser al menos la altura de la imagen (30) + un margen (5)
            pdf.set_y(y_inicio + 35)
        
        pdf.ln(5) # Espacio extra entre días

    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFAZ Y NAVEGACIÓN ---
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Inicio", "Explorar Atractivos", "Planificador Inteligente"])
st.sidebar.markdown("---")
st.sidebar.info(f"📍 Seleccionados: **{len(st.session_state.seleccionados)}**")

if opcion == "Inicio":
    st.markdown('<h1 class="hero-text">Descubre la magia del norte de Chile</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Playas infinitas, valles fértiles, altiplano andino y milenaria cultura.</h3>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>☁️ Clima Actual - Arica</h3>
            <h1 style="color:white !important;">22°C</h1>
            <p>Soleado - Humedad 65%</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3>💲 Conversor de Divisas</h3>
            <p><b>1000 CLP</b> = 1.10 USD</p>
            <p>Dolar observado: $940 CLP</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.image("https://placehold.co/1200x400/005f7f/ffffff?text=Paisaje+Arica", use_container_width=True)

elif opcion == "Explorar Atractivos":
    st.title("🗺️ Atractivos Turísticos")
    st.write("Selecciona tus destinos favoritos para armar tu itinerario.")
    
    categorias = ["Todos"] + sorted(list(set([x['categoria'] for x in data_turismo])))
    filtro = st.selectbox("Filtrar por categoría:", categorias)
    items_mostrar = data_turismo if filtro == "Todos" else [x for x in data_turismo if x['categoria'] == filtro]
    
    cols = st.columns(3)
    for i, item in enumerate(items_mostrar):
        with cols[i % 3]:
            with st.container(border=True):
                st.image(item['img'], use_container_width=True)
                st.subheader(item['nombre'])
                st.caption(f"📍 {item['ubicacion']}") 
                is_selected = item['id'] in st.session_state.seleccionados
                if st.checkbox(f"Seleccionar", value=is_selected, key=f"chk_{item['id']}"):
                    if item['id'] not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(item['id'])
                else:
                    if item['id'] in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(item['id'])

elif opcion == "Planificador Inteligente":
    st.title("📅 Planifica tu viaje")
    
    col_config, col_resumen = st.columns([1, 2])
    with col_config:
        st.markdown("### Configuración")
        dias = st.number_input("¿Cuántos días estarás de visita?", min_value=1, max_value=7, value=3)
        st.markdown("### Tus Selecciones")
        if not st.session_state.seleccionados:
            st.warning("No has seleccionado atractivos. Ve a 'Explorar'.")
        else:
            sel_items = [d for d in data_turismo if d['id'] in st.session_state.seleccionados]
            for item in sel_items:
                st.write(f"• {item['nombre']}")
            if st.button("✨ Generar Itinerario", use_container_width=True):
                st.session_state.generado = True

    with col_resumen:
        if st.session_state.get('generado') and st.session_state.seleccionados:
            st.markdown("## 📋 Tu Itinerario Sugerido")
            
            # Lógica simple de distribución
            items_obj = [d for d in data_turismo if d['id'] in st.session_state.seleccionados]
            import math
            items_por_dia = math.ceil(len(items_obj) / dias)
            
            itinerario_final = {}
            idx_item = 0
            
            for dia in range(1, dias + 1):
                itinerario_final[dia] = []
                st.subheader(f"Día {dia}")
                for _ in range(items_por_dia):
                    if idx_item < len(items_obj):
                        act = items_obj[idx_item]
                        itinerario_final[dia].append(act)
                        
                        # Renderizado en pantalla (diseño similar al PDF)
                        c1, c2 = st.columns([1, 4])
                        c1.image(act['img'], use_container_width=True)
                        c2.write(f"**{act['nombre']}**")
                        c2.caption(f"📍 {act['ubicacion']} | ⏱️ {act['duracion']}h")
                        idx_item += 1
                st.divider()

            # Generar el PDF con el nuevo diseño
            pdf_bytes = generar_pdf_estilo_tarjeta(itinerario_final)
            
            st.download_button(
                label="📥 Descargar PDF (Diseño Tarjeta)",
                data=pdf_bytes,
                file_name="Itinerario_Arica.pdf",
                mime="application/pdf",
                use_container_width=True
            )
