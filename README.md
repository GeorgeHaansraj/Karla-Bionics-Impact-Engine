# 🦾 Karla Impact Intelligence Engine

**Karla Impact Intelligence Engine** adalah sistem otomatisasi pelaporan CSR berbasis _Artificial Intelligence_ dan pemrosesan data (ETL) yang dirancang khusus untuk **Karla Bionics**.

Proyek ini dikembangkan sebagai luaran Kerja Praktik oleh George Haansraj (Program Studi Informatika, Institut Teknologi Sumatera) untuk menggantikan alur pelaporan dampak sosial manual menjadi ekosistem digital yang interaktif dan _real-time_. Sistem ini mengekstraksi data pendaftaran dari Google Forms, memvisualisasikan metrik dampak sosial pengguna tangan prostetik (seperti jam produktif dan utilitas), dan memanfaatkan _Generative LLM_ untuk merangkai narasi laporan secara dinamis.

## 🔒 Pemberitahuan Kerahasiaan (Confidentiality Notice)

Repositori ini berfungsi sebagai portofolio teknis dan arsip cetak biru arsitektur. Karena proyek ini dikembangkan secara eksklusif untuk kepentingan operasional Karla Bionics:

- **Data Pasien & Kredensial:** Seluruh data riil pasien (CSV/JSON) dan kunci akses rahasia (API Key AI & Firebase Service Account) **tidak dipublikasikan** di repositori ini demi mematuhi regulasi privasi data.
- **Akses Operasional:** Bagi teknisi penerus atau _developer_ Karla Bionics, _file_ `.env` asli dan `karla-bionics-firebase-adminsdk.json` telah diserahkan secara privat (Out-of-Band). Silakan hubungi pemilik repositori jika memerlukan akses kredensial untuk pengembangan lanjutan.

## 📸 Antarmuka Sistem (Screenshots)

_(Tambahkan tangkapan layar Dasbor Publik Streamlit di sini)_

> `[Gambar 1: Tampilan Utama Dashboard Streamlit dengan Metrik Agregat]`

_(Tambahkan tangkapan layar Dokumentasi API FastAPI)_

> `[Gambar 2: Tampilan Swagger UI pada localhost:8000/docs]`

## 🚀 Fitur Utama

1.  **Automated ETL Pipeline:** Ekstraksi data otomatis menggunakan Pandas untuk membersihkan dan menstandarisasi data mentah sebelum dikirim ke Google Cloud Firestore.
2.  **Dual-Environment Datamart:** Pemisahan _database_ menjadi koleksi `staging` (untuk simulasi/UI testing) dan `production` (data riil) melalui konfigurasi _environment variables_.
3.  **Decoupled API Backend (FastAPI):** Endpoint RESTful berkecepatan tinggi yang menyuplai data metrik (_JSON format_) untuk diintegrasikan ke _website_ utama Karla Bionics.
4.  **Generative AI Storytelling:** Integrasi LLM (via OpenAI/Groq API) untuk menghasilkan narasi pelaporan CSR tingkat eksekutif secara otomatis berdasarkan perubahan data terbaru.
5.  **Interactive Dashboard (Streamlit):** Antarmuka visual analitik untuk memonitor metrik sebaran demografi dan tingkat utilitas tangan prostetik.

## 🛠️ Arsitektur & Teknologi

- **Bahasa Pemrograman:** Python 3.x
- **Backend & API:** FastAPI, Uvicorn
- **Data Processing:** Pandas, UUID
- **Database:** Google Cloud Firestore (NoSQL)
- **Frontend/Dashboard:** Streamlit
- **AI Integration:** OpenAI Python SDK / Groq

## ⚙️ Panduan Instalasi (Setup & Installation)

**1. Kloning Repositori**

Bash

```
git clone https://github.com/username/karla-impact-intelligence-engine.git
cd karla-impact-intelligence-engine

```

**2. Siapkan Virtual Environment** Sangat disarankan menggunakan _virtual environment_ agar dependensi terisolasi.

Bash

```
python -m venv karla-venv
# Untuk Windows:
karla-venv\Scripts\activate
# Untuk Mac/Linux:
source karla-venv/bin/activate

```

**3. Instalasi Dependensi**

Bash

```
python -m pip install -r requirements.txt

```

**4. Konfigurasi Environment Variables** Duplikasi _file_ `.env.example` dan ubah namanya menjadi `.env`. Masukkan parameter nama koleksi Firestore dan API Key yang valid (dapatkan kunci ini secara privat).

Plaintext

```
GROQ_API_KEY=masukkan_api_key_di_sini
FIRESTORE_COLLECTION_NAME=laporan_karla_staging

```

_Pastikan file JSON kredensial Firebase diletakkan di root folder sesuai instruksi serah terima._

## 💻 Cara Penggunaan (Usage)

Sistem ini memiliki dua komponen utama yang bisa dijalankan secara paralel.

**A. Menjalankan API Server (FastAPI)** Untuk menghidupkan _endpoint_ yang akan melayani _frontend web_:

Bash

```
python -m uvicorn api:app --reload

```

- Akses dokumentasi interaktif (Swagger UI): `http://localhost:8000/docs`
- _Endpoint_ Metrik Publik: `GET /api/v1/metrics/public`
- _Endpoint_ Generator Narasi AI: `POST /api/v1/generate-narrative`

**B. Menjalankan Dashboard Analitik (Streamlit)** Untuk memonitor data dan mencetak Laporan CSR (PDF):

Bash

```
streamlit run app.py

```

- Dasbor akan terbuka otomatis di _browser_ pada alamat `http://localhost:8501`.

## 📝 Kontribusi & Lisensi

Sistem ini bersifat hak milik (_proprietary_) dan dikembangkan khusus sebagai infrastruktur internal Karla Bionics. Repositori ini bersifat tertutup untuk kontribusi publik (_open-source contribution_). Segala bentuk modifikasi, penggunaan komersial, dan distribusi aset intelektual di dalam repositori ini harus melalui persetujuan manajemen Karla Bionics.
