import { test, expect } from '@playwright/test';

test.describe('TC-6: Мобильная версия — Переключение темы', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('переключение с светлой темы на тёмную и обратно', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const themeToggle = page.locator('[class*="themeToggle"]');
    await expect(themeToggle).toBeVisible();

    // Check initial light theme
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    const bgLight = await page.evaluate('getComputedStyle(document.body).backgroundColor');
    expect(bgLight).toBe('rgb(255, 255, 255)');
    await expect(themeToggle).toContainText('Темная');

    // Switch to dark theme
    await themeToggle.click();
    await page.waitForTimeout(500);

    // Check dark theme
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    const bgDark = await page.evaluate('getComputedStyle(document.body).backgroundColor');
    expect(bgDark).toBe('rgb(26, 26, 26)');
    await expect(themeToggle).toContainText('Светлая');

    // Switch back to light theme
    await themeToggle.click();
    await page.waitForTimeout(500);

    // Check light theme restored
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    const bgRestored = await page.evaluate('getComputedStyle(document.body).backgroundColor');
    expect(bgRestored).toBe('rgb(255, 255, 255)');
    await expect(themeToggle).toContainText('Темная');
  });
});
