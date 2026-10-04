🦾 Karla Impact Intelligence Engine
Karla Impact Intelligence Engine adalah sistem otomatisasi pelaporan CSR berbasis Artificial Intelligence dan pemrosesan data (ETL) yang dirancang khusus untuk Karla Bionics.

Proyek ini dikembangkan sebagai luaran Kerja Praktik oleh George Haansraj (Program Studi Informatika, Institut Teknologi Sumatera) untuk menggantikan alur pelaporan dampak sosial manual menjadi ekosistem digital yang interaktif dan real-time. Sistem ini mengekstraksi data pendaftaran dari Google Forms, memvisualisasikan metrik dampak sosial pengguna tangan prostetik (seperti jam produktif dan utilitas), dan memanfaatkan Generative LLM untuk merangkai narasi laporan secara dinamis.

🔒 Pemberitahuan Kerahasiaan (Confidentiality Notice)
Repositori ini berfungsi sebagai portofolio teknis dan arsip cetak biru arsitektur. Karena proyek ini dikembangkan secara eksklusif untuk kepentingan operasional Karla Bionics:

Data Pasien & Kredensial: Seluruh data riil pasien (CSV/JSON) dan kunci akses rahasia (API Key AI & Firebase Service Account) tidak dipublikasikan di repositori ini demi mematuhi regulasi privasi data.

Akses Operasional: Bagi teknisi penerus atau developer Karla Bionics, file .env asli dan karla-bionics-firebase-adminsdk.json telah diserahkan secara privat (Out-of-Band). Silakan hubungi pemilik repositori jika memerlukan akses kredensial untuk pengembangan lanjutan.

📸 Antarmuka Sistem (Screenshots)
(Tambahkan tangkapan layar Dasbor Publik Streamlit di sini)

[Gambar 1: Tampilan Utama Dashboard Streamlit dengan Metrik Agregat]

(Tambahkan tangkapan layar Dokumentasi API FastAPI)

[Gambar 2: Tampilan Swagger UI pada localhost:8000/docs]

🚀 Fitur Utama
Automated ETL Pipeline: Ekstraksi data otomatis menggunakan Pandas untuk membersihkan dan menstandarisasi data mentah sebelum dikirim ke Google Cloud Firestore.

Dual-Environment Datamart: Pemisahan database menjadi koleksi staging (untuk simulasi/UI testing) dan production (data riil) melalui konfigurasi environment variables.

Decoupled API Backend (FastAPI): Endpoint RESTful berkecepatan tinggi yang menyuplai data metrik (JSON format) untuk diintegrasikan ke website utama Karla Bionics.

Generative AI Storytelling: Integrasi LLM (via OpenAI/Groq API) untuk menghasilkan narasi pelaporan CSR tingkat eksekutif secara otomatis berdasarkan perubahan data terbaru.

Interactive Dashboard (Streamlit): Antarmuka visual analitik untuk memonitor metrik sebaran demografi dan tingkat utilitas tangan prostetik.

🛠️ Arsitektur & Teknologi
Bahasa Pemrograman: Python 3.x

Backend & API: FastAPI, Uvicorn

Data Processing: Pandas, UUID

Database: Google Cloud Firestore (NoSQL)

Frontend/Dashboard: Streamlit

AI Integration: OpenAI Python SDK / Groq

⚙️ Panduan Instalasi (Setup & Installation)

1. Kloning Repositori

Bash

git clone https://github.com/username/karla-impact-intelligence-engine.git
cd karla-impact-intelligence-engine 2. Siapkan Virtual Environment
Sangat disarankan menggunakan virtual environment agar dependensi terisolasi.

Bash

python -m venv karla-venv

# Untuk Windows:

karla-venv\Scripts\activate

# Untuk Mac/Linux:

source karla-venv/bin/activate 3. Instalasi Dependensi

Bash

python -m pip install -r requirements.txt 4. Konfigurasi Environment Variables
Duplikasi file .env.example dan ubah namanya menjadi .env. Masukkan parameter nama koleksi Firestore dan API Key yang valid (dapatkan kunci ini secara privat).

Plaintext

GROQ_API_KEY=masukkan_api_key_di_sini
FIRESTORE_COLLECTION_NAME=laporan_karla_staging
Pastikan file JSON kredensial Firebase diletakkan di root folder sesuai instruksi serah terima.

💻 Cara Penggunaan (Usage)
Sistem ini memiliki dua komponen utama yang bisa dijalankan secara paralel.

A. Menjalankan API Server (FastAPI)
Untuk menghidupkan endpoint yang akan melayani frontend web:

Bash

python -m uvicorn api:app --reload
Akses dokumentasi interaktif (Swagger UI): http://localhost:8000/docs

Endpoint Metrik Publik: GET /api/v1/metrics/public

Endpoint Generator Narasi AI: POST /api/v1/generate-narrative

B. Menjalankan Dashboard Analitik (Streamlit)
Untuk memonitor data dan mencetak Laporan CSR (PDF):

Bash

streamlit run app.py
Dasbor akan terbuka otomatis di browser pada alamat http://localhost:8501.

📝 Kontribusi & Lisensi
Sistem ini bersifat hak milik (proprietary) dan dikembangkan khusus sebagai infrastruktur internal Karla Bionics. Repositori ini bersifat tertutup untuk kontribusi publik (open-source contribution). Segala bentuk modifikasi, penggunaan komersial, dan distribusi aset intelektual di dalam repositori ini harus melalui persetujuan manajemen Karla Bionics.
