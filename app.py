import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# ========== CONFIG ==========
st.set_page_config(page_title="System Meslon Digital", layout="wide")

# ========== STYLE ==========
st.markdown("""
    <style>
    .meslon-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #4A6CF7;
        margin-top: 2rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2em;
        color: gray;
        margin-bottom: 2rem;
    }
    .chat-box {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1rem;
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 1rem;
    }
    .user-msg {
        color: white;
        background-color: #4A6CF7;
        padding: 0.6rem 1rem;
        border-radius: 1rem;
        margin: 0.4rem 0;
        text-align: right;
        font-size: 1rem;
    }
    .bot-msg {
        background-color: #444;
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 1rem;
        margin: 0.4rem 0;
        text-align: left;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


# ========== LOAD DATA ==========
sheet2_url = "https://docs.google.com/spreadsheets/d/1qV5t1JSeYT6Lr5pPmbUqdPYLOWCDshOn5CTzRINyPZM/gviz/tq?tqx=out:csv&sheet=Sheet1"

@st.cache_data(ttl=60)
def load_data(sheet_url):
    return pd.read_csv(sheet_url)

try:
    df_customer_raw = load_data(sheet2_url)
    df_customer = df_customer_raw.loc[:, ~df_customer_raw.columns.str.contains("^Unnamed")]
    df_customer.replace("None", pd.NA, inplace=True)
except Exception as e:
    st.error("❌ Gagal memuat data Google Sheets")
    st.stop()

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("📊 Navigasi")
    menu = st.radio("Pilih halaman:", [
        "🏠 Home",
        "📗 Data Customer",
        "📈 Analisis Data",
        "🤖 ChatBot"
    ])

# ========== HOME ==========
if menu == "🏠 Home":
    st.markdown('<div class="meslon-title">System Meslon Digital</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Selamat datang di sistem dashboard & layanan interaktif</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(
            "https://images.unsplash.com/photo-1635837594301-aee27378931f?q=80&w=871&auto=format&fit=crop&ixlib=rb-4.1.0",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        ### Apa itu Meslon Digital?

        Meson Digital adalah platform monitoring data dan interaksi digital yang memudahkan Anda melihat informasi penting dengan cepat dan modern.

        **Fitur:**
        - Visualisasi data otomatis  
        - Integrasi Google Sheets  
        - ChatBot untuk interaksi dasar  
        """)

# ========== DATA CUSTOMER ==========
elif menu == "📗 Data Customer":
    st_autorefresh(interval=1000, key="datarefresh")
    st.title("📗 TABEL DATA CUSTOMER")

    # Export (di atas tabel)
    st.subheader("⬇️ Export Data Customer")
    selected_cols = st.multiselect(
        "Pilih kolom yang ingin diekspor:",
        options=df_customer.columns.tolist(),
        default=df_customer.columns.tolist()
    )

    if selected_cols:
        export_df = df_customer[selected_cols].drop_duplicates().dropna(how="all")
        st.download_button(
            label="💾 Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="data_customer_terpilih.csv",
            mime="text/csv"
        )

    # Tampilkan data
    st.dataframe(df_customer, use_container_width=True)

# ========== ANALISIS DATA ==========
elif menu == "📈 Analisis Data":
    st.title("📈 Insight Bisnis dari Data Customer")

    st.subheader("👥 Jumlah Total Customer")
    st.metric("Total Customer Terdaftar", len(df_customer))

    st.subheader("🏢 Top 5 Perusahaan dengan Customer Terbanyak")
    perusahaan_kolom = [col for col in df_customer.columns if "perusahaan" in col.lower()]
    if perusahaan_kolom:
        top_perusahaan = df_customer[perusahaan_kolom[0]].value_counts().head(5)
        st.bar_chart(top_perusahaan)
    else:
        st.warning("Kolom perusahaan tidak ditemukan.")

    st.subheader("📞 Kanal Kontak yang Paling Sering Digunakan")
    kontak_summary = {}
    kontak_kolom_dict = {
        "Email": ["email", "email address"],
        "WhatsApp": ["whatsapp", "no whatsapp"],
        "Instagram": ["instagram"],
        "Website": ["website", "website edutec.com"]
    }

    for label, keyword_list in kontak_kolom_dict.items():
        for keyword in keyword_list:
            match = [col for col in df_customer.columns if keyword.lower() in col.lower()]
            if match:
                kontak_summary[label] = df_customer[match[0]].notna().sum()
                break

    if kontak_summary:
        st.dataframe(pd.DataFrame.from_dict(kontak_summary, orient="index", columns=["Jumlah"]).sort_values(by="Jumlah", ascending=False))
    else:
        st.warning("Tidak ada kolom kontak ditemukan.")

    st.subheader("📌 Persentase Customer yang Mengisi Kontak")
    kontak_kolom_valid = [col for col in df_customer.columns if any(k in col.lower() for k in ["email", "whatsapp", "instagram", "website"])]
    if kontak_kolom_valid:
        total = len(df_customer)
        kontak_lengkap = df_customer[kontak_kolom_valid].notna().any(axis=1).sum()
        st.metric("Customer Isi Minimal Satu Kontak", f"{kontak_lengkap}", f"{(kontak_lengkap / total) * 100:.1f}%")
    else:
        st.warning("Tidak ada kolom kontak yang bisa dihitung.")

# ========== CHATBOT ==========
elif menu == "🤖 ChatBot":
    st.title("🤖 ChatBot Sederhana")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ✅ NOTE PROMPT
    with st.expander("📌 Prompt yang Bisa Digunakan"):
        st.markdown("""
        Berikut beberapa contoh pesan yang bisa kamu ketik untuk mendapatkan informasi dari data customer:

        - **total customer** → Menampilkan jumlah seluruh customer  
        - **email** → Menampilkan berapa customer yang mengisi email  
        - **5 customer terakhir** → Menampilkan 5 customer paling akhir  
        - **dari perusahaan [nama]** → Menampilkan jumlah customer dari perusahaan tertentu  
        - **siapa kamu** → Mengenal chatbot  
        """)

    # Kotak chat history
    with st.container():
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for role, msg in st.session_state.chat_history:
            css_class = "user-msg" if role == "user" else "bot-msg"
            st.markdown(f'<div class="{css_class}">{msg}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Form chat
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Ketik pesan Anda...")
        submitted = st.form_submit_button("Kirim 💬")

    # Logika respon ChatBot
    if submitted and user_input.strip():
        st.session_state.chat_history.append(("user", user_input))
        user_input_lower = user_input.lower()

        if "total customer" in user_input_lower:
            response = f"Total customer saat ini ada {len(df_customer)} orang."

        elif "5 customer terakhir" in user_input_lower:
            try:
                recent_customers = df_customer.tail(5)
                nama_col = df_customer.columns[0]
                response = "5 customer terakhir:\n" + "\n".join(recent_customers[nama_col].astype(str).tolist())
            except:
                response = "Maaf, data customer tidak bisa dibaca."

        elif "email" in user_input_lower:
            email_cols = [col for col in df_customer.columns if "email" in col.lower()]
            if email_cols:
                count = df_customer[email_cols[0]].notna().sum()
                response = f"Ada {count} customer yang mengisi alamat email."
            else:
                response = "Kolom email tidak ditemukan dalam data."

        elif "dari perusahaan" in user_input_lower:
            keyword = user_input_lower.split("perusahaan")[-1].strip()
            perusahaan_cols = [col for col in df_customer.columns if "perusahaan" in col.lower()]
            if perusahaan_cols and keyword:
                match = df_customer[df_customer[perusahaan_cols[0]].str.contains(keyword, case=False, na=False)]
                response = f"Ada {len(match)} customer dari perusahaan \"{keyword}\"."
            else:
                response = "Data perusahaan tidak ditemukan atau tidak lengkap."

        elif "siapa kamu" in user_input_lower:
            response = "Saya adalah chatbot dari Sistem Meslon Digital 🤖"

        elif "data" in user_input_lower:
            response = "Data customer bisa dilihat di menu 'Data Customer' ya!"

        elif "hai" in user_input_lower or "hi" in user_input_lower:
            response = "Hai juga! Ada yang bisa saya bantu?"

        else:
            response = "Maaf, saya belum mengerti. Silakan coba prompt seperti 'total customer', 'email', atau 'dari perusahaan ABC'. 😊"

        st.session_state.chat_history.append(("bot", response))

