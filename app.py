import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="Descubre Arica y Parinacota",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS Personalizado (Estilos)
# Esto es necesario para que se vea como la imagen (fondo oscuro, tarjetas, tipografía)
st.markdown("""
<style>
    /* Ajustes generales */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Estilo del Hero (La imagen grande con texto) */
    .hero-container {
        background-image: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.6)), url('https://images.unsplash.com/photo-1596483957297-c6b653457a4e?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        padding: 80px 40px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        font-family: sans-serif;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        margin-bottom: 2rem;
        max-width: 600px;
        line-height: 1.5;
    }
    
    /* Botón personalizado estilo Hero */
    .hero-btn {
        background-color: #0d8ca1;
        color: white;
        padding: 10px 25px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        transition: 0.3s;
    }
    .hero-btn:hover {
        background-color: #0a6c7c;
        color: white;
        text-decoration: none;
    }

    /* Estilo de las Tarjetas (Cards) inferiores */
    div.stContainer {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Texto de precio */
    .price-text {
        font-size: 24px;
        font-weight: bold;
        color: #0d8ca1;
    }
</style>
""", unsafe_allow_html=True)

# 3. Barra de Navegación (Simulada con columnas)
col_nav1, col_nav2 = st.columns([1, 2])

with col_nav1:
    # Usamos markdown para el logo para tener más control visual
    st.markdown("### 🧭 Descubre Arica y Parinacota")

with col_nav2:
    # Botones de navegación alineados a la derecha (simulado)
    c1, c2, c3, c4 = st.columns(4)
    c1.button("🏠 Inicio", use_container_width=True)
    c2.button("🧭 Explorar", use_container_width=True)
    c3.button("📅 Planificador (3)", use_container_width=True)
    c4.button("🏢 Agencias", use_container_width=True)

st.write("") # Espacio

# 4. Sección Hero (Imagen Principal)
# Usamos HTML puro aquí porque Streamlit no permite poner texto sobre imagen nativamente
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Descubre la magia del norte<br>de Chile</div>
    <div class="hero-subtitle">Playas infinitas, valles fértiles, altiplano andino y milenaria cultura. Todo en un solo destino.</div>
    <br>
    <a href="#" class="hero-btn">⏱ Comenzar a explorar ➝</a>
</div>
""", unsafe_allow_html=True)


# 5. Sección Inferior (Dos Columnas: Clima y Conversor)
col_left, col_right = st.columns(2)

# --- Tarjeta Izquierda: Clima ---
with col_left:
    with st.container():
        st.markdown("##### ☁️ Clima Actual - Arica")
        
        # Columnas internas para el icono grande y los detalles
        c_icon, c_temp, c_details = st.columns([1, 1, 2])
        
        with c_icon:
            st.markdown("<h1 style='text-align: center;'>☀️</h1>", unsafe_allow_html=True)
        
        with c_temp:
            st.metric(label="Soleado", value="22°C")
            
        with c_details:
            st.caption("💧 Humedad: 65%")
            st.caption("🍃 Viento: 12 km/h")

# --- Tarjeta Derecha: Conversor de Divisas ---
with col_right:
    with st.container():
        st.markdown("##### 💲 Conversor de Divisas")
        
        amount = st.number_input("Cantidad", value=1000, step=100)
        
        curr_c1, curr_c2 = st.columns(2)
        with curr_c1:
            currency_from = st.selectbox("De", ["CLP - Peso Chileno", "USD - Dólar", "EUR - Euro"])
        with curr_c2:
            currency_to = st.selectbox("A", ["USD - US Dollar", "CLP - Peso Chileno", "EUR - Euro"])
            
        # Lógica simple de conversión (tasas fijas para el ejemplo)
        # En una app real, usarías una API
        rate = 0.0011 if currency_from == "CLP - Peso Chileno" and currency_to == "USD - US Dollar" else 930
        
        if currency_from == currency_to:
            result = amount
        elif "CLP" in currency_from and "USD" in currency_to:
            result = amount * 0.00107
        elif "USD" in currency_from and "CLP" in currency_to:
            result = amount * 935
        else:
            result = amount * 1.1 # Ejemplo genérico
            
        st.markdown("Convertir:")
        st.markdown(f"<div class='price-text'>${result:,.2f} {currency_to.split(' - ')[0]}</div>", unsafe_allow_html=True)
