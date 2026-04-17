from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path('/root/.openclaw/workspace/hidencloud-renew-local')
ENV_FILE = BASE / '.env.local'
LOG_DIR = BASE / 'logs'
RUN_LOG = LOG_DIR / 'scheduled-check.log'
SUMMARY = LOG_DIR / 'latest-summary.txt'
MAIN = BASE / 'main.py'
PY = BASE / '.venv/bin/python'
CACHE_FILE = BASE / 'hiden_cookies_US.json'


def load_env_file(path: Path):
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        if not line or line.strip().startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v
    return env


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    # .env.local 只作为“初始种子 cookie”来源；真正的滚动更新由上游脚本写入本地缓存文件实现
    env.update(load_env_file(ENV_FILE))

    ts = datetime.now().strftime('%F %T')
    header = f'===== HidenCloud scheduled check @ {ts} =====\n'
    with RUN_LOG.open('a', encoding='utf-8') as f:
        f.write(header)
        f.write(f'[cookie_seed_file] {ENV_FILE}\n')
        f.write(f'[cookie_cache_file] {CACHE_FILE}\n')
        f.write(f'[cookie_cache_exists] {CACHE_FILE.exists()}\n\n')

    p = subprocess.run([str(PY), str(MAIN)], cwd=str(BASE), env=env, text=True, capture_output=True)
    output = (p.stdout or '') + (p.stderr or '')

    with RUN_LOG.open('a', encoding='utf-8') as f:
        f.write(output)
        f.write(f'\n[exit_code] {p.returncode}\n\n')

    lines = [line for line in output.splitlines() if line.strip()]
    tail = '\n'.join(lines[-60:])
    invalid_cookie = any(x in output for x in [
        '登录失败',
        '未登录',
        '失效',
        '请重新登录',
        'cookie',
    ]) and p.returncode != 0

    summary = [
        f'time: {ts}',
        f'exit_code: {p.returncode}',
        f'cookie_cache_file: {CACHE_FILE}',
        f'cookie_cache_exists: {CACHE_FILE.exists()}',
        '',
        'recent_output:',
        tail,
        '',
        ('action_needed: cookie 可能失效，需要你手动走一次 VNC 登录，然后运行 export_epiphany_hiden_cookie.py 重新播种。' if invalid_cookie else 'action_needed: none'),
        '',
        f'full_log: {RUN_LOG}',
    ]
    SUMMARY.write_text('\n'.join(summary), encoding='utf-8')
    print(SUMMARY)


if __name__ == '__main__':
    main()
