from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

TARGET_URL = "https://dash.hidencloud.com/service/207229/manage"
ARTIFACTS = Path("/root/.openclaw/workspace/playwright-python/artifacts/hidencloud-renew-2026-04-19")
LOG = ARTIFACTS / "run.log"
EPHY_BIN = "/usr/bin/epiphany-browser"
DISPLAY = ":1"
TMP_SHOT = ARTIFACTS / ".tmp-screen.png"
TMP_TXT = ARTIFACTS / ".tmp-ocr"

RENEW_X = 1058
RENEW_Y = 367
STATE_TIMEOUT = 180
POLL_INTERVAL = 3

PAGE_READY_NEEDLES = [
    'Free Server #207229',
    'Due date',
    'Renew',
    'Delete',
]
POPUP_NEEDLES = [
    'Renewal Restricted',
    'less than 1 day left',
]


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


def ocr_screen_text() -> str:
    run(f"export DISPLAY={DISPLAY}; scrot '{TMP_SHOT}'", check=True)
    run(f"tesseract '{TMP_SHOT}' '{TMP_TXT}' >/dev/null 2>&1", check=True)
    txt_path = TMP_TXT.with_suffix('.txt')
    if txt_path.exists():
        return txt_path.read_text(encoding='utf-8', errors='ignore')
    return ''


def wait_for_ocr(needles: list[str], timeout: int, label: str) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        text = ocr_screen_text()
        if all(n.lower() in text.lower() for n in needles):
            log(f'ocr_ready={label}')
            return True
        time.sleep(POLL_INTERVAL)
    log(f'ocr_timeout={label}')
    return False


def launch_browser():
    run("pkill -f 'epiphany-browser' || true")
    time.sleep(1)
    run(f"export DISPLAY={DISPLAY}; nohup {EPHY_BIN} --new-window '{TARGET_URL}' >/root/.openclaw/workspace/playwright-python/vnc/epiphany-renew.log 2>&1 &")
    time.sleep(3)


def focus_service_window():
    p = run(f"export DISPLAY={DISPLAY}; wmctrl -lx")
    lines = p.stdout.splitlines() if p.stdout else []
    chosen = None
    for line in lines:
        low = line.lower()
        if 'epiphany' in low and 'services - hidencloud' in low:
            chosen = line.split()[0]
            break
    if not chosen:
        for line in lines:
            low = line.lower()
            if 'epiphany' in low and 'hidencloud' in low and 'new tab' not in low:
                chosen = line.split()[0]
                break
    if not chosen:
        raise RuntimeError('service window not found')
    run(f"export DISPLAY={DISPLAY}; wmctrl -ia {chosen}", check=True)
    time.sleep(1)
    return chosen


def move_mouse_to_renew_only():
    focus_service_window()
    run(f"export DISPLAY={DISPLAY}; xdotool mousemove {RENEW_X} {RENEW_Y}", check=True)
    time.sleep(1)


def click_renew():
    focus_service_window()
    run(f"export DISPLAY={DISPLAY}; xdotool mousemove {RENEW_X} {RENEW_Y} click 1", check=True)
    time.sleep(1)


def main():
    ensure_dirs()
    force = '--force' in sys.argv
    log(f'start hidencloud renew once job force={force}')
    launch_browser()

    focus_service_window()
    wait_for_ocr(PAGE_READY_NEEDLES, STATE_TIMEOUT, 'target_page_ready')
    screenshot('01-target-page.png')

    move_mouse_to_renew_only()
    screenshot('02-before-renew.png')

    click_renew()
    wait_for_ocr(POPUP_NEEDLES, 30, 'renew_popup_ready')
    screenshot('03-after-renew-click.png')

    log('done')


if __name__ == '__main__':
    main()
