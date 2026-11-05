from openai import OpenAI
import configparser

# Load configuration from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
openai_api_base = config.get('API', 'openai_api_base')
openai_api_key = config.get('API', 'openai_api_key')
# Model IDs are provider-specific; set them in the [MODELS] section of config.ini
model = config.get('MODELS', 'tts', fallback='')
if not model:
    raise SystemExit("Set [MODELS] tts in config.ini (see config.ini.example)")

# Voice names depend on the TTS model. Set [MODELS] tts_voices in config.ini
# to override (comma-separated); defaults to OpenAI's standard voices.
voices = config.get('MODELS', 'tts_voices', fallback='alloy, echo, fable, onyx, nova, shimmer')
VOICES = [v.strip() for v in voices.split(',') if v.strip()]

# Initialize OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

TEXT = "Hello World"

def test_tts():
    for voice in VOICES:
        print(f"Testing voice: {voice}...")
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=TEXT
            )
            filename = f"test_{voice}.mp3"
            response.write_to_file(filename)
            print(f"Successfully saved to {filename}")
        except Exception as e:
            print(f"Error testing voice {voice}: {e}")

if __name__ == "__main__":
    test_tts()
