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
    """Send a test conversation to the chat model and print the response"""
    
    # Create a chat completion with predefined messages
    completion = client.chat.completions.create(
        model=model,
        messages=[
            # System message defines the AI assistant's behavior
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            # Simulated conversation history
            {"role": "assistant", "content": "Hello, what can I assist you with?"},
            {"role": "user", "content": "Hello, my name is john"},
            {"role": "assistant", "content": "Hello, John, what can I assist you with today?"},
            # User's current query
            {"role": "user", "content": "What is my name?"},
        ],
        # max_tokens=200,     # Maximum length of the response in tokens
        temperature=0.7,    # Controls randomness (0=deterministic, 1=creative)
    )
    
    # Print the full response
    print("Completion result:")
    print(completion)
    return completion

if __name__ == '__main__':
    test()