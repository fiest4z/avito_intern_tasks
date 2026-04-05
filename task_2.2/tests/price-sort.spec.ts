import { test, expect } from '@playwright/test';

function parsePrice(text: string): number {
  return parseInt(text.replace(/[^0-9]/g, ''));
}

test.describe('TC-2: Сортировка «По цене»', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('сортирует по цене по убыванию', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const sortSelect = page.locator('select').filter({ hasText: 'Дате создания' });
    await sortSelect.selectOption({ label: 'Цене' });
    await page.waitForTimeout(1000);

    // Ensure order is "По убыванию"
    const orderSelect = page.locator('select').filter({ hasText: /убыванию|возрастанию/ });
    await orderSelect.selectOption({ label: 'По убыванию' });
    await page.waitForTimeout(1000);

    const priceTexts = await page.locator('[class*="card__price"]').allTextContents();
    expect(priceTexts.length).toBeGreaterThan(1);

    const prices = priceTexts.map(parsePrice);
    for (let i = 1; i < prices.length; i++) {
      expect(prices[i]).toBeLessThanOrEqual(prices[i - 1]);
    }
  });

  test('сортирует по цене по возрастанию', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const sortSelect = page.locator('select').filter({ hasText: 'Дате создания' });
    await sortSelect.selectOption({ label: 'Цене' });
    await page.waitForTimeout(500);

    const orderSelect = page.locator('select').filter({ hasText: /убыванию|возрастанию/ });
    await orderSelect.selectOption({ label: 'По возрастанию' });
    await page.waitForTimeout(1000);

    const priceTexts = await page.locator('[class*="card__price"]').allTextContents();
    expect(priceTexts.length).toBeGreaterThan(1);

    const prices = priceTexts.map(parsePrice);
    for (let i = 1; i < prices.length; i++) {
      expect(prices[i]).toBeGreaterThanOrEqual(prices[i - 1]);
    }
  });
});
