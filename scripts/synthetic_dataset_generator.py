# ==============================================================================
# SCRIPT UTILITY: GENERATOR DATA SINTETIK
# Digunakan HANYA untuk keperluan demonstrasi dan pengujian UI (Staging).
# JANGAN JALANKAN SCRIPT INI DI DATABASE PRODUCTION (DATA ASLI).
# ==============================================================================

import pandas as pd
import random
import numpy as np

print("Membuat 300 Data Tiruan (Format Identik dengan NLP)...")

# Opsi Variabel Sesuai Skema
kategori_adl = [
    ["Pekerjaan/Ekonomi"],
    ["Domestik/Rumah Tangga"],
    ["Sosial/Komunitas"],
    ["Pasif/Hanya Dipakai"],
    ["Pekerjaan/Ekonomi", "Domestik/Rumah Tangga"],
]
status_util = ["Sangat Berguna", "Cukup Berguna", "Terkendala", "Tidak Berguna"]
sentimen = ["Positif", "Netral", "Negatif"]
keluhan = [
    ["Tidak Ada Keluhan"],
    ["Tali kendor"],
    ["Baterai drop"],
    ["Motor macet"],
    ["Soket longgar", "Tali kendor"],
]
urgensi = ["Rendah", "Sedang", "Tinggi"]

data_dummy = []

for i in range(300):
    keluhan_terpilih = random.choice(keluhan)
    urgensi_terpilih = (
        "Tinggi" if "Motor macet" in keluhan_terpilih else random.choice(urgensi)
    )

    # 20% probabilitas Durasi_Pakai kosong (NaN) meniru data asli Taufan/Daffa
    durasi = round(random.uniform(0.5, 10.0), 1) if random.random() > 0.2 else np.nan

    # Struktur Dictionary DIURUTKAN PERSIS seperti output OpenAI-mu
    row = {
        "Durasi_Pakai_Jam": durasi,
        "Kategori_Aktivitas_ADL": random.choice(kategori_adl),
        "Status_Utilitas": random.choice(status_util),
        "Sentimen_Laporan": random.choice(sentimen),
        "Keluhan_Hardware": keluhan_terpilih,
        "Kutipan_Asli": "Alat ini sangat membantu saya sehari-hari, meski kadang harus disesuaikan.",
        "Tingkat_Urgensi_Pemeliharaan": urgensi_terpilih,
        "ID_Pasien": f"P-{random.randint(100, 999)}",
    }
    data_dummy.append(row)

# Jadikan DataFrame
df_dummy = pd.DataFrame(data_dummy)

# Simpan ke CSV
df_dummy.to_csv("data/karla_synthetic_data_300.csv", index=False)

print("Selesai! Skema kini 100% identik.")
print(df_dummy.head(3))
