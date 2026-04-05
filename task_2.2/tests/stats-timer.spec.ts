import { test, expect } from '@playwright/test';

test.describe('TC-5: Страница статистики — Таймер обновления', () => {
  test.use({ viewport: { width: 1280, height: 720 } });

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.click('text=Статистика');
    await page.locator('[class*="refreshButton"]').waitFor({ timeout: 15000 });
  });

  test('кнопка «Обновить» обновляет данные и сбрасывает таймер', async ({ page }) => {
    // Wait for timer to count down significantly so reset is clearly detectable
    await page.waitForTimeout(5000);
    const timerBefore = await page.locator('[class*="timeValue"]').textContent();

    function timerToSeconds(t: string): number {
      const parts = t.split(':');
      return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    }

    const secondsBefore = timerToSeconds(timerBefore!);
    expect(secondsBefore).toBeLessThanOrEqual(296);

    // Click refresh
    await page.locator('button:has-text("Обновить")').click();
    await page.waitForTimeout(2000);

    const timerAfter = await page.locator('[class*="timeValue"]').textContent();
    const secondsAfter = timerToSeconds(timerAfter!);

    // After refresh, timer should reset (closer to 5:00 than before)
    expect(secondsAfter).toBeGreaterThan(secondsBefore);
  });

  test('кнопка паузы останавливает таймер', async ({ page }) => {
    const pauseBtn = page.locator('button:has-text("⏸")');
    await expect(pauseBtn).toBeVisible();
    await pauseBtn.click();
    await page.waitForTimeout(500);

    // Button should change to play icon
    await expect(page.locator('[class*="toggleIcon"]')).toContainText('▶');

    // Timer should show "Автообновление выключено"
    await expect(page.locator('text=Автообновление выключено')).toBeVisible();
  });

  test('кнопка запуска возобновляет таймер после паузы', async ({ page }) => {
    // Pause timer
    await page.locator('button:has-text("⏸")').click();
    await page.waitForTimeout(500);
    await expect(page.locator('text=Автообновление выключено')).toBeVisible();

    // Click play button to resume
    const toggleBtn = page.locator('[class*="toggleButton"]');
    await toggleBtn.click();
    await page.waitForTimeout(1000);

    // BUG: After clicking play, the timer should resume but it stays disabled.
    // The toggle button should change back to pause (⏸) and show countdown.
    await expect(page.locator('[class*="toggleIcon"]')).toContainText('⏸');
  });
});
