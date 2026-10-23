import { chromium } from 'playwright-core';
const out = process.argv[2];
const shots = {
  hero: 'az=-38&el=14&head=-15&dist=470',
  front: 'az=0&el=6&dist=560',
  waddle: 'az=-60&el=12&dist=500&hipL=20&hipR=20&ankL=-14&ankR=-14&tilt=-6&head=25&mood=happy&bg=%23e6f0ea&floor=%23b9cdb8',
  side: 'az=-90&el=4&dist=580',
  back: 'az=150&el=22&dist=500',
  exploded: 'explode=1&az=-45&el=18&dist=760&tz=20&bg=%23eef1f5&floor=%23cfd6de',
};
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
page.on('pageerror', e => console.error('page error', e.message));
for (const [name, q] of Object.entries(shots)) {
  await page.goto(`http://localhost:8765/index.html?${q}`);
  await page.waitForFunction('window.DONE === true', null, { timeout: 120000 });
  await page.locator('canvas').screenshot({ path: `${out}/impression_${name}.png` });
  console.log('rendered', name);
}
await browser.close();
