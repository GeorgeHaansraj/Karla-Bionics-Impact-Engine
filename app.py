import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import plotly.express as px
from openai import OpenAI
from fpdf import FPDF
import os

from api import COLLECTION_NAME


# ==========================================
# 1. SETUP & KONEKSI FIRESTORE (CACHED)
# ==========================================
# st.cache_resource memastikan Firebase tidak login berulang-ulang setiap kali tombol ditekan
@st.cache_resource
def init_connection():
    if not firebase_admin._apps:
        # GANTI NAMA FILE JSON INI DENGAN MILIKMU YANG ADA DI FOLDER LOKAL
        cred = credentials.Certificate(
            "karla-bionics-firebase-adminsdk-fbsvc-da0c821b20.json"
        )
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = init_connection()


# Fungsi menarik data dari Firestore ke Pandas DataFrame
@st.cache_data(ttl=600)  # Data di-cache selama 10 menit
def load_data():
    docs = db.collection(COLLECTION_NAME).stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)


# Memuat data
df = load_data()

# ==========================================
# 2. PENGATURAN HALAMAN (PAGE CONFIG)
# ==========================================
st.set_page_config(
    page_title="Karla Bionics Impact Engine",
    page_icon="🦾",
    layout="wide",  # Agar dasbor melebar memenuhi layar
)

# ==========================================
# 3. SISTEM ROUTING (SIDEBAR)
# ==========================================
st.sidebar.title("🦾 Karla Bionics")
st.sidebar.markdown("### Navigasi Sistem")

# Membuat radio button untuk navigasi halaman
halaman = st.sidebar.radio(
    "Pilih Tampilan Dasbor:", ["Publik / CSR Showcase", "Internal R&D (Raw Data)"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    f"Status Koneksi: Terhubung ke Firestore\nTotal Data: {len(df)} Laporan"
)

# ==========================================
# 4. LOGIKA TAMPILAN (VIEW LOGIC)
# ==========================================
if halaman == "Publik / CSR Showcase":
    st.title("🌟 Laporan Dampak & Keberlanjutan CSR")
    st.write(
        "Selamat datang di Dasbor Publik Karla Bionics. Di sini kami menyoroti narasi positif, kemandirian pasien, dan dampak sosial yang terukur (SDG 4)."
    )

    st.markdown("---")

    # Memastikan kolom Durasi dibaca sebagai angka (mengabaikan NaN/teks kosong)
    df["Durasi_Pakai_Jam"] = pd.to_numeric(
        df["Durasi_Pakai_Jam"], errors="coerce"
    ).fillna(0)

    # 1. HERO CARDS (Metrik Kinerja Utama)
    col1, col2, col3 = st.columns(3)
    total_pasien = len(df)
    total_jam_produktif = int(df["Durasi_Pakai_Jam"].sum())
    utilitas_positif = len(
        df[df["Status_Utilitas"].isin(["Sangat Berguna", "Cukup Berguna"])]
    )

    col1.metric(label="Total Penerima Manfaat", value=f"{total_pasien} Jiwa")
    col2.metric(
        label="Total Jam Produktif (Akumulasi)", value=f"{total_jam_produktif} Jam"
    )
    col3.metric(label="Pengguna Aktif & Terbantu", value=f"{utilitas_positif} Pasien")

    st.markdown("---")

    # 2. GRAFIK VISUALISASI
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Peta Sebaran Wilayah")
        # Menghitung jumlah pasien per domisili
        df_domisili = df["Domisili"].value_counts().reset_index()
        df_domisili.columns = ["Provinsi", "Jumlah Pasien"]

        # Membuat Bar Chart Interaktif
        fig_sebaran = px.bar(
            df_domisili,
            x="Provinsi",
            y="Jumlah Pasien",
            color="Provinsi",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_sebaran.update_layout(showlegend=False)
        st.plotly_chart(fig_sebaran, use_container_width=True)

    with chart_col2:
        st.subheader("Tingkat Kebermanfaatan Alat")
        # Menghitung persentase utilitas
        df_utilitas = df["Status_Utilitas"].value_counts().reset_index()
        df_utilitas.columns = ["Status", "Total"]

        # Membuat Donut Chart
        fig_util = px.pie(
            df_utilitas,
            names="Status",
            values="Total",
            hole=0.4,
            color="Status",
            color_discrete_map={
                "Sangat Berguna": "#2ecc71",
                "Cukup Berguna": "#3498db",
                "Terkendala": "#f1c40f",
                "Tidak Berguna": "#e74c3c",
            },
        )
        st.plotly_chart(fig_util, use_container_width=True)

    st.markdown("---")

    # 3. KUTIPAN TESTIMONI (Hanya Sentimen Positif)
    st.subheader("💬 Cerita Kebaikan (Testimoni)")
    # Menyaring data khusus yang positif
    df_positif = (
        df[df["Sentimen_Laporan"] == "Positif"].dropna(subset=["Kutipan_Asli"]).head(3)
    )

    for index, row in df_positif.iterrows():
        st.success(
            f"**{row['ID_Pasien']} ({row['Usia']} Tahun, {row['Domisili']})**\n\n> *\"{row['Kutipan_Asli']}\"*"
        )

    st.markdown("---")

    # 4. GENERATIVE STORYTELLING & EXPORT PDF
    st.subheader("🤖 Generative AI: Laporan Eksekutif Otomatis")
    st.write(
        "Sistem AI akan membaca metrik saat ini dan merangkai narasi laporan CSR profesional secara otomatis."
    )

    # Input API Key secara aman di antarmuka
    api_key_input = st.text_input(
        "Masukkan OpenAI API Key (sk-...) untuk men-generate laporan:", type="password"
    )

    if st.button("✨ Generate Narasi CSR & Siapkan PDF"):
        if not api_key_input:
            st.warning("⚠️ Silakan masukkan API Key OpenAI terlebih dahulu.")
        else:
            with st.spinner("AI sedang menganalisis data dan merangkai narasi..."):
                try:
                    # 1. ARAHKAN KE SERVER GROQ
                    client = OpenAI(
                        base_url="https://api.groq.com/openai/v1", api_key=api_key_input
                    )

                    # Prompting dinamis dengan metrik real-time
                    prompt_laporan = f"""
                    Tuliskan 2 paragraf narasi eksekutif yang profesional dan inspiratif untuk laporan donatur CSR Karla Bionics.
                    Gunakan data live berikut:
                    - Total Penerima Manfaat: {total_pasien} jiwa
                    - Total Jam Produktif (Akumulasi): {total_jam_produktif} jam
                    - Jumlah Pengguna Aktif & Terbantu: {utilitas_positif} pasien
                    
                    Instruksi Khusus:
                    - Fokus pada pencapaian Tujuan Pembangunan Berkelanjutan (SDG 4 & 10).
                    - Jelaskan bagaimana angka-angka ini mencerminkan peningkatan kemandirian penyandang disabilitas (tuna daksa).
                    - Gunakan bahasa Indonesia yang formal, elegan, dan apresiatif. Tanpa awalan sapaan surat.
                    """

                    # Pemanggilan LLM (gpt-oss-120b) untuk menghasilkan narasi
                    chat_completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",  # Harus persis dengan teks di menu dropdown
                        messages=[
                            {
                                "role": "system",
                                "content": "Anda adalah spesialis komunikasi CSR dan analis dampak sosial.",
                            },
                            {"role": "user", "content": prompt_laporan},
                        ],
                        temperature=0.7,
                    )

                    narasi_ai = chat_completion.choices[0].message.content

                    st.success("✅ Narasi berhasil dibuat!")
                    st.info(narasi_ai)

                    # Logika Pembuatan File PDF menggunakan FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(
                        0,
                        10,
                        "Laporan Eksekutif Dampak CSR - Karla Bionics",
                        ln=True,
                        align="C",
                    )
                    pdf.ln(10)

                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, "Ringkasan Metrik Utama:", ln=True)
                    pdf.set_font("Arial", "", 12)
                    pdf.cell(
                        0, 8, f"- Total Penerima Manfaat: {total_pasien} Jiwa", ln=True
                    )
                    pdf.cell(
                        0,
                        8,
                        f"- Total Jam Produktif: {total_jam_produktif} Jam",
                        ln=True,
                    )
                    pdf.cell(
                        0,
                        8,
                        f"- Pengguna Aktif & Terbantu: {utilitas_positif} Pasien",
                        ln=True,
                    )
                    pdf.ln(10)

                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, "Narasi Dampak Berkelanjutan:", ln=True)
                    pdf.set_font("Arial", "", 12)

                    # FPDF memerlukan encoding khusus (latin-1) agar tidak error saat membaca teks AI
                    narasi_bersih = narasi_ai.encode("latin-1", "replace").decode(
                        "latin-1"
                    )
                    pdf.multi_cell(0, 7, txt=narasi_bersih)

                    # Output PDF ke dalam format byte string agar bisa diunduh oleh Streamlit
                    pdf_output = pdf.output(dest="S").encode("latin-1")

                    # Tombol Unduh
                    st.download_button(
                        label="📄 Unduh Laporan PDF Eksekutif",
                        data=pdf_output,
                        file_name="Laporan_Eksekutif_Karla_Bionics.pdf",
                        mime="application/pdf",
                    )

                except Exception as e:
                    st.error(f"Terjadi kesalahan pada sistem AI: {str(e)}")

elif halaman == "Internal R&D (Raw Data)":
    st.title("🔧 Intelijen Pemeliharaan & Audit Hardware")
    st.write(
        "Peringatan: Tampilan ini tidak disensor. Berisi raw data operasional, Red Flag Matrix, dan log keluhan spesifik dari setiap ID Pasien."
    )

    st.markdown("---")

    # 1. RED FLAG MATRIX (Prioritas Servis)
    st.subheader("🚨 Red Flag Matrix (Tindakan Mendesak)")
    st.info(
        "Tabel ini secara otomatis memfilter pasien dengan Tingkat Urgensi Pemeliharaan 'Tinggi'. Teknisi harap segera menindaklanjuti."
    )

    # Memfilter data dengan urgensi tinggi
    df_red_flag = df[df["Tingkat_Urgensi_Pemeliharaan"] == "Tinggi"].copy()

    # Menampilkan tabel khusus untuk teknisi (hanya kolom yang relevan)
    if not df_red_flag.empty:
        kolom_teknisi = [
            "ID_Pasien",
            "Tanggal_Lapor",
            "Keluhan_Hardware",
            "Domisili",
            "Status_Utilitas",
        ]
        st.dataframe(df_red_flag[kolom_teknisi], use_container_width=True)
    else:
        st.success("Tidak ada pasien dengan tingkat urgensi tinggi saat ini.")

    st.markdown("---")

    # 2. ANALISIS KELUHAN HARDWARE (Grafik Batang)
    st.subheader("📊 Distribusi Kendala Fisik Alat")

    try:
        # Karena Keluhan_Hardware berbentuk list/array di Firestore, kita pisahkan (explode) agar bisa dihitung
        # Pastikan data di-convert ke tipe string terlebih dahulu agar aman
        df_keluhan = df.copy()
        df_keluhan["Keluhan_Hardware"] = df_keluhan["Keluhan_Hardware"].astype(str)

        # Membersihkan karakter kurung siku dari format string array
        df_keluhan["Keluhan_Hardware"] = df_keluhan["Keluhan_Hardware"].str.replace(
            r"\[|\]|'", "", regex=True
        )

        # Memisahkan string berdasarkan koma jika ada lebih dari 1 keluhan
        df_keluhan["Keluhan_Hardware"] = df_keluhan["Keluhan_Hardware"].str.split(", ")

        # Melakukan explode (meratakan list menjadi baris)
        df_exploded = df_keluhan.explode("Keluhan_Hardware")

        # Menghitung frekuensi setiap keluhan
        df_count = df_exploded["Keluhan_Hardware"].value_counts().reset_index()
        df_count.columns = ["Jenis Kerusakan", "Jumlah Kasus"]

        # Memisahkan keluhan "Tidak Ada Keluhan" agar fokus pada kerusakan saja
        df_kerusakan = df_count[df_count["Jenis Kerusakan"] != "Tidak Ada Keluhan"]

        fig_keluhan = px.bar(
            df_kerusakan,
            x="Jenis Kerusakan",
            y="Jumlah Kasus",
            color="Jenis Kerusakan",
            text_auto=True,
            color_discrete_sequence=px.colors.sequential.Reds_r,
        )
        fig_keluhan.update_layout(showlegend=False)
        st.plotly_chart(fig_keluhan, use_container_width=True)
    except Exception as e:
        st.warning(
            f"Sistem sedang memproses format data keluhan hardware... (Error log: {e})"
        )

    st.markdown("---")

    # 3. AUDIT DATA MENTAH (FULL DATAMART)
    st.subheader("🗄️ Audit Data Mentah (Datamart Penuh)")
    st.write(
        "Fasilitas pencarian dan pencocokan data asli untuk keperluan investigasi lanjutan."
    )
    st.dataframe(df, use_container_width=True)
