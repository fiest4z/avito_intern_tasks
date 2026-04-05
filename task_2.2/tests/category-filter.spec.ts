import { test, expect } from '@playwright/test';

test.describe('TC-3: Фильтр «Категория»', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('фильтрует объявления по категории «Электроника»', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const categorySelect = page.locator('aside select').filter({ hasText: 'Все категории' });
    await categorySelect.selectOption({ label: 'Электроника' });
    await page.waitForTimeout(1000);

    const categories = await page.locator('[class*="card__category"]').allTextContents();
    expect(categories.length).toBeGreaterThan(0);

    for (const cat of categories) {
      expect(cat.trim()).toBe('Электроника');
    }
  });

  test('фильтрует объявления по категории «Транспорт»', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const categorySelect = page.locator('aside select').filter({ hasText: 'Все категории' });
    await categorySelect.selectOption({ label: 'Транспорт' });
    await page.waitForTimeout(1000);

    const categories = await page.locator('[class*="card__category"]').allTextContents();
    expect(categories.length).toBeGreaterThan(0);

    for (const cat of categories) {
      expect(cat.trim()).toBe('Транспорт');
    }
  });

  test('сброс категории показывает все объявления', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const paginationBefore = await page.locator('[class*="pagination__info"]').textContent();

    const categorySelect = page.locator('aside select').filter({ hasText: 'Все категории' });
    await categorySelect.selectOption({ label: 'Электроника' });
    await page.waitForTimeout(1000);

    await categorySelect.selectOption({ label: 'Все категории' });
    await page.waitForTimeout(1000);

    const paginationAfter = await page.locator('[class*="pagination__info"]').textContent();
    expect(paginationAfter).toBe(paginationBefore);
  });
});
