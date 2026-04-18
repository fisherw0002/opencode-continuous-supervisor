#!/usr/bin/env python3
import os, json, base64, sys
from urllib import request

BASE = os.environ.get("G2A_BASE_URL") or os.environ.get("G2AD_BASE_URL") or "http://127.0.0.1:8011/v1"
API_KEY = os.environ.get("G2AD_API_KEY") or os.environ.get("G2A_API_KEY")
if not API_KEY:
    print("NO_G2A_API_KEY", file=sys.stderr)
    sys.exit(2)

prompt = os.environ.get("G2A_PROMPT")
if not prompt:
    print("NO_G2A_PROMPT", file=sys.stderr)
    sys.exit(3)

size = os.environ.get("G2A_SIZE", "1024x1024")
model = os.environ.get("G2A_IMAGE_MODEL", "grok-imagine-1.0")

payload = {
    "model": model,
    "prompt": prompt,
    "n": 1,
    "size": size,
    "response_format": "b64_json",
}

req = request.Request(
    BASE + "/images/generations",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "curl/8.5",
    },
    method="POST",
)

with request.urlopen(req, timeout=180) as resp:
    raw = resp.read().decode("utf-8", errors="replace")

j = json.loads(raw)
if "error" in j:
    raise SystemExit(f"API error: {j['error']}")

data = j.get("data") or []
if not data:
    raise SystemExit(f"no data in response: {j}")

b64 = data[0].get("b64_json")
if not b64:
    raise SystemExit(f"no b64_json in response: {j}")

bin = base64.b64decode(b64)
if bin[:2] == b"\xff\xd8":
    ext = "jpg"
elif bin[:8] == b"\x89PNG\r\n\x1a\n":
    ext = "png"
else:
    ext = "img"

os.makedirs("/root/g2a_out", exist_ok=True)
out = f"/root/g2a_out/p_{os.getpid()}.{ext}"
with open(out, "wb") as f:
    f.write(bin)

print(out)
