# LLM Basics

Simple, self-contained examples showing how to use an OpenAI-compatible API for various AI tasks. The scripts work with OpenAI directly or any other OpenAI-compatible endpoint (vLLM, LLM Factory, etc.) — just point `config.ini` at your server and pick your model IDs.

## Setup Instructions

1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `config.ini.example` to `config.ini`
3. Add your API key to the `[API]` section (LLM Factory keys are issued at https://llm-factory.ai.uky.edu/api-keys)
4. The `[MODELS]` section ships with the models currently served by the example LLM Factory endpoint (`https://api-llm-factory.ai.uky.edu/v1`). Using a different OpenAI-compatible server? Update the base URL and model IDs — run `python test_models_endpoint.py` to list what it offers (each entry includes a `task` field indicating what the model is for).

## Example Scripts

* `chat_completions_test.py` - Chat with a language model
* `stream_test.py` - Stream chat responses token by token
* `tools_test.py` - Use tool-augmented language models (function calling)
* `vision_test.py` - Process images with multimodal models
* `embeddings_test.py` - Create vector embeddings from text
* `simple_rag.py` - Implement a basic RAG (Retrieval-Augmented Generation) system with FAISS
* `transcriptions_test.py` - Generate transcriptions from audio files (uses the included `fitnessgram.mp3` sample)
* `test_tts.py` - Generate speech from text (writes `test_<voice>.mp3` files)
* `test_models_endpoint.py` - List the models available on the configured server
* `decisions_test.py` - Probe the decisions endpoints (`/v1/systemone` Nimble / TypeSafe System One and `/v1/decisions` OpenAI Decisions format) and report whether they work on the configured server
* `quota_test.py` - Probe rate-limit/quota behavior (HTTP 429s, `Retry-After` and `X-RateLimit` headers, `/quotas/me`) if your server implements it

Run each script after configuring to test different capabilities of the API.
