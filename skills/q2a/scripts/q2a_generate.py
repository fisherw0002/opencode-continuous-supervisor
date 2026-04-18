#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = os.environ.get('Q2A_BASE_URL', 'http://38.14.196.84:3000/v1')
DEFAULT_API_KEY = os.environ.get('Q2A_API_KEY', 'sk-J0pjubVCCd359W933IxrmHFJ7nXQOIO6')
DEFAULT_IMAGE_MODEL = os.environ.get('Q2A_IMAGE_MODEL', 'Qwen3.6-Plus-image')
DEFAULT_VIDEO_MODEL = os.environ.get('Q2A_VIDEO_MODEL', 'Qwen3.6-Plus-video')


def post_json(url: str, payload: dict, api_key: str, timeout: int = 300):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8', 'replace'))


def image_to_data_uri(path: str) -> str:
    p = Path(path)
    mime = 'image/png'
    suffix = p.suffix.lower()
    if suffix in ('.jpg', '.jpeg'):
        mime = 'image/jpeg'
    elif suffix == '.webp':
        mime = 'image/webp'
    elif suffix == '.gif':
        mime = 'image/gif'
    b64 = base64.b64encode(p.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{b64}'


def extract_video_url_from_chat_response(payload: dict) -> str:
    try:
        content = payload['choices'][0]['message']['content']
    except Exception as e:
        raise RuntimeError(f'Unexpected response shape: {payload!r}') from e
    m = re.search(r'https?://[^\s<>)\]]+\.mp4\?[^\s<>)\]]+|https?://[^\s<>)\]]+\.mp4', content)
    if not m:
        m = re.search(r'https?://[^\s<>)\]]+', content)
    if not m:
        raise RuntimeError(f'No video URL found in response: {content!r}')
    return m.group(0)


def generate_image(prompt: str, size: str, response_format: str, base_url: str, api_key: str, model: str):
    payload = {
        'model': model,
        'prompt': prompt,
        'size': size,
        'response_format': response_format,
    }
    return post_json(f'{base_url}/images/generations', payload, api_key)


def generate_video(prompt: str, size: str, base_url: str, api_key: str, model: str, image_path: str | None = None):
    if image_path:
        payload = {
            'model': model,
            'chat_type': 't2v',
            'stream': False,
            'messages': [{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {'type': 'image_url', 'image_url': {'url': image_to_data_uri(image_path)}},
                ],
            }],
            'size': size,
        }
        return post_json(f'{base_url}/chat/completions', payload, api_key)
    payload = {
        'model': model,
        'prompt': prompt,
        'size': size,
    }
    return post_json(f'{base_url}/videos', payload, api_key)


def main():
    parser = argparse.ArgumentParser(description='Generate image/video via Qwen2API native endpoints.')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_img = sub.add_parser('image')
    p_img.add_argument('--prompt', required=True)
    p_img.add_argument('--size', default='1024x1536')
    p_img.add_argument('--response-format', default='url', choices=['url', 'b64_json'])
    p_img.add_argument('--base-url', default=DEFAULT_BASE_URL)
    p_img.add_argument('--api-key', default=DEFAULT_API_KEY)
    p_img.add_argument('--model', default=DEFAULT_IMAGE_MODEL)

    p_vid = sub.add_parser('video')
    p_vid.add_argument('--prompt', required=True)
    p_vid.add_argument('--size', default='1024x1792')
    p_vid.add_argument('--image', default='')
    p_vid.add_argument('--base-url', default=DEFAULT_BASE_URL)
    p_vid.add_argument('--api-key', default=DEFAULT_API_KEY)
    p_vid.add_argument('--model', default=DEFAULT_VIDEO_MODEL)

    args = parser.parse_args()

    if args.cmd == 'image':
        result = generate_image(args.prompt, args.size, args.response_format, args.base_url, args.api_key, args.model)
        print(json.dumps(result, ensure_ascii=False))
        return

    result = generate_video(args.prompt, args.size, args.base_url, args.api_key, args.model, args.image or None)
    # normalize chat-completions style response to a simple object with URL when possible
    if args.image:
        url = extract_video_url_from_chat_response(result)
        print(json.dumps({'url': url, 'raw': result}, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
