import streamlit as st
import pandas as pd
import plotly.express as px

# ========== CONFIGURASI ==========
st.set_page_config(page_title="Dashboard Google Sheet", layout="wide")

# ========== SETUP LINK GOOGLE SHEET ==========
sheet_id = "1btaoOSn3StOn_NSROY8tdgV_Y9jRVAF45PdTITWGlmY"
sheet_name = "Sheet1"  # Pastikan sesuai
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📊 Menu Navigasi")
    selected = st.radio("Pilih halaman:", ["📄 Tabel Data", "📈 Visualisasi"])

# ========== LOAD DATA ==========
@st.cache_data
def load_data():
    return pd.read_csv(csv_url)

try:
    df = load_data()
except Exception as e:
    st.error("❌ Gagal memuat data dari Google Sheets")
    st.stop()

# ========== PREPROCESS DATA ==========
# Fungsi konversi harga dari format 'Rp1.000.000,00' menjadi integer
def to_number(s):
    try:
        return int(str(s).replace("Rp", "").replace(".", "").replace(",", "").strip())
    except:
        return None

df["harga_baru"] = df["Harga (Rp)"].apply(to_number)
df["harga_lama"] = df["Harga Lama"].apply(to_number)
df["checklist_flag"] = df["CHECKLIST"].map({True: "Diceklis", False: "Tidak", "TRUE": "Diceklis", "FALSE": "Tidak"}).fillna("Tidak")

# ========== HALAMAN: TABEL ==========
if selected == "📄 Tabel Data":
    st.title("📄 Data dari Google Sheet")
    st.dataframe(df, use_container_width=True)

# ========== HALAMAN: VISUALISASI ==========
elif selected == "📈 Visualisasi":
    st.title("📈 Visualisasi Data Mobil")

    # 1. Jumlah unit per Model
    st.subheader("Jumlah Unit per Model")
    fig_model = px.histogram(df, x="Model", color="Model", title="Jumlah Mobil per Model")
    st.plotly_chart(fig_model, use_container_width=True)

    # 2. Distribusi STATUS Update
    st.subheader("Status Update (SUDAH / BELUM)")
    fig_status = px.pie(df, names="STATUS", title="Distribusi STATUS Update")
    st.plotly_chart(fig_status, use_container_width=True)

    # 3. Perbandingan Harga Lama vs Baru
    st.subheader("Perbandingan Harga Lama dan Harga Baru")
    harga_df = df.dropna(subset=["harga_baru", "harga_lama"])
    if not harga_df.empty:
        fig_harga = px.bar(
            harga_df,
            x="Tipe",
            y=["harga_baru", "harga_lama"],
            barmode="group",
            color_discrete_map={"harga_baru": "green", "harga_lama": "red"},
            title="Harga Baru vs Harga Lama per Tipe"
        )
        st.plotly_chart(fig_harga, use_container_width=True)
    else:
        st.info("Tidak ada data harga lama untuk dibandingkan.")

    # 4. Checklist Status Count
    st.subheader("Status Checklist")
    checklist_counts = df["checklist_flag"].value_counts().reset_index()
    checklist_counts.columns = ["Checklist", "Jumlah"]
    fig_checklist = px.bar(checklist_counts, x="Checklist", y="Jumlah", color="Checklist", title="Checklist Status")
    st.plotly_chart(fig_checklist, use_container_width=True)
