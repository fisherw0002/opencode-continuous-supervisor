from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

TARGET_URL = "https://dash.hidencloud.com/service/207229/manage"
EXPECTED_DUE = "20 Apr 2026"
ARTIFACTS = Path("/root/.openclaw/workspace/playwright-python/artifacts/hidencloud-renew-2026-04-19")
LOG = ARTIFACTS / "run.log"
EPHY_BIN = "/usr/bin/epiphany-browser"
DISPLAY = ":1"
# 当前桌面 1440x900 的预估坐标；后续可继续微调
RENEW_X = 1220
RENEW_Y = 370
POST_CLICK_WAIT = 6


def log(msg: str):
    ts = datetime.now().strftime("%F %T")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: str, check: bool = False):
    log(f"$ {cmd}")
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if p.stdout:
        log("stdout: " + p.stdout.strip().replace("\n", " | "))
    if p.stderr:
        log("stderr: " + p.stderr.strip().replace("\n", " | "))
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {cmd} -> {p.returncode}")
    return p


def ensure_dirs():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    LOG.touch(exist_ok=True)


def screenshot(name: str):
    path = ARTIFACTS / name
    run(f"export DISPLAY={DISPLAY}; scrot '{path}'", check=True)
    return path


def current_session_state() -> str:
    candidates = [
        Path('/root/.local/share/epiphany/session_state.xml'),
        Path('/root/.local/share/ephy/session_state.xml'),
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding='utf-8', errors='ignore')
    return ''


def due_present_in_session() -> bool:
    text = current_session_state()
    return EXPECTED_DUE in text and 'dash.hidencloud.com/service/207229/manage' in text


def due_advanced_in_session() -> bool:
    text = current_session_state()
    return ('dash.hidencloud.com/service/207229/manage' in text) and (EXPECTED_DUE not in text)


def launch_browser():
    run("pkill -f 'epiphany-browser' || true")
    time.sleep(1)
    run(f"export DISPLAY={DISPLAY}; nohup {EPHY_BIN} --new-window '{TARGET_URL}' >/root/.openclaw/workspace/playwright-python/vnc/epiphany-renew.log 2>&1 &")
    time.sleep(10)


def focus_epiphany_window():
    p = run(f"export DISPLAY={DISPLAY}; wmctrl -lx")
    lines = p.stdout.splitlines() if p.stdout else []
    win_id = None
    for line in lines:
        if 'epiphany' in line.lower() or 'org.gnome.epiphany' in line.lower():
            win_id = line.split()[0]
            break
    if not win_id:
        raise RuntimeError('epiphany window not found')
    run(f"export DISPLAY={DISPLAY}; wmctrl -ia {win_id}", check=True)
    time.sleep(1)
    return win_id


def click_renew():
    focus_epiphany_window()
    run(f"export DISPLAY={DISPLAY}; xdotool mousemove {RENEW_X} {RENEW_Y} click 1", check=True)
    time.sleep(POST_CLICK_WAIT)


def main():
    ensure_dirs()
    force = '--force' in sys.argv
    log(f'start hidencloud renew once job force={force}')
    launch_browser()

    target_img = screenshot('01-target-page.png')
    log(f'target_page_screenshot={target_img}')

    due_ok = due_present_in_session()
    log(f'due_guard_passed={due_ok}')
    if not due_ok and not force:
        log(f'status=abort_due_mismatch expected_due={EXPECTED_DUE}')
        return

    before_img = screenshot('02-before-renew.png')
    log(f'before_renew_screenshot={before_img}')

    click_renew()

    after_img = screenshot('03-after-renew-click.png')
    log(f'after_renew_click_screenshot={after_img}')

    if due_advanced_in_session():
        log('status=renew_success_inferred')
    else:
        log('status=renew_result_unknown_or_not_yet_changed')

    log('done')


if __name__ == '__main__':
    main()
