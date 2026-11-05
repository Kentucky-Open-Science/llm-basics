import configparser
import json
import sys

import httpx

# Load the configured LLM endpoint from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
api_base = config.get('API', 'openai_api_base').rstrip('/')
api_key = config.get('API', 'openai_api_key')

# Decision model that supports the decisions endpoints on the configured server
# (override with [MODELS] decisions in config.ini)
model = config.get('MODELS', 'decisions', fallback='bespokelabs/Bespoke-Nimble-9B')

# The text to judge, shared by every question
state = (
    "I was charged twice for my subscription this month. "
    "Please refund one of the charges. The service itself works fine."
)

# Nimble / TypeSafe System One request body (POST {base}/v1/systemone)
systemone_payload = {
    "model": model,
    "state": state,
    "questions": {
        "requests_refund": {
            "type": "noul",
            "instructions": "Does the customer ask for a refund?",
        },
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this request?",
            "criteria": {
                "billing": "Charges, payments and refunds",
                "technical": "Software bugs and outages",
                "other": "Requests outside these categories",
            },
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this request?",
            "criteria": [
                "Routine request; the service works",
                "Some functionality is unavailable",
                "Complete service outage",
            ],
        },
    },
}

# OpenAI Decisions API request body (POST {base}/v1/decisions)
decisions_payload = {
    "model": model,
    "input": state,
    "questions": [
        {
            "type": "predicate",
            "name": "requests_refund",
            "instructions": "Does the customer ask for a refund?",
        },
        {
            "type": "choice",
            "name": "department",
            "instructions": "Which department should handle this request?",
            "choices": [
                {"value": "billing", "description": "Charges, payments and refunds"},
                {"value": "technical", "description": "Software bugs and outages"},
                {"value": "other", "description": "Requests outside these categories"},
            ],
        },
        {
            "type": "score",
            "name": "urgency",
            "instructions": "How urgent is this request?",
            "levels": [
                {"label": "0", "description": "Routine request; the service works"},
                {"label": "1", "description": "Some functionality is unavailable"},
                {"label": "2", "description": "Complete service outage"},
            ],
        },
    ],
}


def api_path(suffix):
    """Join the configured base URL with an API path, adding /v1 if needed"""
    if api_base.endswith('/v1'):
        return api_base + suffix
    return api_base + '/v1' + suffix


def post(name, url, payload):
    """POST one decisions-style request; returns the response JSON or None on failure"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    print(f"[{name}] POST {url}")
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=120)
    except httpx.HTTPError as error:
        print(f"[{name}] FAIL: request error: {error}")
        return None
    if response.status_code >= 400:
        print(f"[{name}] FAIL: HTTP {response.status_code}: {response.text[:300]}")
        return None
    data = response.json()
    print(f"[{name}] PASS")
    print(json.dumps(data, indent=2))
    return data


def test_systemone():
    """Test the Nimble / TypeSafe System One endpoint"""
    data = post('systemone', api_path('/systemone'), systemone_payload)
    if data is None:
        return False
    answers = data.get("answers", {})
    print("Answers:")
    for name, answer in answers.items():
        kind = answer.get("type")
        if kind == "noul":
            print(f"  {name} (noul): {answer.get('noul')}")
        elif kind == "choice":
            print(f"  {name} (choice): {answer.get('choice')} "
                  f"(confidence: {answer.get('confidence')})")
        elif kind == "score":
            print(f"  {name} (score): {answer.get('score')} "
                  f"(confidence: {answer.get('confidence')})")
        else:
            print(f"  {name}: {answer}")
    return True


def test_decisions():
    """Test the OpenAI Decisions API endpoint"""
    data = post('decisions', api_path('/decisions'), decisions_payload)
    if data is None:
        return False
    answers = data.get("answers", [])
    if not answers:
        print("Answers: none returned")
        return False
    print("Answers:")
    for answer in answers:
        kind = answer.get("type")
        if kind == "predicate":
            print(f"  {answer.get('name')} (predicate): {answer.get('probability')}")
        elif kind == "choice":
            print(f"  {answer.get('name')} (choice): {answer.get('choice')} "
                  f"(confidence: {answer.get('confidence')})")
        elif kind == "score":
            print(f"  {answer.get('name')} (score): {answer.get('score')} "
                  f"(confidence: {answer.get('confidence')})")
        else:
            print(f"  {answer.get('name')}: {answer}")
    return True


def test():
    """Probe both decisions-style endpoints on the configured server"""
    systemone_ok = test_systemone()
    print()
    decisions_ok = test_decisions()
    print()
    if systemone_ok or decisions_ok:
        print("Decisions endpoint works.")
        return 0
    print("Decisions endpoint does not work on this server: "
          "neither /v1/systemone nor /v1/decisions accepted a request.")
    return 1


if __name__ == '__main__':
    sys.exit(test())
