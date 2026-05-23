#!/usr/bin/env node
/**
 * TRA Schedule Query Script
 * Usage: node query_tra.js --from "員林" --to "台北" --date "2026/05/27" --startTime "15:00" --endTime "20:00"
 * Outputs: JSON array of train results to stdout
 */

const { chromium } = require('playwright');

const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : null;
};

const FROM = get('--from') || '員林';
const TO = get('--to') || '台北';
const DATE = get('--date') || new Date().toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/');
const START_TIME = get('--startTime') || '00:00';
const END_TIME = get('--endTime') || '23:30';

(async () => {
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    await page.goto('https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime', {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });

    // Fill: from station (autocomplete)
    await page.click('#startStation');
    await page.type('#startStation', FROM, { delay: 120 });
    await page.waitForTimeout(1200);
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(400);

    // Fill: to station (autocomplete)
    await page.click('#endStation');
    await page.type('#endStation', TO, { delay: 120 });
    await page.waitForTimeout(1200);
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(400);

    // Fill date and time range
    await page.fill('#rideDate', DATE);
    await page.selectOption('#startTime', START_TIME);
    await page.selectOption('#endTime', END_TIME);

    // Submit form
    await Promise.all([
      page.waitForURL('**/querybytime', { timeout: 15000 }).catch(() => {}),
      page.click('input[name="query"]'),
    ]);
    await page.waitForTimeout(3000);

    const html = await page.content();

    // Parse results from <tbody> blocks
    const trains = parseTrains(html);

    console.log(JSON.stringify({ ok: true, from: FROM, to: TO, date: DATE, trains }, null, 2));
  } catch (err) {
    console.log(JSON.stringify({ ok: false, error: err.message }));
  } finally {
    if (browser) await browser.close();
  }
})();

function parseTrains(html) {
  const strip = (s) => s.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

  // Main summary rows: <tr class="trip-column ..."> contains type, no, times, price
  const mainRowRe = /<tr[^>]*class="[^"]*trip-column[^"]*"[\s\S]*?<\/tr>/g;
  const mainRows = [];
  let mr;
  while ((mr = mainRowRe.exec(html)) !== null) {
    const text = strip(mr[0]);
    const typeAndNo = text.match(/(自強\(3000\)|自強|莒光|普悠瑪|太魯閣|區間快|區間)\s+(\d{3,4})/);
    const times = text.match(/(\d{2}:\d{2})\s+(\d{2}:\d{2})/);
    const duration = text.match(/(\d+)\s*小時\s*(\d+)\s*分/);
    const via = text.match(/(山線|海線|內灣線|六家線)/);
    const price = mr[0].match(/<span[^>]*>\s*\$\s*(\d{3,4})\s*<\/span>/);
    mainRows.push({
      type: typeAndNo ? typeAndNo[1] : '未知',
      no: typeAndNo ? typeAndNo[2] : '',
      depart: times ? times[1] : '',
      arrive: times ? times[2] : '',
      duration: duration ? `${duration[1]}h${duration[2]}m` : '',
      via: via ? via[1] : '',
      price: price ? `$${price[1]}` : '',
    });
  }

  // Detail tbodies: extract remarks (週末停駛, 親子車廂, etc.)
  const remarkMap = {};
  const tbodyRe = /<tbody[\s\S]*?<\/tbody>/g;
  let tb;
  while ((tb = tbodyRe.exec(html)) !== null) {
    const text = strip(tb[0]);
    const noMatch = text.match(/(自強\(3000\)|自強|莒光|普悠瑪|太魯閣|區間快|區間)\s+(\d{3,4})/);
    if (!noMatch) continue;
    const no = noMatch[2];
    const weekendMatch = text.match(/(逢週[六日及例假日]+停駛)/);
    const childMatch = text.match(/(親子車廂)/);
    remarkMap[no] = weekendMatch ? weekendMatch[1] : (childMatch ? '含親子車廂' : '');
  }

  return mainRows.map(r => ({ ...r, remark: remarkMap[r.no] || '' }));
}
