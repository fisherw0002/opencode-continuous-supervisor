const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, args:['--no-sandbox'] });
  const ctx = await browser.newContext({
    ignoreHTTPSErrors: true,
    httpCredentials: { username: 'ocadmin', password: 'T5w!2nQp9Kx7mV4' },
    viewport: { width: 1600, height: 1000 }
  });

  const backendAuth = 'Basic ' + Buffer.from('opencode:t4hFNBdWxQI/Mv+z+barnwi1').toString('base64');
  await ctx.setExtraHTTPHeaders({ Authorization: backendAuth });

  const page = await ctx.newPage();

  page.on('response', async (resp) => {
    try {
      const url = resp.url();
      if (/provider|config|session|project|model/i.test(url)) {
        const ct = resp.headers()['content-type'] || '';
        if (ct.includes('application/json')) {
          const txt = await resp.text();
          console.log('\n=== RESPONSE', resp.status(), url, '===');
          console.log(txt.slice(0, 5000));
        } else {
          console.log('\n=== RESPONSE', resp.status(), url, 'CT=' + ct + ' ===');
        }
      }
    } catch (e) {
      console.log('RESP_ERR', String(e));
    }
  });

  await page.goto('https://oc.fisht.de5.net', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/root/.openclaw/workspace/oc_front_1_home.png', fullPage: true });

  const openBtn = page.getByRole('button', { name: /Open project/i }).first();
  if (await openBtn.count()) await openBtn.click().catch(()=>{});
  await page.waitForTimeout(1500);

  const wsButton = page.getByRole('button', { name: /\.openclaw\/workspace/i }).first();
  if (await wsButton.count()) {
    await wsButton.click().catch(()=>{});
  } else {
    const anyWorkspace = page.locator('text=/workspace/i').first();
    if (await anyWorkspace.count()) await anyWorkspace.click().catch(()=>{});
  }
  await page.waitForTimeout(6000);
  await page.screenshot({ path: '/root/.openclaw/workspace/oc_front_2_workspace.png', fullPage: true });

  const texts = await page.locator('body').innerText().catch(()=> '');
  console.log('\n=== BODY TEXT PREVIEW ===\n' + texts.slice(0, 4000));

  const candidates = [
    page.getByRole('button', { name: /model/i }).first(),
    page.locator('[data-slot*=model], [data-component*=model], button:has-text("GPT"), button:has-text("Claude"), button:has-text("99dun")').first(),
  ];
  for (const c of candidates) {
    try {
      if (await c.count()) {
        await c.click({ timeout: 3000 }).catch(()=>{});
        break;
      }
    } catch {}
  }
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/root/.openclaw/workspace/oc_front_3_after_model_click.png', fullPage: true });

  const dom = await page.evaluate(() => {
    const vis = (el) => {
      const s = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
    };
    return [...document.querySelectorAll('body *')]
      .filter(vis)
      .map(el => ({
        tag: el.tagName,
        text: (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' '),
        role: el.getAttribute('role') || '',
        aria: el.getAttribute('aria-label') || '',
        cls: (el.className || '').toString().slice(0, 120)
      }))
      .filter(x => x.text && x.text.length < 120)
      .slice(0, 800);
  });
  console.log('\n=== VISIBLE DOM ITEMS ===');
  for (const item of dom) console.log(JSON.stringify(item));

  await browser.close();
})();
