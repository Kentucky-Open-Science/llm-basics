"""Quota enforcement tests against the configured server.

Reads config.ini ([API] openai_api_base / openai_api_key, [MODELS] chat).

Usage:
  python quota_test.py burst [n]     # fire n rapid non-streaming requests
  python quota_test.py concurrent n  # fire n simultaneous streaming requests
  python quota_test.py single        # one request, print outcome
  python quota_test.py status        # show /quotas/me (limits + usage)

Expects quota policies to be configured for your user (via the router admin
API or a Quota Management dashboard). Prints per-request HTTP status,
error codes, Retry-After and X-RateLimit headers so enforcement can be
verified. The /quotas/me endpoint is router-specific and may not exist on
every server; the status command simply prints the HTTP status in that case.
"""

import configparser
import concurrent.futures
import json
import sys
import time

import httpx

# Server responses can contain characters the console can't display
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

config = configparser.ConfigParser()
config.read("config.ini")
BASE = config.get("API", "openai_api_base").rstrip("/")
ROOT = BASE[: BASE.rfind("/v1")] if BASE.endswith("/v1") else BASE
KEY = config.get("API", "openai_api_key")
MODEL = config.get("MODELS", "chat", fallback="")
if not MODEL:
    raise SystemExit("Set [MODELS] chat in config.ini (see config.ini.example)")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def one(timeout=90, stream=False, content="hi"):
    """Fire one chat completion; returns (status, headers, body)."""
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "stream": stream,
    }
    with httpx.Client(timeout=timeout) as client:
        if stream:
            with client.stream(
                "POST", f"{BASE}/chat/completions", headers=HEADERS, json=payload
            ) as resp:
                body = b""
                for chunk in resp.iter_raw():
                    body += chunk
                return resp.status_code, dict(resp.headers), body.decode(errors="replace")
        resp = client.post(f"{BASE}/chat/completions", headers=HEADERS, json=payload)
        return resp.status_code, dict(resp.headers), resp.text


def summarize(i, status, headers, body):
    line = f"  req {i}: HTTP {status}"
    if status == 429:
        try:
            err = json.loads(body)["error"]
            line += (
                f" code={err.get('code')}"
                f" retry_after={headers.get('retry-after')}"
                f" ratelimit_remaining={headers.get('x-ratelimit-remaining')}"
            )
        except Exception:
            line += f" body={body[:140]}"
    elif status == 200:
        try:
            usage = json.loads(body).get("usage", {})
            line += f" total_tokens={usage.get('total_tokens')}"
        except Exception:
            line += " (stream ok)"
    else:
        line += f" body={body[:140]}"
    print(line)


def burst(n):
    print(f"burst: {n} sequential non-streaming requests")
    for i in range(1, n + 1):
        s, h, b = one()
        summarize(i, s, h, b)
        time.sleep(0.2)


def parallel(n):
    print(f"parallel: {n} simultaneous streaming requests")
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
        futs = {
            pool.submit(one, 120, True, "Write a 120 word story about a lighthouse."): i
            for i in range(1, n + 1)
        }
        for fut in concurrent.futures.as_completed(futs):
            i = futs[fut]
            try:
                s, h, b = fut.result()
                summarize(i, s, h, b)
            except Exception as exc:
                print(f"  req {i}: EXCEPTION {exc}")


def single():
    print("single request:")
    s, h, b = one()
    summarize(1, s, h, b)
    time.sleep(1.5)  # let background token billing land
    status()


def status():
    with httpx.Client(timeout=15) as client:
        r = client.get(f"{ROOT}/quotas/me", headers=HEADERS)
        print(f"GET /quotas/me -> {r.status_code}")
        try:
            data = r.json()
            print(f"  subject: {data.get('subject')} (source: {data.get('source')})")
            print(f"  limits: {json.dumps(data.get('limits'))}")
            print(f"  usage:  {json.dumps(data.get('usage'))}")
        except Exception:
            print(f"  body: {r.text[:300]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if cmd == "burst":
        burst(arg or 4)
    elif cmd == "parallel":
        parallel(arg or 2)
    elif cmd == "single":
        single()
    elif cmd == "status":
        status()
    else:
        print(__doc__)
        sys.exit(1)
