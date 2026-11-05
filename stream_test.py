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
# Model IDs are provider-specific; set them in the [MODELS] section of config.ini
model = config.get('MODELS', 'chat', fallback='')
if not model:
    raise SystemExit("Set [MODELS] chat in config.ini (see config.ini.example)")

# Initialize OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)


def test():
    """Stream a chat completion and print each chunk as it arrives"""
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say 'double bubble bath' ten times fast.",
            },
        ],
        stream=True,
    )

    for chunk in stream:
        print(chunk)
        print(chunk.choices[0].delta)
        print("****************")


if __name__ == '__main__':
    test()
