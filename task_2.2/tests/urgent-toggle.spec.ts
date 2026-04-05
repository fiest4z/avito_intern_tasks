import { test, expect } from '@playwright/test';

test.describe('TC-4: Тогл «Только срочные»', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test('при активации отображает только срочные объявления', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get total count before
    const paginationBefore = await page.locator('[class*="pagination__info"]').textContent();
    const totalBefore = parseInt(paginationBefore!.match(/из (\d+)/)?.[1] || '0');

    // Activate urgent toggle
    await page.locator('text=Только срочные').click();
    await page.waitForTimeout(1000);

    // Check that total count decreased
    const paginationAfter = await page.locator('[class*="pagination__info"]').textContent();
    const totalAfter = parseInt(paginationAfter!.match(/из (\d+)/)?.[1] || '0');
    expect(totalAfter).toBeLessThan(totalBefore);

    // Check that all visible cards have "Срочно" badge
    const cards = page.locator('[class*="card_15fhn"]');
    const cardCount = await cards.count();
    expect(cardCount).toBeGreaterThan(0);

    for (let i = 0; i < cardCount; i++) {
      const priorityBadge = cards.nth(i).locator('[class*="priority"]');
      await expect(priorityBadge).toBeVisible();
      await expect(priorityBadge).toHaveText('Срочно');
    }
  });

  test('при деактивации показывает все объявления', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const paginationBefore = await page.locator('[class*="pagination__info"]').textContent();

    // Toggle on
    await page.locator('text=Только срочные').click();
    await page.waitForTimeout(1000);

    // Toggle off
    await page.locator('text=Только срочные').click();
    await page.waitForTimeout(1000);

    const paginationAfter = await page.locator('[class*="pagination__info"]').textContent();
    expect(paginationAfter).toBe(paginationBefore);
  });
});
