import streamlit as st
import pandas as pd
import plotly.express as px

# ========== CONFIGURASI ==========
st.set_page_config(page_title="Dashboard Google Sheet", layout="wide")

# ========== LINK GOOGLE SHEET ==========
# Tabel 1: DATA HARGA MOBIL
sheet1_url = "https://docs.google.com/spreadsheets/d/1btaoOSn3StOn_NSROY8tdgV_Y9jRVAF45PdTITWGlmY/gviz/tq?tqx=out:csv&sheet=Sheet1"

# Tabel 2: DATA CUSTOMER
sheet2_url = "https://docs.google.com/spreadsheets/d/1qV5t1JSeYT6Lr5pPmbUqdPYLOWCDshOn5CTzRINyPZM/gviz/tq?tqx=out:csv&sheet=Sheet1"

# ========== LOAD DATA ==========
@st.cache_data
def load_data(sheet_url):
    return pd.read_csv(sheet_url)

try:
    df_mobil = load_data(sheet1_url)

    # Perbaikan untuk data customer, hilangkan kolom yang Unnamed
    df_customer_raw = load_data(sheet2_url)
    df_customer = df_customer_raw.loc[:, ~df_customer_raw.columns.str.contains("^Unnamed")]

except Exception as e:
    st.error("❌ Gagal memuat salah satu Google Sheets")
    st.stop()

# ========== PREPROSES DATA HARGA MOBIL ==========
def to_number(s):
    try:
        return int(str(s).replace("Rp", "").replace(".", "").replace(",", "").strip())
    except:
        return None

df_mobil["harga_baru"] = df_mobil["Harga (Rp)"].apply(to_number)
df_mobil["harga_lama"] = df_mobil["Harga Lama"].apply(to_number)
df_mobil["checklist_flag"] = df_mobil["CHECKLIST"].map({True: "Diceklis", False: "Tidak", "TRUE": "Diceklis", "FALSE": "Tidak"}).fillna("Tidak")

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📊 Menu Navigasi")
    selected = st.radio("Pilih halaman:", ["📘 DATA HARGA MOBIL", "📗 DATA CUSTOMER", "📈 VISUALISASI"])

# ========== HALAMAN: DATA HARGA MOBIL ==========
if selected == "📘 DATA HARGA MOBIL":
    st.title("📘 TABEL DATA HARGA MOBIL")
    st.dataframe(df_mobil, use_container_width=True)

# ========== HALAMAN: DATA CUSTOMER ==========
elif selected == "📗 DATA CUSTOMER":
    st.title("📗 TABEL DATA CUSTOMER")
    st.dataframe(df_customer, use_container_width=True)

# ========== HALAMAN: VISUALISASI ==========
elif selected == "📈 VISUALISASI":
    st.title("📈 VISUALISASI DATA HARGA MOBIL")

    st.subheader("Jumlah Unit per Model")
    fig_model = px.histogram(df_mobil, x="Model", color="Model", title="Jumlah Mobil per Model")
    st.plotly_chart(fig_model, use_container_width=True)

    st.subheader("Status Update (SUDAH / BELUM)")
    fig_status = px.pie(df_mobil, names="STATUS", title="Distribusi STATUS Update")
    st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Perbandingan Harga Lama dan Harga Baru")
    harga_df = df_mobil.dropna(subset=["harga_baru", "harga_lama"])
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

    st.subheader("Status Checklist")
    checklist_counts = df_mobil["checklist_flag"].value_counts().reset_index()
    checklist_counts.columns = ["Checklist", "Jumlah"]
    fig_checklist = px.bar(checklist_counts, x="Checklist", y="Jumlah", color="Checklist", title="Checklist Status")
    st.plotly_chart(fig_checklist, use_container_width=True)
