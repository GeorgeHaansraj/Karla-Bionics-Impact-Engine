from fastapi import FastAPI, HTTPException
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Memuat environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Mengambil nama koleksi dari .env. Jika tidak ada, default-nya 'laporan_karla_staging'
COLLECTION_NAME = os.getenv("FIRESTORE_COLLECTION_NAME", "laporan_karla_staging")

# Inisialisasi FastAPI
app = FastAPI(
    title="Karla Bionics Impact API",
    description="Endpoint API untuk menyuplai data ke Web Karla Bionics (React/Next.js)",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to Karla Bionics Impact API. Please visit /docs for API documentation.",
    }


# Inisialisasi Firestore
def get_db():
    if not firebase_admin._apps:
        # Mengambil nama file dari .env
        cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()


# ==============================================================
# ENDPOINT 1: MENGAMBIL METRIK DASHBOARD PUBLIK
# ==============================================================
@app.get("/api/v1/metrics/public")
def get_public_metrics():
    try:
        db = get_db()
        # CATATAN: Untuk Production, arahkan ke koleksi data riil
        docs = db.collection(COLLECTION_NAME).stream()
        data = [doc.to_dict() for doc in docs]

        if not data:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")

        df = pd.DataFrame(data)
        df["Durasi_Pakai_Jam"] = pd.to_numeric(
            df["Durasi_Pakai_Jam"], errors="coerce"
        ).fillna(0)

        # Kalkulasi Metrik (Meniru logika dari Streamlit)
        total_pasien = len(df)
        total_jam = int(df["Durasi_Pakai_Jam"].sum())
        utilitas_positif = len(
            df[df["Status_Utilitas"].isin(["Sangat Berguna", "Cukup Berguna"])]
        )

        # Mengembalikan data dalam format JSON murni
        return {
            "status": "success",
            "data": {
                "total_penerima_manfaat": total_pasien,
                "total_jam_produktif": total_jam,
                "pengguna_aktif": utilitas_positif,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================
# ENDPOINT 2: GENERATIVE STORYTELLING (MEMANGGIL GROQ)
# ==============================================================
@app.post("/api/v1/generate-narrative")
def generate_csr_narrative():
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API Key Groq tidak ditemukan di server (periksa file .env)",
        )

    try:
        # Panggil metrik dari endpoint di atas
        metrics_response = get_public_metrics()
        metrics = metrics_response["data"]

        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)

        prompt = f"""
        Tuliskan 2 paragraf narasi eksekutif untuk laporan CSR Karla Bionics.
        Data live saat ini:
        - Pasien Terbantu: {metrics['total_penerima_manfaat']} jiwa
        - Jam Produktif: {metrics['total_jam_produktif']} jam
        - Pengguna Aktif: {metrics['pengguna_aktif']} pasien
        Fokus pada kemandirian pasien dan SDG 4. Bahasa profesional.
        """

        chat_completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", messages=[{"role": "user", "content": prompt}]
        )

        return {
            "status": "success",
            "narasi": chat_completion.choices[0].message.content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
