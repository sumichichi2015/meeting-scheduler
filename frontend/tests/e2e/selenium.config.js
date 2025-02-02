const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');

const setup = async () => {
  const options = new chrome.Options();
  options.addArguments('--headless');
  options.addArguments('--no-sandbox');
  options.addArguments('--disable-dev-shm-usage');

  const driver = await new Builder()
    .forBrowser('chrome')
    .setChromeOptions(options)
    .build();

  return driver;
};

const takeScreenshot = async (driver, name) => {
  const screenshot = await driver.takeScreenshot();
  require('fs').writeFileSync(`./tests/e2e/screenshots/${name}.png`, screenshot, 'base64');
};

module.exports = {
  setup,
  takeScreenshot,
  BASE_URL: 'http://localhost:5173'
};
