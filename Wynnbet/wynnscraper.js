const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

(async () => {
    const browser = await puppeteer.launch({ 
        headless: false,
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    });
    const page = await browser.newPage();

    // Set a random user agent
    const userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"; // You can change this
    await page.setUserAgent(userAgent);

    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9',
    });

    await page.goto('https://ny.wynnbet.com/competition/115');

    // Wait for the NFL link and click
    await page.waitForSelector("p[normalize-space()='NFL']", { timeout: 10000 });
    await page.click("p[normalize-space()='NFL']");

    // Simulate more human-like mouse movements and clicks
    const gameLinks = await page.$$(".eventItemName");
    for (let link of gameLinks) {
        const linkPosition = await link.boundingBox();
        await page.mouse.move(linkPosition.x + linkPosition.width / 2, linkPosition.y + linkPosition.height / 2);
        await page.mouse.click(linkPosition.x + linkPosition.width / 2, linkPosition.y + linkPosition.height / 2);
        
        await page.waitForTimeout(2000); // wait for 2 seconds
        await page.goBack();
    }

    await browser.close();
})();
