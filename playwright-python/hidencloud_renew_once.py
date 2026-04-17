from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import subprocess
import time

TARGET_URL = "https://dash.hidencloud.com/service/207229/manage"
EXPECTED_DUE = "20 Apr 2026"
ARTIFACTS = Path("/root/.openclaw/workspace/playwright-python/artifacts/hidencloud-renew-2026-04-19")
LOG = ARTIFACTS / "run.log"

EPHY_BIN = "/usr/bin/epiphany-browser"
DISPLAY = ":1"


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


def screenshot(name: str):
    path = ARTIFACTS / name
    run(f"export DISPLAY={DISPLAY}; gnome-screenshot -f '{path}'", check=True)
    return path


def ensure_dirs():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    LOG.touch(exist_ok=True)


def current_session_state() -> str:
    p = Path('/root/.local/share/epiphany/session_state.xml')
    if not p.exists():
        return ''
    return p.read_text(encoding='utf-8', errors='ignore')


def due_present_in_session() -> bool:
    text = current_session_state()
    return EXPECTED_DUE in text and 'dash.hidencloud.com/service/207229/manage' in text


def restriction_present_in_session() -> bool:
    text = current_session_state().lower()
    return 'renewal restricted' in text or 'less than 1 day left' in text


def due_advanced_in_session() -> bool:
    text = current_session_state()
    # 成功后至少不应再是 20 Apr 2026；先做最稳的弱判断
    return ('dash.hidencloud.com/service/207229/manage' in text) and (EXPECTED_DUE not in text)


def launch_browser():
    run("pkill -f 'epiphany-browser' || true")
    time.sleep(1)
    run(f"export DISPLAY={DISPLAY}; nohup {EPHY_BIN} --new-window '{TARGET_URL}' >/root/.openclaw/workspace/playwright-python/vnc/epiphany-renew.log 2>&1 &")
    time.sleep(8)


def main():
    ensure_dirs()
    log('start hidencloud renew once job')

    launch_browser()
    before_img = screenshot('01-before.png')
    log(f'before_screenshot={before_img}')

    if not due_present_in_session():
        log(f'status=abort_due_mismatch expected_due={EXPECTED_DUE}')
        return

    # 这里先不盲点，留出人工/后续接入 xdotool 的位置
    # 当前交付目标：4/19 当天自动打开、截图、守门、给出是否进入可点击窗口
    if restriction_present_in_session():
        log('status=page_already_shows_restriction_or_modal')

    after_guard_img = screenshot('02-after-guard.png')
    log(f'guard_screenshot={after_guard_img}')

    if due_advanced_in_session():
        log('status=renew_success_inferred')
    else:
        log('status=ready_for_manual_or_next_click_step')


if __name__ == '__main__':
    main()
