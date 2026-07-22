import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import base64
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. KONFIGURASI HALAMAN (HANYA SEKALI DI ATAS)
# ==========================================
st.set_page_config(
    page_title="SMART DASH",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

count = st_autorefresh(interval=30000, key="datarefreshcounter")

# Custom CSS untuk merapikan estetika & tata letak
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #0056b3;
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1e293b;
    }
    .metric-title {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .topic-card {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .sample-text {
        font-size: 12px;
        color: #475569;
        font-style: italic;
        background-color: #f1f5f9;
        padding: 6px 10px;
        border-radius: 4px;
        margin-top: 6px;
        border-left: 3px solid #cbd5e1;
        display: block;
    }
    .login-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    .login-title {
        font-size: 26px;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 5px;
    }
    .login-subtitle {
        font-size: 13px;
        color: #64748b;
        text-align: center;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div.stButton > button:first-child {
        background-color: #0056b3;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #004085;
        box-shadow: 0 4px 12px rgba(0, 86, 179, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SISTEM AUTENTIKASI (LOGIN)
# ==========================================
@st.cache_data(ttl=60)
def load_credentials_from_sheet():
    try:
        # Masukkan link CSV Publish to Web dari tab AKUN_ADMIN kamu di sini
        URL_AKUN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5yBJlYrdU2-FhV_xWuZg0hLJsdbfsrW-q1Y-gdmTlqA8LDX_PXWsRkZewXbvpmlnIuW702Ajamgm5/pub?gid=1272034771&single=true&output=csv"
        df_akun = pd.read_csv(URL_AKUN)
        
        # Membersihkan spasi pada nama kolom dan isinya
        df_akun.columns = df_akun.columns.str.strip().str.lower()
        
        return dict(zip(df_akun['username'].astype(str).str.strip(), df_akun['password'].astype(str).str.strip()))
    except Exception as e:
        # Fallback akun darurat jika koneksi sheet gagal
        return {"zae": "astra2026"}

USER_CREDENTIALS = load_credentials_from_sheet()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Fungsi Render Logo Menggunakan Base64 (Aman & Stabil di Streamlit)
def render_logo(svg_file="Logo.svg", width="250px", align="center"):
    if os.path.exists(svg_file):
        with open(svg_file, "r", encoding="utf-8") as f:
            svg_content = f.read()
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        st.markdown(
            f'<div style="text-align: {align}; margin-bottom: 5px;"><img src="data:image/svg+xml;base64,{b64}" width="{width}"/></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"<h2 style='text-align: {align}; color: #1e293b;'>📊 SMART DASH</h2>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        render_logo("Logo.svg", width="260px", align="center")
        st.markdown("<div class='login-subtitle'>Corporate Monitoring Dashboard</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username Anda")
            password = st.text_input("Password", type="password", placeholder="Masukkan password Anda")
            st.markdown("<br>", unsafe_allow_html=True)
            submit_button = st.form_submit_button("Masuk Dashboard", use_container_width=True)
            
            if submit_button:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login Berhasil! Memuat dashboard...")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
                    
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. PEMUATAN DATA (LOAD DATA)
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        URL_DM = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5yBJlYrdU2-FhV_xWuZg0hLJsdbfsrW-q1Y-gdmTlqA8LDX_PXWsRkZewXbvpmlnIuW702Ajamgm5/pub?gid=194885921&single=true&output=csv"
        URL_KOMENTAR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5yBJlYrdU2-FhV_xWuZg0hLJsdbfsrW-q1Y-gdmTlqA8LDX_PXWsRkZewXbvpmlnIuW702Ajamgm5/pub?gid=736850477&single=true&output=csv"

        df_dm = pd.read_csv(URL_DM)
        df_comment = pd.read_csv(URL_KOMENTAR)

        df_dm['Tanggal'] = pd.to_datetime(df_dm['Tanggal'], errors='coerce').dt.date
        df_comment['Tanggal'] = pd.to_datetime(df_comment['Tanggal'], errors='coerce').dt.date

        df_dm['Tonality'] = df_dm['Klasifikasi_Manual'] if 'Klasifikasi_Manual' in df_dm.columns else "Neutral"
        df_comment['Tonality'] = df_comment['Klasifikasi_Manual'] if 'Klasifikasi_Manual' in df_comment.columns else "Neutral"

        df_dm = df_dm.drop_duplicates(subset=['Tanggal', 'Pengirim', 'Isi Pesan'], keep='first')

        return df_dm, df_comment, None
        
    except Exception as e:
        df_dummy_dm = pd.DataFrame(columns=["Tanggal", "Waktu", "Nama Chat/Grup", "Pengirim", "Isi Pesan", "Kategori", "Topik Unik", "Tonality"])
        df_dummy_comment = pd.DataFrame(columns=["Tanggal", "Waktu", "Nama Pengirim", "Kategori", "Isi Komentar", "Topik Unik", "Tonality"])
        return df_dummy_dm, df_dummy_comment, str(e)

df_dm, df_comment, error_msg = load_data()

if error_msg:
    st.error(f"❌ Gagal memuat data live: {error_msg}")

def auto_categorize(text):
    if pd.isna(text):
        return "Lainnya"
    
    text = str(text).lower()
    
    # Keyword Mapping
    lalin_keywords = ['macet', 'padat', 'antrean', 'antrian', 'gerbang', 'etoll', 'e-toll', 'saldo', 'emoney', 'e-money', 'flazz', 'brizzi', 'tap', 'gardu', 'petugas', 'patroli', 'derek', 'kecelakaan', 'laka', 'contraflow']
    fasilitas_keywords = ['rest area', 'restarea', 'toilet', 'kamar mandi', 'mushola', 'masjid', 'spbu', 'bbm', 'parkir', 'lampu', 'penerangan', 'pju', 'lubang', 'aspal', 'rambu', 'guardrail', 'sampah', 'kebersihan', 'genangan']
    struk_keywords = ['struk', 'receipt', 'digital', 'cetak', 'download', 'unduh', 'riwayat', 'mutasi', 'slip', 'email', 'gagal kirim']
    
    # Cek kecocokan keyword
    for kw in lalin_keywords:
        if kw in text:
            return "Lalu Lintas"
            
    for kw in fasilitas_keywords:
        if kw in text:
            return "Fasilitas"
            
    for kw in struk_keywords:
        if kw in text:
            return "Struk Digital"
            
    return "Lainnya"
    
# ==========================================
# 4. SIDEBAR / TATA LETAK UTAMA & LOGOUT
# ==========================================
with st.sidebar:
    render_logo("Logo.svg", width="150px", align="center")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write(f"👤 Halo, **{st.session_state.username.upper()}**")
    if st.button("Keluar (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.markdown("---")
    st.markdown("### Filter Dashboard", unsafe_allow_html=True)

sumber_analisis = st.sidebar.radio(
    "Pilih Sumber Analisis Topik:",
    options=["Pesan (DM)", "Komentar"],
    index=0
)

df_dm_clean = df_dm.dropna(subset=['Tanggal']) if not df_dm.empty and 'Tanggal' in df_dm.columns else df_dm
df_comment_clean = df_comment.dropna(subset=['Tanggal']) if not df_comment.empty and 'Tanggal' in df_comment.columns else df_comment

if sumber_analisis == "Pesan (DM)":
    df_active_clean = df_dm_clean
else:
    df_active_clean = df_comment_clean

if not df_active_clean.empty:
    min_date = min(df_active_clean['Tanggal'])
    max_date = max(df_active_clean['Tanggal'])
    
    start_date, end_date = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    col_kategori = 'Kategori' if 'Kategori' in df_active_clean.columns else df_active_clean.columns[-1]
    list_kategori = ["Semua Kategori"] + list(df_active_clean[col_kategori].dropna().unique())
    selected_kategori = st.sidebar.selectbox("Pilih Kategori Komplain:", list_kategori)

    list_tonality = ["Semua Tonality", "Positive", "Neutral", "Negative"]
    selected_tonality = st.sidebar.selectbox("Pilih Tonality Sentimen:", list_tonality)

    df_filtered = df_active_clean[(df_active_clean['Tanggal'] >= start_date) & (df_active_clean['Tanggal'] <= end_date)]
    if selected_kategori != "Semua Kategori":
        df_filtered = df_filtered[df_filtered[col_kategori] == selected_kategori]
    if selected_tonality != "Semua Tonality":
        df_filtered = df_filtered[df_filtered['Tonality'] == selected_tonality]
else:
    df_filtered = df_active_clean
    start_date, end_date = datetime.now().date(), datetime.now().date()

if not df_filtered.empty:
    if 'Pengirim' in df_filtered.columns:
        df_user_filtered = df_filtered[df_filtered['Pengirim'] != 'Astra Tol Tamer']
    elif 'Nama Pengirim' in df_filtered.columns:
        df_user_filtered = df_filtered[df_filtered['Nama Pengirim'] != 'Astra Tol Tamer']
    else:
        df_user_filtered = df_filtered
else:
    df_user_filtered = df_filtered

# ==========================================
# 5. HEADER UTAMA DASHBOARD
# ==========================================
render_logo("Logo.svg", width="240px", align="center")
st.markdown("<h2 style='text-align: center; color: #1e293b; margin-top: 10px; margin-bottom: 0px;'>SMART DASHBOARD</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; margin-top: 2px;'>Astra Infra Toll Road Tangerang-Merak — Real-time Customer Feedback Monitoring</p>", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 6. KARTU METRIK UTAMA
# ==========================================
st.subheader("Kategori Komplain")
col1, col2, col3 = st.columns(3)

with col1:
    lalin_count = len(df_user_filtered[df_user_filtered['Kategori'].str.lower() == 'lalu lintas']) if (not df_user_filtered.empty and 'Kategori' in df_user_filtered.columns) else 0
    st.markdown(f"""
        <div class="metric-container" style="border-left-color: #dc3545;">
            <div class="metric-title">🚦 Lalu Lintas</div>
            <div class="metric-value">{lalin_count}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    fasilitas_count = len(df_user_filtered[df_user_filtered['Kategori'].str.lower() == 'fasilitas']) if (not df_user_filtered.empty and 'Kategori' in df_user_filtered.columns) else 0
    st.markdown(f"""
        <div class="metric-container" style="border-left-color: #ffc107;">
            <div class="metric-title">🚧 Fasilitas</div>
            <div class="metric-value">{fasilitas_count}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    struk_count = len(df_user_filtered[df_user_filtered['Kategori'].str.lower() == 'struk digital']) if (not df_user_filtered.empty and 'Kategori' in df_user_filtered.columns) else 0
    st.markdown(f"""
        <div class="metric-container" style="border-left-color: #28a745;">
            <div class="metric-title">📱 Struk Digital</div>
            <div class="metric-value">{struk_count}</div>
        </div>
    """, unsafe_allow_html=True)

# BARIS KPI SENTIMEN
col_pos, col_neu, col_neg = st.columns(3)
total_active = len(df_user_filtered) if not df_user_filtered.empty else 1

with col_pos:
    pos_count = len(df_user_filtered[df_user_filtered['Tonality'] == 'Positive']) if not df_user_filtered.empty else 0
    st.metric(label="😊 Sentimen Positif (Apresiasi)", value=pos_count, delta=f"{round(pos_count/total_active*100, 1)}% dari total")

with col_neu:
    neu_count = len(df_user_filtered[df_user_filtered['Tonality'] == 'Neutral']) if not df_user_filtered.empty else 0
    st.metric(label="😐 Sentimen Netral (Tanya/Info)", value=neu_count, delta=f"{round(neu_count/total_active*100, 1)}% dari total", delta_color="off")

with col_neg:
    neg_count = len(df_user_filtered[df_user_filtered['Tonality'] == 'Negative']) if not df_user_filtered.empty else 0
    st.metric(label="😡 Sentimen Negatif (Komplain)", value=neg_count, delta=f"-{round(neg_count/total_active*100, 1)}% dari total", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 7. VISUALISASI GRAFIK & DIAGRAM
# ==========================================
st.subheader("Analisis Visual Komplain & Sentimen")
chart_col1, chart_col2, chart_col3 = st.columns(3)

with chart_col1:
    st.write(f"*Tren Kasus Masuk ({sumber_analisis})*")
    if not df_user_filtered.empty and 'Tanggal' in df_user_filtered.columns:
        if 'Nama Chat/Grup' in df_user_filtered.columns:
            df_trend = df_user_filtered.groupby('Tanggal')['Nama Chat/Grup'].nunique().reset_index(name='Jumlah Komplain')
        else:
            df_trend = df_user_filtered.groupby('Tanggal').size().reset_index(name='Jumlah Komplain')
            
        fig_trend = px.line(
            df_trend, x='Tanggal', y='Jumlah Komplain',
            labels={'Tanggal': 'Tanggal', 'Jumlah Komplain': 'Total Kasus'},
            markers=True,
            color_discrete_sequence=['#F4991A']
        )
        fig_trend.update_xaxes(type='category')
        fig_trend.update_layout(margin=dict(l=20, r=20, t=10, b=20), height=300)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Belum ada data tanggal.")

with chart_col2:
    st.write(f"*Distribusi Kategori Komplain ({sumber_analisis})*")
    if not df_user_filtered.empty and 'Kategori' in df_user_filtered.columns:
        df_cat = df_user_filtered['Kategori'].value_counts().reset_index(name='Jumlah')
        df_cat.columns = ['Kategori', 'Jumlah']
        
        fig_pie = px.pie(
            df_cat, values='Jumlah', names='Kategori',
            hole=0.4,
            color_discrete_sequence=['#FF8F00', '#FBC02D', '#F5F5DC']
        )
        fig_pie.update_layout(margin=dict(l=20, r=20, t=10, b=20), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Belum ada data kategori.")

with chart_col3:
    st.write(f"*Proporsi Sebaran Tonality ({sumber_analisis})*")
    if not df_user_filtered.empty and 'Tonality' in df_user_filtered.columns:
        df_tonality = df_user_filtered['Tonality'].value_counts().reset_index(name='Jumlah')
        df_tonality.columns = ['Tonality', 'Jumlah']
        
        color_map = {'Positive': '#F5F5DC', 'Neutral': '#FF8F00', 'Negative': '#C62828'}
        
        fig_pie_tonality = px.pie(
            df_tonality, values='Jumlah', names='Tonality',
            hole=0.4,
            color='Tonality',
            color_discrete_map=color_map
        )
        fig_pie_tonality.update_layout(margin=dict(l=20, r=20, t=10, b=20), height=300)
        st.plotly_chart(fig_pie_tonality, use_container_width=True)
    else:
        st.info("Belum ada data sentimen.")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 8. TOP PEMBAHASAN PER KATEGORI
# ==========================================
st.markdown(f"### 🔝 Top Pembahasan per Kategori Utama (Sumber: {sumber_analisis})")
st.markdown("Berikut adalah topik keluhan terbanyak beserta *contoh keluhan langsung* dari pengguna jalan:")

topic_col1, topic_col2, topic_col3 = st.columns(3)

def get_top_topics_with_sample(df, category_name, top_n=3):
    try:
        if df.empty:
            return []
            
        col_kategori = 'Kategori' 
        if col_kategori not in df.columns:
             for col in df.columns:
                if 'kategori' in col.lower():
                    col_kategori = col
                    break
        
        col_message = None
        for col in df.columns:
            if col.strip().lower() == 'isi pesan':
                col_message = col
                break
        if not col_message:
            for col in df.columns:
                if any(key in col.lower() for key in ['pesan', 'komentar', 'isi', 'chat']):
                    col_message = col
                    break
        if not col_message:
            col_message = df.columns[4] if len(df.columns) > 4 else df.columns[-1]

        col_topic = 'Topik Unik'  
        if col_topic not in df.columns:
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['topik', 'topic', 'sub', 'detail']):
                    col_topic = col
                    break
            
        if not col_topic or col_topic not in df.columns:
            return []

        kategori_seragam = df[col_kategori].astype(str).str.strip().str.lower()
        kategori_target = category_name.strip().lower()
        df_cat = df[kategori_seragam == kategori_target]
        
        if df_cat.empty:
            return []

        results = []
        if col_topic and col_topic in df_cat.columns and df_cat[col_topic].notna().sum() > 0:
            df_valid_topic = df_cat[df_cat[col_topic].notna()]
            df_valid_topic = df_valid_topic[~df_valid_topic[col_topic].astype(str).str.strip().isin(['0', '1', '', 'nan', 'None', '#N/A', '#VALUE!'])]
            
            if not df_valid_topic.empty:
                top_counts = df_valid_topic[col_topic].value_counts().head(top_n)
                for topic, count in top_counts.items():
                    subset = df_valid_topic[df_valid_topic[col_topic] == topic]
                    valid_messages = subset[col_message].dropna().astype(str).tolist() if col_message else []
                    
                    clean_messages = []
                    for msg in valid_messages:
                        msg_clean = msg.strip()
                        if "sent an attachment" in msg_clean.lower() or len(msg_clean) <= 5:
                            continue
                        clean_messages.append(msg_clean)
                    
                    if clean_messages:
                        clean_messages = sorted(clean_messages, key=len, reverse=True)
                        sample_msg = clean_messages[0]
                    elif valid_messages:
                        sample_msg = valid_messages[0]
                    else:
                        sample_msg = "Tidak ada rincian pesan."
                        
                    if len(sample_msg) > 130:
                        sample_msg = sample_msg[:127] + "..."
                        
                    results.append({
                        'topik': topic,
                        'jumlah': count,
                        'sample': sample_msg
                    })
                    
        return results
    except Exception as e:
        return []

with topic_col1:
    st.markdown("<h4 style='color: #dc3545;'>🚦 Lalu Lintas</h4>", unsafe_allow_html=True)
    lalin_topics = get_top_topics_with_sample(df_user_filtered, 'Lalu Lintas')
    if lalin_topics:
        for idx, item in enumerate(lalin_topics):
            st.markdown(f"""
                <div class="topic-card" style="border-left: 4px solid #dc3545;">
                    <span style="font-weight:bold; color:#1e293b;">#{idx+1} {item['topik']}</span>
                    <br><span style="font-size:11px; color:#64748b;">Muncul: {item['jumlah']} kali</span>
                    <span class="sample-text">💬 "{item['sample']}"</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data topik untuk Lalu Lintas.")

with topic_col2:
    st.markdown("<h4 style='color: #ffc107;'>🚧 Fasilitas</h4>", unsafe_allow_html=True)
    fasilitas_topics = get_top_topics_with_sample(df_user_filtered, 'Fasilitas')
    if fasilitas_topics:
        for idx, item in enumerate(fasilitas_topics):
            st.markdown(f"""
                <div class="topic-card" style="border-left: 4px solid #ffc107;">
                    <span style="font-weight:bold; color:#1e293b;">#{idx+1} {item['topik']}</span>
                    <br><span style="font-size:11px; color:#64748b;">Muncul: {item['jumlah']} kali</span>
                    <span class="sample-text">💬 "{item['sample']}"</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data topik untuk Fasilitas.")

with topic_col3:
    st.markdown("<h4 style='color: #28a745;'>📱 Struk Digital</h4>", unsafe_allow_html=True)
    struk_topics = get_top_topics_with_sample(df_user_filtered, 'Struk Digital')
    if struk_topics:
        for idx, item in enumerate(struk_topics):
            st.markdown(f"""
                <div class="topic-card" style="border-left: 4px solid #28a745;">
                    <span style="font-weight:bold; color:#1e293b;">#{idx+1} {item['topik']}</span>
                    <br><span style="font-size:11px; color:#64748b;">Muncul: {item['jumlah']} kali</span>
                    <span class="sample-text">💬 "{item['sample']}"</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data topik untuk Struk Digital.")

st.markdown("<br><hr>", unsafe_allow_html=True)

# ==========================================
# 9. TABEL DETAIL DATA
# ==========================================
st.subheader("📋 Detail Data Mentah & Komentar")
tab_dm, tab_komen = st.tabs(["💬 Data Mentah DM", "💬 Data Komentar"])

with tab_dm:
    if not df_dm.empty:
        df_dm_filtered_table = df_dm[(df_dm['Tanggal'] >= start_date) & (df_dm['Tanggal'] <= end_date)] if not df_dm_clean.empty else df_dm
        default_cols_dm = [col for col in ["Tanggal", "Waktu", "Nama Chat/Grup", "Pengirim", "Isi Pesan", "Kategori", "Tonality"] if col in df_dm_filtered_table.columns]
        show_cols_dm = st.multiselect("Kolom DM yang ingin ditampilkan:", list(df_dm_filtered_table.columns), default=default_cols_dm, key="cols_dm")
        st.dataframe(df_dm_filtered_table[show_cols_dm], use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data DM.")

with tab_komen:
    if not df_comment.empty:
        df_comment_filtered_table = df_comment[(df_comment['Tanggal'] >= start_date) & (df_comment['Tanggal'] <= end_date)] if not df_comment_clean.empty else df_comment
        default_cols_comment = [col for col in ["Tanggal", "Waktu", "Nama Pengirim", "Kategori", "Isi Komentar", "Tonality"] if col in df_comment_filtered_table.columns]
        if not default_cols_comment:
            default_cols_comment = list(df_comment_filtered_table.columns[:6])
            
        show_cols_comment = st.multiselect("Kolom Komentar yang ingin ditampilkan:", list(df_comment_filtered_table.columns), default=default_cols_comment, key="cols_comment")
        st.dataframe(df_comment_filtered_table[show_cols_comment], use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data komentar.")
