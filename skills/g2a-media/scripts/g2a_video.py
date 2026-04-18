#!/usr/bin/env python3
import os, json, re, sys
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

aspect_ratio = os.environ.get('G2A_ASPECT', '1:1')
video_length = int(os.environ.get('G2A_LEN', '6'))
resolution = os.environ.get('G2A_RES', 'HD')
preset = os.environ.get('G2A_PRESET', 'normal')
PREFERRED_VIDEO_MODELS = [
    'grok-imagine-video',
    'grok-imagine-1.0-video',
]


def api_json(method, path, payload=None, timeout=240):
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


def detect_video_model():
    explicit = os.environ.get('G2A_VIDEO_MODEL')
    if explicit:
        return explicit
    models = api_json('GET', '/models', timeout=60).get('data') or []
    ids = [m.get('id') for m in models if m.get('id')]
    for preferred in PREFERRED_VIDEO_MODELS:
        if preferred in ids:
            return preferred
    for mid in ids:
        if 'video' in mid.lower():
            return mid
    raise SystemExit(f'NO_G2A_VIDEO_MODEL_AVAILABLE: {ids}')


model = detect_video_model()
payload = {
    'model': model,
    'messages': [{'role': 'user', 'content': prompt}],
    'stream': False,
    'video_config': {
        'aspect_ratio': aspect_ratio,
        'video_length': video_length,
        'resolution': resolution,
        'preset': preset,
    },
}

j = api_json('POST', '/chat/completions', payload)
if 'error' in j:
    raise SystemExit(f"API error: {j['error']}")

choices = j.get('choices') or []
if not choices:
    raise SystemExit(f'no choices in response: {j}')

content = ((choices[0].get('message') or {}).get('content') or '')
url = None
m = re.search(r'href="(https?://[^"]+)"', content)
if m:
    url = m.group(1)
if not url:
    m = re.search(r"https?://[^\s\"']+\.mp4", content)
    if m:
        url = m.group(0)
if not url:
    m = re.search(r"https?://[^\s\"']+generated_video[^\s\"']*", content)
    if m:
        url = m.group(0)
if not url:
    raise SystemExit('no downloadable url found in content: ' + content[:600])

os.makedirs('/root/g2a_out', exist_ok=True)
out = f'/root/g2a_out/v_{os.getpid()}.mp4'
req2 = request.Request(url, headers={'User-Agent': 'curl/8.5'}, method='GET')
with request.urlopen(req2, timeout=300) as resp2:
    data = resp2.read()

head = data[:64]
ok = len(head) >= 12 and head[4:8] == b'ftyp'
if not ok:
    out = f'/root/g2a_out/v_{os.getpid()}.bin'
with open(out, 'wb') as f:
    f.write(data)
print(out)
