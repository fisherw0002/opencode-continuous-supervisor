#!/usr/bin/env python3
"""G2A image generation - auto-detects the best available image model from /v1/models."""
import os, json, base64, sys
from urllib import request, error

BASE = os.environ.get('G2A_BASE_URL') or os.environ.get('G2AD_BASE_URL') or 'https://g2a.fisht.cc.cd/v1'
API_KEY = os.environ.get('G2A_API_KEY') or os.environ.get('G2AD_API_KEY')
if not API_KEY:
    print('NO_G2A_API_KEY', file=sys.stderr)
    sys.exit(2)

prompt = os.environ.get('G2A_PROMPT')
if not prompt:
    print('NO_G2A_PROMPT', file=sys.stderr)
    sys.exit(3)

size = os.environ.get('G2A_SIZE', '1024x1024')
PREFERRED_IMAGE_MODELS = [
    'grok-imagine-image-lite',
    'grok-imagine-image',
    'grok-imagine-1.0',
]


def api_json(method, path, payload=None, timeout=180):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = request.Request(
        BASE + path,
        data=data,
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'User-Agent': 'curl/8.5',
        },
        method=method,
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8', errors='replace'))
    except error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(body, file=sys.stderr)
        raise SystemExit(f'HTTP {e.code}: {body[:1200]}')


def detect_image_model():
    explicit = os.environ.get('G2A_IMAGE_MODEL')
    if explicit:
        return explicit
    models = api_json('GET', '/models', timeout=60).get('data') or []
    ids = [m.get('id') for m in models if m.get('id')]
    for preferred in PREFERRED_IMAGE_MODELS:
        if preferred in ids:
            return preferred
    for mid in ids:
        low = mid.lower()
        if 'image' in low and 'video' not in low and 'edit' not in low:
            return mid
    raise SystemExit(f'NO_G2A_IMAGE_MODEL_AVAILABLE: {ids}')


model = detect_image_model()
payload = {
    'model': model,
    'prompt': prompt,
    'n': 1,
    'size': size,
    'response_format': 'b64_json',
}

j = api_json('POST', '/images/generations', payload)
if 'error' in j:
    raise SystemExit(f"API error: {j['error']}")

data = j.get('data') or []
if not data:
    raise SystemExit(f'no data in response: {j}')

b64 = data[0].get('b64_json')
if not b64:
    raise SystemExit(f'no b64_json in response: {j}')

blob = base64.b64decode(b64)
if blob[:2] == b'\xff\xd8':
    ext = 'jpg'
elif blob[:8] == b'\x89PNG\r\n\x1a\n':
    ext = 'png'
else:
    ext = 'img'

os.makedirs('/root/g2a_out', exist_ok=True)
out = f'/root/g2a_out/p_{os.getpid()}.{ext}'
with open(out, 'wb') as f:
    f.write(blob)

print(out)
