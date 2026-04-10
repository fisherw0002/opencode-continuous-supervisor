const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args:['--no-sandbox'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 960 } });
  const page = await ctx.newPage();
  const auth = 'Basic ' + Buffer.from('opencode:t4hFNBdWxQI/Mv+z+barnwi1').toString('base64');
  await page.setExtraHTTPHeaders({ Authorization: auth });

  page.on('console', msg => console.log('CONSOLE', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR', err.message));
  page.on('response', async resp => {
    const u=resp.url();
    if(/provider|config|project|session|model/i.test(u)) console.log('RESP', resp.status(), u);
  });

  try {
    await page.goto('http://127.0.0.1:4096', { waitUntil: 'load', timeout: 120000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_1.png', fullPage:true });

    const openBtn = page.getByRole('button', { name: /Open project/i }).first();
    if (await openBtn.count()) await openBtn.click().catch(()=>{});
    await page.waitForTimeout(1000);

    // prefer exact workspace entry
    // click the recent project entry explicitly
    const wsExact = page.locator('button:has-text("~/.openclaw/workspace")').first();
    if (await wsExact.count()) {
      await wsExact.scrollIntoViewIfNeeded().catch(()=>{});
      await wsExact.click({ timeout: 3000, force: true }).catch(()=>{});
      await wsExact.dblclick({ timeout: 3000, force: true }).catch(()=>{});
    } else {
      const ws = page.getByRole('button', { name: /\.openclaw\/workspace/i }).first();
      if (await ws.count()) {
        await ws.scrollIntoViewIfNeeded().catch(()=>{});
        await ws.click({ timeout: 3000, force: true }).catch(()=>{});
        await ws.dblclick({ timeout: 3000, force: true }).catch(()=>{});
      } else {
        const any = page.getByText('~/.openclaw/workspace').first();
        if (await any.count()) {
          await any.scrollIntoViewIfNeeded().catch(()=>{});
          await any.click({ timeout: 3000, force: true }).catch(()=>{});
          await any.dblclick({ timeout: 3000, force: true }).catch(()=>{});
        }
      }
    }

    await page.waitForTimeout(8000);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_2.png', fullPage:true });

    // try open model selector (explicit current model button)
    const modelBtn = page.locator('button:has-text("99dun · GPT-5.3 Codex")').first();
    if (await modelBtn.count()) {
      await modelBtn.scrollIntoViewIfNeeded().catch(()=>{});
      await modelBtn.click({ timeout: 3000, force: true }).catch(()=>{});
    } else {
      const candidates = [
        page.getByRole('button', { name: /model/i }).first(),
        page.locator('[data-slot*=model], [data-component*=model], button:has-text("GPT"), button:has-text("Claude"), button:has-text("99dun")').first(),
      ];
      for (const c of candidates) {
        try {
          if (await c.count()) { await c.click({ timeout: 3000 }).catch(()=>{}); break; }
        } catch {}
      }
    }
    await page.waitForTimeout(3000);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_3.png', fullPage:true });

    // incremental search: type 'r' then '3'
    await page.keyboard.type('r').catch(()=>{});
    await page.waitForTimeout(1200);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_4_r_search.png', fullPage:true });

    await page.keyboard.type('3').catch(()=>{});
    await page.waitForTimeout(1200);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_5_r3_search.png', fullPage:true });

    // attempt to click an R3 model if visible
    const r3btn = page.locator('button:has-text("R3 ·")').first();
    if (await r3btn.count()) {
      await r3btn.scrollIntoViewIfNeeded().catch(()=>{});
      await r3btn.click({ timeout: 3000, force: true }).catch(()=>{});
    }
    await page.waitForTimeout(1500);
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_6_r3_selected.png', fullPage:true });

    // scroll model list to bottom if possible
    try {
      const list = page.locator('div[role="listbox"], [data-component*=select], [data-component*=list]').first();
      if (await list.count()) {
        await list.hover();
        await page.mouse.wheel(0, 2000);
        await page.waitForTimeout(1000);
        await page.mouse.wheel(0, 2000);
        await page.waitForTimeout(1000);
      }
    } catch {}
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_ws_7_scrolled.png', fullPage:true });

    const dom = await page.evaluate(() => {
      const vis = (el) => {
        const s = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
      };
      return [...document.querySelectorAll('body *')]
        .filter(vis)
        .map(el => ({ text: (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' '), tag: el.tagName }))
        .filter(x => x.text && x.text.length < 120)
        .slice(0, 2400);
    });
    console.log('DOM_ITEMS', JSON.stringify(dom));

  } catch (e) {
    console.log('FATAL', e && e.stack ? e.stack : String(e));
  }

  await browser.close();
})();
