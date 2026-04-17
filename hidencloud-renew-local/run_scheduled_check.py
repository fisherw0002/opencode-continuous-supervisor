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

    lowered = output.lower()
    invalid_cookie = (
        any(x in output for x in ['登录失败', '未登录', '请重新登录'])
        or ('cookie' in lowered and ('失效' in output or 'invalid' in lowered or 'expired' in lowered))
    )
    renewed = ('续期成功' in output) or ('renew success' in lowered)
    logged_in = '登录成功' in output
    target_seen = '处理服务 ID: 207229' in output
    not_due = ('未到续期时间' in output) or ('低于' in output and '1 天' in output) or ('days_until=' in lowered and 'threshold=' in lowered)

    if invalid_cookie:
        status = 'COOKIE_INVALID'
        action_needed = 'cookie 可能失效，需要你手动走一次 VNC 登录，然后运行 reseed_cookie_from_vnc.sh 重新播种。'
    elif renewed:
        status = 'RENEWED'
        action_needed = 'none'
    elif logged_in and target_seen and not_due:
        status = 'NOT_DUE'
        action_needed = 'none'
    elif logged_in and target_seen:
        status = 'OK'
        action_needed = 'none'
    else:
        status = 'ERROR'
        action_needed = 'check recent_output and full_log'

    summary = [
        f'time: {ts}',
        f'status: {status}',
        f'exit_code: {p.returncode}',
        f'cookie_cache_file: {CACHE_FILE}',
        f'cookie_cache_exists: {CACHE_FILE.exists()}',
        '',
        'signals:',
        f'- logged_in: {logged_in}',
        f'- target_service_seen: {target_seen}',
        f'- renewed: {renewed}',
        f'- not_due: {not_due}',
        f'- invalid_cookie: {invalid_cookie}',
        '',
        'recent_output:',
        tail,
        '',
        f'action_needed: {action_needed}',
        '',
        f'full_log: {RUN_LOG}',
    ]
    SUMMARY.write_text('\n'.join(summary), encoding='utf-8')
    print(SUMMARY)


if __name__ == '__main__':
    main()
