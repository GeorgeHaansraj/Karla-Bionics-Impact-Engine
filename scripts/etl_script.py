# Install library firebase jika belum ada:
# !pip install firebase-admin pandas

import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

print("Memulai Proses ETL Terintegrasi (Extract, Transform, Load ke Firestore)...\n")

# ==========================================
# 1. EXTRACT (Membaca & Menumpuk Data)
# ==========================================
# A. Membaca Data Asli (Hasil AI 2023)
df_asli = pd.read_csv("data/hasil_ekstraksi_karla_2023.csv")

# B. Membaca Data Tiruan (300 Baris)
# df_sintetik = pd.read_csv("data/karla_synthetic_data_300.csv")
df_nlp = pd.read_csv("data/hasil_ekstraksi_karla_2023.csv")

# C. Menumpuk (Concatenate) kedua data secara vertikal
# ignore_index=True memastikan nomor baris (index) diurutkan ulang dari 0 sampai 300+
# df_nlp = pd.concat([df_asli, df_sintetik], ignore_index=True)

# print(f"Total data gabungan: {len(df_nlp)} baris (Data Asli + Data Sintetik).")
print(f"Total data hasil etl: {len(df_nlp)} baris (Data Asli).")

# Mensimulasikan Data Demografi (G-Form Pendaftaran)
id_unik = df_nlp["ID_Pasien"].unique()
data_demografi = []
for pid in id_unik:
    data_demografi.append(
        {
            "ID_Pasien": pid,
            "Usia": random.randint(15, 65),
            "Domisili": random.choice(
                [
                    "Jawa Barat",
                    "DKI Jakarta",
                    "Jawa Tengah",
                    "Jawa Timur",
                    "Banten",
                    "Lampung",
                ]
            ),
            "Kategori_Tuna_Daksa": random.choice(
                ["Below Elbow", "Above Elbow", "Bilateral (Keduanya)"]
            ),
        }
    )
df_demografi = pd.DataFrame(data_demografi)

# ==========================================
# 2. TRANSFORM (Penggabungan & Penyuntikan)
# ==========================================
df_datamart = pd.merge(df_nlp, df_demografi, on="ID_Pasien", how="left")


def generate_random_date():
    return (datetime.today() - timedelta(days=random.randint(1, 90))).strftime(
        "%Y-%m-%d"
    )


df_datamart.insert(
    0, "ID_Laporan", [str(uuid.uuid4())[:8] for _ in range(len(df_datamart))]
)
df_datamart.insert(
    1, "Tanggal_Lapor", [generate_random_date() for _ in range(len(df_datamart))]
)

# ==========================================
# 3. LOAD (Menyimpan Backup CSV & Push ke Firestore)
# ==========================================
# A. Simpan sebagai backup lokal (CSV)
df_datamart.to_csv("data/datamart_karla_production.csv", index=False)
print("Backup CSV berhasil dibuat.")

# B. Push ke Firestore NoSQL
print("Menghubungkan ke Google Cloud Firestore...")

# Inisialisasi Firebase (GANTI NAMA FILE JSON INI DENGAN MILIKMU)
if not firebase_admin._apps:
    cred = credentials.Certificate(
        "karla-bionics-firebase-adminsdk-fbsvc-da0c821b20.json"
    )
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Membersihkan nilai kosong (NaN) agar Firebase tidak menolaknya
df_datamart_clean = df_datamart.fillna("")
records = df_datamart_clean.to_dict(orient="records")

koleksi_nama = "laporan_dampak_karla_production"
"""
Nanti, saat Dasbor sudah selesai dan siap mempresentasikan data aslinya ke Karla,
tinggal menjalankan skrip ETL yang berisi data asli dan mengirimkannya ke koleksi bernama laporan_karla_production.
Dasbor Streamlit tinggal diarahkan ke koleksi production tersebut.
"""

berhasil_upload = 0

print(f"Mengunggah {len(records)} baris data ke koleksi Firestore '{koleksi_nama}'...")

for record in records:
    doc_id = record["ID_Laporan"]
    db.collection(koleksi_nama).document(doc_id).set(record)
    berhasil_upload += 1

print(
    f"\n✅ PROSES ETL SELESAI! {berhasil_upload} data sudah bersarang di Firestore dan siap ditarik oleh Streamlit."
)
print(df_datamart.head(3))
