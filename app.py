import streamlit as st
import pandas as pd
import numpy as np

# Forzar el tipo de texto tradicional para evitar conflictos con Arrow/Streamlit
pd.set_option("mode.string_storage", "python")

# Configuración de la página
st.set_page_config(
    page_title="Simulador Financiero - Comercio Exterior",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Simulador Financiero: Comercio Exterior, Aranceles y Punto de Equilibrio")
st.markdown("""
Herramienta especializada para proyectos de **Negocios Internacionales**. Permite simular la conversión de divisas, 
la cadena de valor bajo **Incoterms (FOB/CIF)**, el pago de **aranceles e IVA de importación**, gastos aduanales, 
costos operativos y el punto de equilibrio financiero con análisis por canales de distribución.
""")

# --- BARRA LATERAL: PARÁMETROS DE ENTRADA ---
st.sidebar.header("🎛️ Panel de Control Global")

# 1. Módulo de Proveedor y Divisas
st.sidebar.subheader("1. Moneda y Proveedor")
moneda = st.sidebar.selectbox("Moneda de Proveedor / Extranjera", ["USD ($)", "EUR (€)", "CAD ($)"])
tipo_cambio = st.sidebar.number_input("Tipo de Cambio (Moneda a MXN)", value=20.00, min_value=1.00, step=0.10)
costo_insumo_ext = st.sidebar.number_input("Costo de Insumo / Producto (Moneda Extranjera)", value=20.00, min_value=0.01, step=1.00)

# 2. Módulo de Logística e Incoterms
st.sidebar.subheader("2. Logística e Incoterms")
incoterm = st.sidebar.selectbox("Seleccionar Incoterm", ["EXW (En Fábrica)", "FOB (Free On Board)", "CIF (Cost, Insurance and Freight)"])

flete_interno = 0.0
seguro_interno = 0.0
flete_internacional = 0.0
seguro_internacional = 0.0

if incoterm == "EXW (En Fábrica)":
    flete_interno = st.sidebar.number_input("Costo Flete Interno Origen (MXN)", value=1500.0, step=100.0)
    flete_internacional = st.sidebar.number_input("Flete Internacional (USD)", value=300.0, step=50.0)
    seguro_internacional = st.sidebar.number_input("Seguro Internacional (USD)", value=50.0, step=10.0)
elif incoterm == "FOB (Free On Board)":
    flete_internacional = st.sidebar.number_input("Flete Internacional (USD)", value=300.0, step=50.0)
    seguro_internacional = st.sidebar.number_input("Seguro Internacional (USD)", value=50.0, step=10.0)
else: # CIF
    flete_internacional = 0.0  
    seguro_internacional = 0.0 

# 3. Módulo de Aranceles e Impuestos Aduanales
st.sidebar.subheader("3. Aranceles e Impuestos")
arancel_pct = st.sidebar.slider("Arancel de Importación (Ad-Valorem %)", min_value=0.0, max_value=50.0, value=10.0, step=0.5)
tasa_iva = 0.16 
honorarios_agente = st.sidebar.number_input("Honorarios Agente Aduanal (MXN)", value=2500.0, step=100.0)

# 4. Costos Operativos de la Empresa
st.sidebar.subheader("4. Costos Operativos (Fijos y Variables)")
costos_fijos_mes = st.sidebar.number_input("Costos Fijos Mensuales (MXN)", value=50000.0, step=5000.0)
precio_venta_base = st.sidebar.number_input("Precio de Venta Base al Mercado (MXN)", value=1200.0, step=50.0)

# --- CÁLCULOS DE COMERCIO EXTERIOR ---
costo_insumo_mxn = costo_insumo_ext * tipo_cambio
flete_int_mxn = flete_internacional * tipo_cambio
seguro_int_mxn = seguro_internacional * tipo_cambio

if incoterm == "EXW (En Fábrica)":
    valor_en_aduana = costo_insumo_mxn + flete_interno + flete_int_mxn + seguro_int_mxn
elif incoterm == "FOB (Free On Board)":
    valor_en_aduana = costo_insumo_mxn + flete_int_mxn + seguro_int_mxn
else: 
    valor_en_aduana = costo_insumo_mxn 

monto_arancel = valor_en_aduana * (arancel_pct / 100.0)
base_iva = valor_en_aduana + monto_arancel
monto_iva = base_iva * tasa_iva

costo_total_importacion = valor_en_aduana + monto_arancel + honorarios_agente

# --- PANTALLA PRINCIPAL: DESGLOSE FINANCIERO ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Estructura de Costos de Importación")
    df_costos = pd.DataFrame({
        "Concepto": [
            "Valor de la Mercancía (MXN)",
            "Logística / Fletes y Seguros",
            "Valor en Aduana (Base Gravable)",
            f"Arancel Ad-Valorem ({arancel_pct}%)",
            "Honorarios Agente Aduanal",
            "IVA de Importación (16%)",
            "Costo Total Unitario (Landed Cost)"
        ],
        "Monto (MXN)": [
            f"${costo_insumo_mxn:,.2f}",
            f"${(flete_interno + flete_int_mxn + seguro_int_mxn):,.2f}",
            f"${valor_en_aduana:,.2f}",
            f"${monto_arancel:,.2f}",
            f"${honorarios_agente:,.2f}",
            f"${monto_iva:,.2f}",
            f"${costo_total_importacion:,.2f}"
        ]
    })
    st.table(df_costos)

with col2:
    st.subheader("🎯 Punto de Equilibrio y Márgenes")
    
    margen_contribucion = precio_venta_base - costo_total_importacion
    if margen_contribucion > 0:
        punto_equilibrio_unidades = costos_fijos_mes / margen_contribucion
        punto_equilibrio_ventas = punto_equilibrio_unidades * precio_venta_base
        
        st.success(f"**Punto de Equilibrio en Unidades:** {int(np.ceil(punto_equilibrio_unidades))} unidades/mes")
        st.info(f"**Punto de Equilibrio en Ventas (MXN):** ${punto_equilibrio_ventas:,.2f} MXN")
        st.metric("Margen de Contribución Unitario", f"${margen_contribucion:,.2f} MXN", f"{(margen_contribucion/precio_venta_base)*100:.1f}% sobre venta")
    else:
        st.error("⚠️ El precio de venta es menor o igual al costo total de importación. Ajusta los parámetros en la barra lateral.")

# --- MÓDULO: SIMULACIÓN DE MÁRGENES POR CANAL DE DISTRIBUCIÓN ---
st.markdown("---")
st.subheader("🌐 Simulación de Márgenes por Canal de Distribución")
st.markdown("Analiza la rentabilidad y el precio final sugerido según el canal comercial al que decidas dirigir tu producto importado:")

col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    st.markdown("### 🏢 Mayoreo / B2B")
    markup_mayoreo = st.slider("Margen de Utilidad Deseado (%)", 15, 50, 25, key="mayoreo")
    precio_mayoreo = costo_total_importacion * (1 + (markup_mayoreo / 100.0))
    utilidad_mayoreo = precio_mayoreo - costo_total_importacion
    st.write(f"**Precio Sugerido:** ${precio_mayoreo:,.2f} MXN")
    st.write(f"**Utilidad Unitaria:** ${utilidad_mayoreo:,.2f} MXN")

with col_c2:
    st.markdown("### 🛍️ Detallista / Retail")
    markup_retail = st.slider("Margen de Utilidad Deseado (%)", 30, 100, 50, key="retail")
    precio_retail = costo_total_importacion * (1 + (markup_retail / 100.0))
    utilidad_retail = precio_retail - costo_total_importacion
    st.write(f"**Precio Sugerido:** ${precio_retail:,.2f} MXN")
    st.write(f"**Utilidad Unitaria:** ${utilidad_retail:,.2f} MXN")

with col_c3:
    st.markdown("### 💻 E-commerce / Directo")
    markup_ecom = st.slider("Margen de Utilidad Deseado (%)", 50, 150, 80, key="ecom")
    precio_ecom = costo_total_importacion * (1 + (markup_ecom / 100.0))
    utilidad_ecom = precio_ecom - costo_total_importacion
    st.write(f"**Precio Sugerido:** ${precio_ecom:,.2f} MXN")
    st.write(f"**Utilidad Unitaria:** ${utilidad_ecom:,.2f} MXN")

# --- GRÁFICA NATIVA DE COMPARATIVA DE CANALES ---
st.markdown("---")
st.subheader("📈 Comparativa Visual de Precios por Canal de Distribución")

df_canales = pd.DataFrame({
    "Precio de Venta Sugerido (MXN)": [precio_mayoreo, precio_retail, precio_ecom]
}, index=["Mayoreo / B2B", "Detallista / Retail", "E-commerce / Directo"])

st.bar_chart(df_canales)