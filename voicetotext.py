import whisper
import os
import ffmpeg
import os

# Cargar el modelo Whisper Tiny una sola vez
# os.environ["PATH"] += os.pathsep + "F:\\Users\\Jose\\Documents\\binaries"
model = whisper.load_model("small", download_root="./models")

def convert_audio_to_wav(audio_path: str) -> str:
    """Convierte un archivo de audio a WAV con 16kHz si no está en el formato correcto."""
    wav_path = "./temp_audio.wav"
    
    try:
        # Reconvertir el audio a 16kHz WAV (necesario para Whisper en algunos casos)
        ffmpeg.input(audio_path).output(wav_path, format="wav", ar="16k").run(overwrite_output=True, quiet=True)
        return wav_path
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

def transcribe(audio_path: str) -> str:
    """Transcribe un audio a texto usando Whisper."""
    # Convertir audio si es necesario
    if not audio_path.endswith(".wav"):
        audio_path = convert_audio_to_wav(audio_path)

    if not audio_path:
        return "Error processing audio file."

    try:
        # Transcribir usando Whisper
        result = model.transcribe(audio_path)
        transcription = result["text"]
        
        # Eliminar archivo temporal después de transcribir
        os.remove(audio_path)

        return transcription
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return "Error during transcription."