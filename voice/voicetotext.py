import whisper
import os
import ffmpeg
from abc import ABC, abstractmethod

class VoiceToText(ABC):
    """
    Abstract base class for converting voice to text.
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        str
            Transcribed text.
        """
        pass

    def convert_audio_to_wav(self, audio_path: str) -> str:
        """
        Convert an audio file to 16kHz WAV format.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        str
            Path to the converted WAV file.
        """
        wav_path = "temp_audio.wav"
        
        try:
            ffmpeg.input(audio_path).output(wav_path, format="wav", ar="16k").run(overwrite_output=True, quiet=True)
            return wav_path
        except Exception as e:
            print(f"Error converting audio: {e}")
            return None


class WhisperVoiceToText(VoiceToText):
    """
    Implementation of VoiceToText using the Whisper model.
    """

    def __init__(self):
        """
        Initialize the Whisper model.
        """
        if not os.path.exists("voice/models"):
            os.makedirs("voice/models")
        self.model = whisper.load_model("small", download_root="voice/models")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.

        Parameters
        ----------
        audio_path : str
            Path to the audio file.

        Returns
        -------
        str
            Transcribed text or error message.
        """
        if not audio_path.endswith(".wav"):
            audio_path = self.convert_audio_to_wav(audio_path)

        if not audio_path:
            return "Error processing audio file."

        try:
            result = self.model.transcribe(audio_path)
            transcription = result["text"]
            
            os.remove(audio_path)

            return transcription
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return "Error during transcription."