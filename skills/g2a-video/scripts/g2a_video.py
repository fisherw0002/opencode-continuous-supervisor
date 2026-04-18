#!/usr/bin/env python3
import os, json, re, sys
from urllib import request

BASE = "https://g2.fisht.cc.cd/v1"
API_KEY = os.environ.get("G2A_API_KEY")
if not API_KEY:
    print("NO_G2A_API_KEY", file=sys.stderr)
    sys.exit(2)

prompt = os.environ.get("G2A_PROMPT")
if not prompt:
    print("NO_G2A_PROMPT", file=sys.stderr)
    sys.exit(3)

aspect_ratio = os.environ.get("G2A_ASPECT", "1:1")
video_length = int(os.environ.get("G2A_LEN", "6"))
resolution = os.environ.get("G2A_RES", "HD")
preset = os.environ.get("G2A_PRESET", "normal")
model = os.environ.get("G2A_VIDEO_MODEL", "grok-imagine-1.0-video")

payload = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "stream": False,
    "video_config": {
        "aspect_ratio": aspect_ratio,
        "video_length": video_length,
        "resolution": resolution,
        "preset": preset,
    },
}

req = request.Request(
    BASE + "/chat/completions",
    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "curl/8.5",
    },
    method="POST",
)

with request.urlopen(req, timeout=240) as resp:
    raw = resp.read().decode("utf-8", errors="replace")

j = json.loads(raw)
if "error" in j:
    raise SystemExit(f"API error: {j['error']}")

choices = j.get("choices") or []
if not choices:
    raise SystemExit(f"no choices in response: {j}")

content = ((choices[0].get("message") or {}).get("content") or "")

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
    raise SystemExit("no downloadable url found in content: " + content[:600])

os.makedirs("/root/g2a_out", exist_ok=True)
out = f"/root/g2a_out/v_{os.getpid()}.mp4"

req2 = request.Request(url, headers={"User-Agent": "curl/8.5"}, method="GET")
with request.urlopen(req2, timeout=300) as resp2:
    data = resp2.read()

head = data[:64]
ok = len(head) >= 12 and head[4:8] == b"ftyp"
if not ok:
    # still store it for debugging
    out = f"/root/g2a_out/v_{os.getpid()}.bin"

with open(out, "wb") as f:
    f.write(data)

print(out)
