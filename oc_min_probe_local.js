const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args:['--no-sandbox'] });
  const ctx = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 960 }
  });
  const page = await ctx.newPage();
  const auth = 'Basic ' + Buffer.from('opencode:t4hFNBdWxQI/Mv+z+barnwi1').toString('base64');
  await page.setExtraHTTPHeaders({ Authorization: auth });
  page.on('close', ()=>console.log('EVENT page close'));
  page.on('crash', ()=>console.log('EVENT page crash'));
  page.on('console', msg => console.log('CONSOLE', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGEERROR', err.message));
  page.on('response', async resp => {
    const u=resp.url();
    if(/provider|config|project|session|model/i.test(u)) console.log('RESP', resp.status(), u);
  });
  page.on('requestfailed', req => console.log('REQFAIL', req.url(), req.failure()?.errorText));
  try {
    await page.goto('http://127.0.0.1:4096', { waitUntil: 'load', timeout: 120000 });
    console.log('TITLE', await page.title());
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_1.png', fullPage:true });
    await page.waitForTimeout(5000);
    console.log('URL1', page.url());
    const txt = await page.locator('body').innerText().catch(()=> '');
    console.log('BODY1', txt.slice(0,3000));
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_2.png', fullPage:true });
    await page.waitForTimeout(10000);
    console.log('URL2', page.url());
    const txt2 = await page.locator('body').innerText().catch(()=> '');
    console.log('BODY2', txt2.slice(0,3000));
    await page.screenshot({ path:'/root/.openclaw/workspace/oc_local_3.png', fullPage:true });
  } catch (e) {
    console.log('FATAL', e && e.stack ? e.stack : String(e));
  }
  await browser.close();
})();
