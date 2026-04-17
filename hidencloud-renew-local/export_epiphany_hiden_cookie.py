from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path('/root/.local/share/epiphany/cookies.sqlite')
OUT = Path('/root/.openclaw/workspace/hidencloud-renew-local/.env.local')


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT name, value, host FROM moz_cookies WHERE host LIKE '%hidencloud.com%' ORDER BY host, name"
    ).fetchall()
    if not rows:
        raise SystemExit('No HidenCloud cookies found in Epiphany cookies.sqlite')

    # 组装成仓库使用的 HIDEN_COOKIE 字符串：name=value; name2=value2
    cookie_pairs = []
    seen = set()
    for name, value, host in rows:
        key = (name, value)
        if key in seen:
            continue
        seen.add(key)
        cookie_pairs.append(f"{name}={value}")

    hidencookie = '; '.join(cookie_pairs)
    OUT.write_text(f'HIDEN_COOKIE={hidencookie}\n', encoding='utf-8')
    print(OUT)
    print(f'cookies={len(cookie_pairs)}')


if __name__ == '__main__':
    main()
