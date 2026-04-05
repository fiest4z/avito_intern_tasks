import { test, expect } from '@playwright/test';

test.describe('TC-1: Фильтр «Диапазон цен»', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('отображает только объявления в указанном ценовом диапазоне', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const priceFrom = page.locator('input[placeholder="От"]');
    const priceTo = page.locator('input[placeholder="До"]');
    await expect(priceFrom).toBeVisible();
    await expect(priceTo).toBeVisible();

    const MIN_PRICE = 10000;
    const MAX_PRICE = 30000;

    await priceFrom.fill(String(MIN_PRICE));
    await priceTo.fill(String(MAX_PRICE));
    await page.waitForTimeout(1000);

    const prices = await page.locator('[class*="card__price"]').allTextContents();
    expect(prices.length).toBeGreaterThan(0);

    for (const priceText of prices) {
      const price = parseInt(priceText.replace(/[^0-9]/g, ''));
      expect(price).toBeGreaterThanOrEqual(MIN_PRICE);
      expect(price).toBeLessThanOrEqual(MAX_PRICE);
    }
  });

  test('после сброса фильтра отображаются все объявления', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const paginationBefore = await page.locator('[class*="pagination__info"]').textContent();

    const priceFrom = page.locator('input[placeholder="От"]');
    const priceTo = page.locator('input[placeholder="До"]');
    await priceFrom.fill('50000');
    await priceTo.fill('60000');
    await page.waitForTimeout(1000);

    const paginationFiltered = await page.locator('[class*="pagination__info"]').textContent();

    // Clear filters
    await priceFrom.clear();
    await priceTo.clear();
    await page.waitForTimeout(1000);

    const paginationAfter = await page.locator('[class*="pagination__info"]').textContent();
    expect(paginationAfter).toBe(paginationBefore);
  });
});
