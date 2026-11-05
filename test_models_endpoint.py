from openai import OpenAI
import configparser

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

# List the model IDs available on the configured server.
# Useful for finding the right values for the [MODELS] section of config.ini.
models = client.models.list()

for m in models.data:
    print(m.id)
