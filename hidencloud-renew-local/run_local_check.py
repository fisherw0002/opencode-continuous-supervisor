from __future__ import annotations

import os
import subprocess
from pathlib import Path

BASE = Path('/root/.openclaw/workspace/hidencloud-renew-local')
ENV_FILE = BASE / '.env.local'
MAIN = BASE / 'main.py'
LOG = BASE / 'latest-run.log'


def load_env_file(path: Path):
    env = {}
    text = path.read_text(encoding='utf-8', errors='ignore')
    for line in text.splitlines():
        if not line or line.strip().startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v
    return env


def main():
    env = os.environ.copy()
    if ENV_FILE.exists():
        env.update(load_env_file(ENV_FILE))
    with LOG.open('w', encoding='utf-8') as f:
        p = subprocess.Popen(['./.venv/bin/python', str(MAIN)], cwd=str(BASE), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        assert p.stdout is not None
        for line in p.stdout:
            print(line, end='')
            f.write(line)
        raise SystemExit(p.wait())


if __name__ == '__main__':
    main()
