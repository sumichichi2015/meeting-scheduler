const { By, until } = require('selenium-webdriver');
const { setup, takeScreenshot, BASE_URL } = require('./selenium.config');

describe('会議作成フロー', () => {
  let driver;

  beforeAll(async () => {
    driver = await setup();
  });

  afterAll(async () => {
    await driver.quit();
  });

  test('会議を作成できること', async () => {
    await driver.get(`${BASE_URL}/create`);
    await takeScreenshot(driver, 'create-meeting-initial');

    // タイトルを入力
    const titleInput = await driver.findElement(By.name('title'));
    await titleInput.sendKeys('テスト会議');

    // 説明を入力
    const descInput = await driver.findElement(By.name('description'));
    await descInput.sendKeys('これはテスト用の会議です');

    // 日時を選択（カレンダーUIの実装に応じて調整が必要）
    const dateInput = await driver.findElement(By.className('date-picker'));
    await dateInput.click();
    
    await takeScreenshot(driver, 'create-meeting-filled');

    // フォームを送信
    const submitButton = await driver.findElement(By.css('button[type="submit"]'));
    await submitButton.click();

    // 成功メッセージを確認
    const successMessage = await driver.wait(
      until.elementLocated(By.className('success-message')),
      5000
    );
    
    await takeScreenshot(driver, 'create-meeting-success');

    expect(await successMessage.isDisplayed()).toBe(true);
  });

  test('必須項目が未入力の場合エラーが表示されること', async () => {
    await driver.get(`${BASE_URL}/create`);

    // 空のフォームを送信
    const submitButton = await driver.findElement(By.css('button[type="submit"]'));
    await submitButton.click();

    // エラーメッセージを確認
    const errorMessage = await driver.wait(
      until.elementLocated(By.className('error-message')),
      5000
    );
    
    await takeScreenshot(driver, 'create-meeting-validation-error');

    expect(await errorMessage.isDisplayed()).toBe(true);
  });
});
