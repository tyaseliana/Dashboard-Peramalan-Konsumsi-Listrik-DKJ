import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Peramalan Konsumsi Listrik DKJ",
    page_icon="⚡",
    layout="wide"
)

# Judul dalam halaman: rata tengah + kata miring
st.markdown(
    """
    <h1 style="text-align: center;">
        Peramalan Konsumsi Listrik <br>Provinsi Daerah Khusus Jakarta (DKJ)
    </h1>
    """,
    unsafe_allow_html=True
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 10rem !important;
        padding-right: 10rem !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }

    .main-header {
        margin-top: 0.5rem !important;
        margin-bottom: 1.5rem !important;
    }

    .metric-container {
        display: flex;
        gap: 1rem;
        align-items: stretch;
    }

    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    p, li {
        font-size: 1.1rem !important;
    }

    /* Styling untuk multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #2a5298 !important;
        color: white !important;
        border: 1px solid #2a5298 !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        margin: 2px !important;
    }

    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
        font-weight: 500 !important;
    }

    .stMultiSelect [data-baseweb="tag"] svg {
        color: white !important;
        opacity: 0.8 !important;
    }

    .stMultiSelect [data-baseweb="tag"] svg:hover {
        opacity: 1 !important;
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 3px !important;
    }

    .stMultiSelect [data-baseweb="select"] {
        border: 2px solid #2a5298 !important;
        border-radius: 8px !important;
    }

    .stMultiSelect [data-baseweb="menu"] [data-highlighted="true"] {
        background-color: #2a5298 !important;
        color: white !important;
    }

    .stMultiSelect [data-baseweb="menu"] [aria-selected="true"] {
        background-color: #2a5298 !important;
        color: white !important;
    }

    .stMultiSelect [data-baseweb="select"]:focus-within {
        border-color: #1e3c72 !important;
        box-shadow: 0 0 0 2px rgba(42, 82, 152, 0.3) !important;
    }

    /* Styling untuk button */
    .stButton > button {
        background-color: #2a5298 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-weight: bold !important;
    }

    .stButton > button:hover {
        background-color: #1e3c72 !important;
        color: white !important;
    }

    .stButton > button:focus {
        background-color: #2a5298 !important;
        color: white !important;
        box-shadow: 0 0 0 2px rgba(42, 82, 152, 0.3) !important;
    }

    /* Styling untuk dataframe */
    .stDataFrame {
        background-color: white !important;
    }

    .stDataFrame [data-testid="stDataFrame"] > div {
        background-color: white !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    .stDataFrame thead th {
        background-color: #2a5298 !important;
        color: white !important;
        font-weight: bold !important;
    }

    .stDataFrame tbody td {
        background-color: white !important;
    }

    /* Model table styling */
    .model-table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 1.05rem;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .model-table th, .model-table td {
        border: 1px solid #ccc;
        padding: 0.6rem;
        text-align: left;
    }
    
    .model-table th {
        background-color: #2a5298;
        color: white;
    }
    
    .model-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .model-table tr:nth-child(3) {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Background image
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    image_base64 = get_base64_image("pixnio-4634x3476-edit.png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: 
                linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)),
                url("data:image/jpeg;base64,{image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    # Skip background image if file not found
    pass

# Load data functions
@st.cache_data
def load_historical_data():
    file_path = r'DATA AKTUAL.xlsx'
    df = pd.read_excel(file_path)
    df.rename(columns={df.columns[0]: 'Date', 'Actual_Consumption': 'Konsumsi'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    return df

@st.cache_data
def load_forecast_real():
    file_path = r'DASHBOARD.xlsx'
    df = pd.read_excel(file_path)
    df.columns = ['Date', 'ARIMA', 'ANN', 'HYBRID']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Hybrid ARIMA-NN'] = df['HYBRID']
    return df

# Load data
historical_data = load_historical_data()
forecast_data = load_forecast_real()

# Mapping bulan ke Bahasa Indonesia
bulan_id = {
    'Jan': 'Januari', 'Feb': 'Februari', 'Mar': 'Maret', 'Apr': 'April',
    'May': 'Mei', 'Jun': 'Juni', 'Jul': 'Juli', 'Aug': 'Agustus',
    'Sep': 'September', 'Oct': 'Oktober', 'Nov': 'November', 'Dec': 'Desember'
}

# ====================== Pendahuluan ======================
st.write("")
st.subheader("Latar Belakang Konsumsi Listrik Provinsi Daerah Khusus Jakarta (DKJ)")
st.markdown("""
<div style="text-align: justify; font-size:1.1rem; line-height:1.6;">
RUPTL 2025–2034 disusun dengan menekankan pentingnya perencanaan kelistrikan <b>berbasis provinsi</b> dan optimalisasi sistem interkoneksi (PLN, 2025). Pemahaman mendalam terhadap pola konsumsi listrik dibutuhkan untuk masing-masing wilayah. Provinsi Daerah Khusus Jakarta (DKJ) ini memiliki tingkat konsumsi listrik yang tinggi dan berperan penting dalam sistem kelistrikan nasional. Wilayah ini juga terhubung dalam sistem kelistrikan Jawa–Madura–Bali (Jamali), sistem interkoneksi terbesar di Indonesia yang ditargetkan memiliki <i>reserve margin</i> sebesar 34% pada 2034. Peramalan konsumsi listrik di Provinsi DKJ dapat mendukung penyusunan RUPTL <b>berbasis provinsi</b>.
</div><br>
""", unsafe_allow_html=True)

st.markdown("""
<div class="metric-container">
    <div class="metric-card">
        <h4>Sumber Data</h4>
        <p>Badan Pusat Statistik DKI Jakarta</p>
    </div>
    <div class="metric-card">
        <h4>Metode Peramalan</h4>
        <p>ARIMA, ANN, dan <i>hybrid</i> ARIMA–NN</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ====================== Grafik Konsumsi Listrik ======================
st.write("")
st.write("")
st.write("")
st.subheader("Grafik Konsumsi Listrik Provinsi Daerah Khusus Jakarta (DKJ)")

# Filter tahun
selected_years = st.multiselect(
    "Pilih tahun yang ingin ditampilkan:",
    options=sorted(historical_data['Year'].unique()),
    default=sorted(historical_data['Year'].unique())
)

# Filter data
filtered_data = historical_data[historical_data['Year'].isin(selected_years)]
min_point = filtered_data.loc[filtered_data['Konsumsi'].idxmin()]
max_point = filtered_data.loc[filtered_data['Konsumsi'].idxmax()]

# Grafik dan info
col1, col2 = st.columns([4, 1])
with col1:
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=filtered_data['Date'],
        y=filtered_data['Konsumsi'],
        mode='lines',
        name='Konsumsi Aktual',
        line=dict(color='#2a5298', width=2),
        hovertemplate='<b>Konsumsi Aktual</b><br>Tanggal: %{x}<br>Konsumsi: %{y:,.0f} kWh<extra></extra>'
    ))
    
    fig_line.update_layout(
        height=500,
        showlegend=False,
        hovermode='closest',
        margin=dict(l=80, r=40, t=40, b=80),
        xaxis=dict(title="Bulan", title_standoff=25, automargin=True),
        yaxis=dict(title="Konsumsi Listrik dalam kWh", title_standoff=25, automargin=True)
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.info(
        f"**📊 Informasi Konsumsi Listrik (kWh)**\n\n"
        f"**🔻 Terendah:**\n"
        f"{bulan_id[min_point['Date'].strftime('%b')]} {min_point['Date'].year}\n"
        f"({format(int(min_point['Konsumsi']), ',').replace(',', '.')})\n\n"
        f"**🔺 Tertinggi:**\n"
        f"{bulan_id[max_point['Date'].strftime('%b')]} {max_point['Date'].year}\n"
        f"({format(int(max_point['Konsumsi']), ',').replace(',', '.')})"
    )

# ====================== Boxplot Distribusi ======================
st.write("")
st.write("")
st.subheader("Distribusi Konsumsi Listrik Provinsi Daerah Khusus Jakarta (DKJ)")

# Persiapan data boxplot
boxplot_data = historical_data.copy()
boxplot_data['Bulan'] = boxplot_data['Date'].dt.strftime('%b')
boxplot_data['Bulan_Angka'] = boxplot_data['Date'].dt.month

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

selected_months = st.multiselect(
    "Pilih bulan yang ingin ditampilkan:",
    options=month_order,
    default=month_order
)

# Filter dan plot boxplot
filtered_boxplot_data = boxplot_data[boxplot_data['Bulan'].isin(selected_months)]
filtered_boxplot_data = filtered_boxplot_data.sort_values('Bulan_Angka')

if not filtered_boxplot_data.empty:
    median_per_bulan = (
        filtered_boxplot_data.groupby('Bulan', sort=False)['Konsumsi']
        .median().reset_index()
    )
    median_per_bulan['Bulan_Angka'] = median_per_bulan['Bulan'].apply(lambda x: month_order.index(x) + 1)
    median_per_bulan = median_per_bulan.sort_values('Bulan_Angka')

    highest_median = median_per_bulan.loc[median_per_bulan['Konsumsi'].idxmax()]
    lowest_median = median_per_bulan.loc[median_per_bulan['Konsumsi'].idxmin()]

    col1, col2 = st.columns([4, 1])
    with col1:
        fig_box, ax = plt.subplots(figsize=(12, 5))
        sns.boxplot(
            data=filtered_boxplot_data,
            x='Bulan',
            y='Konsumsi',
            order=[bulan for bulan in month_order if bulan in selected_months],
            color='#A4BEDC',
            ax=ax
        )
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Konsumsi Listrik dalam kWh')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig_box)

    with col2:
        st.info(
            f"**📊 Informasi Median Konsumsi Listrik (kWh)**\n\n"
            f"**🔻 Terendah:**\n"
            f"bulan {bulan_id[lowest_median['Bulan']]}\n"
            f"({format(int(lowest_median['Konsumsi']), ',').replace(',', '.')})\n\n"
            f"**🔺 Tertinggi:**\n"
            f"bulan {bulan_id[highest_median['Bulan']]}\n"
            f"({format(int(highest_median['Konsumsi']), ',').replace(',', '.')})"
        )
else:
    st.warning("Silakan pilih setidaknya satu bulan untuk menampilkan boxplot.")

# ====================== Evaluasi Model ======================
st.write("")
st.subheader("Evaluasi Pemodelan Konsumsi Listrik")

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("""
    <table class="model-table">
        <tr>
            <th>Model</th>
            <th>Spesifikasi</th>
            <th>RMSE</th>
            <th>MAPE</th>
        </tr>
        <tr>
            <td>ARIMA</td>
            <td>ARIMA(1,0,1)(1,1,0,12)</td>
            <td>83.627.852,34</td>
            <td>2,18%</td>
        </tr>
        <tr>
            <td>ANN</td>
            <td>ANN[12,25,1]</td>
            <td>106.231.327,88</td>
            <td>2,81%</td>
        </tr>
        <tr>
            <td><i>Hybrid</i> ARIMA-NN</td>
            <td><i>Hybrid</i> ARIMA(1,0,1)(1,1,0,12)-ANN[8,50,1]</td>
            <td>57.861.593,25</td>
            <td>1,59%</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

with col2:
    st.info(
        f"**Keterangan:**\n\n"
        f"Nilai **RMSE** dan **MAPE** yang **kecil** menunjukkan kualitas model yang **baik**.\n\n"
    )

# ====================== Hasil Forecasting ======================
st.write("")
st.write("")
st.subheader("Grafik Peramalan Konsumsi Listrik Periode 2025-2026 (*kilowatt-hour*)")

# Model options
model_options = {
    "ARIMA": "**Lihat Hasil Peramalan ARIMA**",
    "ANN": "**Lihat Hasil Peramalan ANN**",
    "Hybrid ARIMA-NN": "**Lihat Hasil Peramalan Hybrid ARIMA-NN**"
}

# Initialize session state
if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = "Hybrid ARIMA-NN"

# Model selection buttons
cols = st.columns(3)
for idx, (model_key, model_label) in enumerate(model_options.items()):
    with cols[idx]:
        if st.button(model_label, key=model_key, use_container_width=True):
            st.session_state["selected_model"] = model_key

selected_model = st.session_state["selected_model"]

# Prepare data for plotting
historical_filtered = historical_data[(historical_data['Date'].dt.year >= 2017) & (historical_data['Date'].dt.year <= 2024)]
forecast_filtered = forecast_data[(forecast_data['Date'].dt.year >= 2025) & (forecast_data['Date'].dt.year <= 2026)]

# Get connection points to avoid gaps
last_actual_date = historical_filtered['Date'].max()
last_actual_value = historical_filtered[historical_filtered['Date'] == last_actual_date]['Konsumsi'].iloc[0]

forecast_2025 = forecast_filtered[forecast_filtered['Date'].dt.year == 2025].copy()
forecast_2026 = forecast_filtered[forecast_filtered['Date'].dt.year == 2026].copy()

# Create connection point
connection_point = pd.DataFrame({
    'Date': [last_actual_date],
    selected_model: [last_actual_value]
})

# Connect forecast 2025
forecast_2025_connected = pd.concat([
    connection_point, 
    forecast_2025[['Date', selected_model]]
], ignore_index=True)

# Create plot
fig_model = go.Figure()

# Add historical data
fig_model.add_trace(go.Scatter(
    x=historical_filtered['Date'],
    y=historical_filtered['Konsumsi'],
    mode='lines',
    name='Aktual',
    line=dict(color='black', width=2),
    hovertemplate='<b>Aktual</b><br>Tanggal: %{x}<br>Konsumsi: %{y:,.0f} kWh<extra></extra>'
))

# Add forecast 2025
fig_model.add_trace(go.Scatter(
    x=forecast_2025_connected['Date'],
    y=forecast_2025_connected[selected_model],
    mode='lines',
    name=f'Peramalan {selected_model} 2025',
    line=dict(color='#2ca02c', width=2),
    connectgaps=True,
    hovertemplate=f'<b>Peramalan {selected_model} 2025</b><br>Tanggal: %{{x}}<br>Konsumsi: %{{y:,.0f}} kWh<extra></extra>'
))

# Connect forecast 2026
last_2025_date = forecast_2025['Date'].max()
last_2025_value = forecast_2025[forecast_2025['Date'] == last_2025_date][selected_model].iloc[0]

connection_2026 = pd.DataFrame({
    'Date': [last_2025_date],
    selected_model: [last_2025_value]
})

forecast_2026_connected = pd.concat([
    connection_2026,
    forecast_2026[['Date', selected_model]]
], ignore_index=True)

# Add forecast 2026
fig_model.add_trace(go.Scatter(
    x=forecast_2026_connected['Date'],
    y=forecast_2026_connected[selected_model],
    mode='lines',
    name=f'Peramalan {selected_model} 2026',
    line=dict(color='#1f77b4', width=2),
    connectgaps=True,
    hovertemplate=f'<b>Peramalan {selected_model} 2026</b><br>Tanggal: %{{x}}<br>Konsumsi: %{{y:,.0f}} kWh<extra></extra>'
))

# Update layout
fig_model.update_layout(
    height=500,
    hovermode='closest',
    margin=dict(l=80, r=40, t=40, b=80),
    xaxis=dict(title="Bulan", title_standoff=25, automargin=True),
    yaxis=dict(title="Konsumsi Listrik dalam kWh", title_standoff=25, automargin=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(fig_model, use_container_width=True)

# ====================== Tabel Forecast ======================
st.write("")
st.write("")
st.subheader("Tabel Hasil Peramalan Konsumsi Listrik Tahun 2025–2026")

# Prepare forecast table
forecast_data['Bulan'] = forecast_data['Date'].dt.strftime('%B %Y')
forecast_2025_2026 = forecast_data[
    forecast_data['Date'].dt.year.isin([2025, 2026])
].sort_values('Date')

forecast_2025_2026_rounded = forecast_2025_2026[['Bulan', 'ARIMA', 'ANN', 'Hybrid ARIMA-NN']].copy()
forecast_2025_2026_rounded[['ARIMA', 'ANN', 'Hybrid ARIMA-NN']] = (
    forecast_2025_2026_rounded[['ARIMA', 'ANN', 'Hybrid ARIMA-NN']]
    .round(0).astype(int)
)

# Format with thousand separators
forecast_display = forecast_2025_2026_rounded.copy()
for col in ['ARIMA', 'ANN', 'Hybrid ARIMA-NN']:
    forecast_display[col] = forecast_display[col].apply(lambda x: f"{x:,}".replace(',', '.'))

st.dataframe(
    forecast_display.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    height=458,
    column_config={
        "Bulan": st.column_config.TextColumn("Bulan", width="medium"),
        "ARIMA": st.column_config.TextColumn("ARIMA", width="medium"), 
        "ANN": st.column_config.TextColumn("ANN", width="medium"),
        "Hybrid ARIMA-NN": st.column_config.TextColumn("Hybrid ARIMA-NN", width="medium")
    }
)

# ====================== Kesimpulan ======================
st.write("")
st.write("")
st.subheader("Ringkasan")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-card">
            <h4>Metode Peramalan</h4>
            <p>Model terbaik untuk peramalan konsumsi listrik Provinsi DKJ adalah <i>hybrid</i> ARIMA-NN.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-card">
            <h4>Konsumsi Listrik</h4>
            <p>Konsumsi listrik bulanan tahun 2025 diramalkan mencapai puncaknya di bulan Oktober dan terendah di bulan Februari.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ====================== Footer ======================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><b>© 2025 Peramalan Konsumsi Listrik Daerah Khusus Jakarta<b/></p>
    <p><b>Eliana Mardiyaningtyas | Politeknik Statistika STIS</b></p>
</div>
""", unsafe_allow_html=True)