import os
from openai import OpenAI
from dotenv import load_dotenv

# Memuat environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


def transcribe_audio_groq(audio_file_path: str) -> str:
    """
    Mentranskripsi file audio/video menjadi teks menggunakan
    Groq API (Model Whisper) yang sangat cepat.
    Mendukung format: mp3, mp4, mpeg, mpga, m4a, wav, webm.
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {audio_file_path}")

    # Inisialisasi client menggunakan API Groq (seperti di app.py)
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)

    print(f"🎙️ Mengirim {audio_file_path} ke server Groq Whisper...")

    # Membaca file dan mengirimnya ke API
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_file_path), file.read()),
            model="whisper-large-v3-turbo",  # Model turbo yang sama seperti di Colab
            language="id",  # Kunci ke bahasa Indonesia
            response_format="text",  # Langsung minta balasan berupa teks murni
        )

    print("✅ Transkripsi instan berhasil!")
    return transcription


if __name__ == "__main__":
    # Cara mengujinya:
    # Siapkan file datates.mp4 atau datates.mp3 di dalam folder data/
    sample_file = "./data/datates.mp3"

    try:
        hasil_teks = transcribe_audio_groq(sample_file)
        print("\n--- HASIL TRANSKRIPSI ---")
        print(hasil_teks)

        # Setelah ini, teks siap dimasukkan ke pipeline ekstraksi NLP kamu!

    except Exception as e:
        print(f"⚠️ Error: {e}")
