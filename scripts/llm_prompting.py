# !pip install groq

import pandas as pd
import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

# 1. SETUP API KEY
# Membaca file .env dari root folder
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq()

# 2. BACA & BERSIHKAN DATA DARI FILE CSV
df_raw = pd.read_csv("data/Data wawancara pasca hibah 2023 - Sheet1.csv")
df_raw = df_raw.fillna("")

# 3. GABUNGKAN KOLOM PERTANYAAN
kolom_pertanyaan = [
    "Pertanyaan 1",
    "pertanyaan 2",
    "pertanyaan 3",
    "pertanyaan 4",
    "Pertanyaan 5",
    "Pertanyaan 6",
    "Pertanyaan 7",
    "Pertanyaan 8",
    "Pertanyaan 9",
    "Pertanyaan 10",
]

# Menggabungkan isinya dengan pemisah spasi
df_raw["Teks_Wawancara"] = df_raw[kolom_pertanyaan].astype(str).agg(" ".join, axis=1)

# Buat dataframe baru yang hanya berisi ID dan Teks
df = df_raw[["Nama", "Teks_Wawancara"]].copy()
df = df.rename(columns={"Nama": "ID_Pasien"})

# Hapus baris yang namanya kosong
df = df[df["ID_Pasien"] != ""]

print("Data siap diekstrak oleh AI! Berikut 2 baris pertamanya:")
print(df.head(2))


# 4. FUNGSI EKSTRAKSI NLP
def ekstrak_dampak_ke_json(teks_wawancara):
    prompt_instruksi = f"""
    Kamu adalah sistem AI Data Engineer spesialis medis. Tugasmu adalah mengekstrak metrik dampak dari wawancara pasien pengguna lengan prostetik.
    Berikan output HANYA dalam format JSON yang valid, tanpa teks awalan atau akhiran apa pun.

    Skema JSON:
    {{
      "Durasi_Pakai_Jam": (Angka float, atau null jika tidak ada),
      "Kategori_Aktivitas_ADL": (Array. Pilih dari: ["Pekerjaan/Ekonomi", "Domestik/Rumah Tangga", "Sosial/Komunitas", "Pasif/Hanya Dipakai"]),
      "Status_Utilitas": (Pilih: "Sangat Berguna", "Cukup Berguna", "Terkendala", "Tidak Berguna"),
      "Sentimen_Laporan": (Pilih: "Positif", "Netral", "Negatif"),
      "Keluhan_Hardware": (Array. Deteksi kerusakan, misal ["Tali kendor", "Baterai drop"]. Jika aman tulis ["Tidak Ada Keluhan"]),
      "Kutipan_Asli": (Satu kalimat asli yang mencerminkan dampak/keluhan),
      "Tingkat_Urgensi_Pemeliharaan": (Pilih: "Tinggi", "Sedang", "Rendah". Jika alat mati/tidak bisa dipakai, wajib "Tinggi")
    }}

    TEKS WAWANCARA:
    {teks_wawancara}
    """

    try:
        # Menggunakan Llama-3.3-70b (Model Groq yang valid dan sangat cerdas untuk instruksi JSON)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful data extraction assistant designed to output strict JSON.",
                },
                {
                    "role": "user",
                    "content": prompt_instruksi,
                },
            ],
            model="openai/gpt-oss-120b",
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        # Kita lemparkan error ke blok iterasi agar bisa ditangkap oleh sistem jeda
        raise e


# 5. ITERASI DENGAN RATE LIMIT HANDLER (Mencegah Error 429)
hasil_ekstraksi = []
print("\nMemulai proses ekstraksi menggunakan Groq API dengan Rate Limit Handler...\n")

for index, row in df.iterrows():
    print(f"Memproses Pasien: {row['ID_Pasien']}...")

    sukses = False
    percobaan = 0

    # Mencoba hingga 3 kali jika terjadi error API
    while not sukses and percobaan < 3:
        try:
            json_result = ekstrak_dampak_ke_json(row["Teks_Wawancara"])

            if json_result:
                json_result["ID_Pasien"] = row["ID_Pasien"]
                hasil_ekstraksi.append(json_result)

            sukses = True
            time.sleep(3)  # Jeda aman 3 detik antar baris agar API tidak terbebani

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                print(
                    f"  -> Rate limit tercapai! Sistem menunggu 20 detik sebelum mencoba lagi..."
                )
                time.sleep(
                    20
                )  # Jeda panjang jika token limit harian/menitan Groq habis
                percobaan += 1
            else:
                print(f"  -> Error lain: {e}")
                break  # Jika error selain limit (misal kuota habis/salah API Key), hentikan baris ini

# 6. TAMPILKAN HASIL AKHIR
df_final = pd.DataFrame(hasil_ekstraksi)
print("\n=== HASIL EKSTRAKSI (SIAP DIMASUKKAN KE DATAMART) ===")
print(df_final)

# Menyimpan hasil akhir ke file CSV dan JSON untuk backup
df_final.to_csv("data/hasil_ekstraksi_karla_2023.csv", index=False)
df_final.to_json("hasil_ekstraksi_karla_2023.json", orient="records", indent=4)
print("Data berhasil diamankan ke dalam file lokal!")
