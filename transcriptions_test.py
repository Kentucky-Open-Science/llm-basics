from openai import OpenAI
import configparser
import sys

# Model output can contain characters the console can't display
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load configuration from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
openai_api_base = config.get('API', 'openai_api_base')
openai_api_key = config.get('API', 'openai_api_key')

# Initialize OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Model IDs are provider-specific; set them in the [MODELS] section of config.ini
model = config.get('MODELS', 'transcription', fallback='')
if not model:
    raise SystemExit("Set [MODELS] transcription in config.ini (see config.ini.example)")

def test():
    """
    Transcribe an audio file to text using the Whisper model
    """
    # Open the audio file in binary read mode
    audio_file = open("fitnessgram.mp3", "rb")
    
    # Call the transcriptions endpoint to convert speech to text
    transcription = client.audio.transcriptions.create(
        model=model,  # Speech-to-text model
        file=audio_file,
    )
    
    # Print the transcription result
    print("Transcription result:")
    print(transcription)

if __name__ == '__main__':
    test()