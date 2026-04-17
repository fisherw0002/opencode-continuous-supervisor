from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sys
import time

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "profiles" / "hidencloud"
TARGET_URL = "https://dash.hidencloud.com/service/207229/manage"
DATE_FMT = "%d %b %Y"
TIMEZONE = timezone.utc


@dataclass
class RenewState:
    due_date: datetime.date | None
    should_renew: bool
    page_text: str


def parse_due_date(text: str):
    m = re.search(r"Due date\s*([0-9]{1,2}\s+[A-Za-z]{3}\s+[0-9]{4})", text, re.I | re.S)
    if not m:
        return None
    return datetime.strptime(m.group(1), DATE_FMT).date()


def get_state(page) -> RenewState:
    body = page.locator("body").inner_text()
    due = parse_due_date(body)
    today = datetime.now(TIMEZONE).date()
    should_renew = bool(due and today >= (due - timedelta(days=1)))
    return RenewState(due_date=due, should_renew=should_renew, page_text=body)


def click_renew(page):
    renew_btn = page.get_by_role("button", name=re.compile(r"^Renew$", re.I))
    renew_btn.click(timeout=15000)


def maybe_confirm_modal(page):
    candidates = [
        re.compile(r"confirm", re.I),
        re.compile(r"ok", re.I),
        re.compile(r"yes", re.I),
        re.compile(r"renew", re.I),
    ]
    for pattern in candidates:
        try:
            btn = page.get_by_role("button", name=pattern)
            if btn.count() > 0:
                btn.first.click(timeout=3000)
                return True
        except Exception:
            pass
    return False


def detect_restriction(page_text: str) -> bool:
    needles = [
        "renewal restricted",
        "less than 1 day left",
        "expires in",
    ]
    lowered = page_text.lower()
    return all(n in lowered for n in needles)


def main():
    dry_run = "--run" not in sys.argv
    if not PROFILE_DIR.exists():
        raise SystemExit(
            f"未找到浏览器 profile: {PROFILE_DIR}\n"
            "先准备一个可复用的已登录 profile，再运行此脚本。"
        )

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1440, "height": 900},
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        before = get_state(page)
        today = datetime.now(TIMEZONE).date()
        print(f"today_utc={today}")
        print(f"due_before={before.due_date}")
        print(f"should_renew={before.should_renew}")

        if not before.due_date:
            print("status=due_date_not_found")
            context.close()
            return

        if not before.should_renew:
            print("status=not_due_yet")
            context.close()
            return

        if dry_run:
            print("status=dry_run_ready")
            context.close()
            return

        click_renew(page)
        time.sleep(2)
        maybe_confirm_modal(page)
        time.sleep(3)

        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except PlaywrightTimeoutError:
            pass

        after = get_state(page)
        print(f"due_after={after.due_date}")

        if detect_restriction(after.page_text):
            print("status=renewal_restricted")
        elif before.due_date and after.due_date and after.due_date > before.due_date:
            print("status=renew_success")
        else:
            print("status=renew_unknown")

        context.close()


if __name__ == "__main__":
    main()
