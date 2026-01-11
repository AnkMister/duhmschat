import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display landing page for unauthenticated users', async ({ page }) => {
    await page.goto('/');

    // Check hero section
    await expect(page.getByRole('heading', { name: /Never Miss an In-The-Money Option/i })).toBeVisible();
    await expect(page.getByText(/Track your options portfolio/i)).toBeVisible();
  });

  test('should have sign in and sign up buttons', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('link', { name: 'Sign In' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Get Started' })).toBeVisible();
  });

  test('should display features section', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByText('ITM Detection')).toBeVisible();
    await expect(page.getByText('Smart Alerts')).toBeVisible();
    await expect(page.getByText('Portfolio Analytics')).toBeVisible();
    await expect(page.getByText('Secure Connection')).toBeVisible();
    await expect(page.getByText('Mobile First')).toBeVisible();
    await expect(page.getByText('AI Insights')).toBeVisible();
  });

  test('should navigate to sign in page', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'Sign In' }).first().click();

    await expect(page).toHaveURL(/.*sign-in/);
  });

  test('should navigate to sign up page', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('link', { name: 'Get Started' }).first().click();

    await expect(page).toHaveURL(/.*sign-up/);
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Header should still be visible
    await expect(page.getByText('Options Monitor')).toBeVisible();

    // Features should stack on mobile
    const featuresSection = page.locator('text=Everything You Need');
    await expect(featuresSection).toBeVisible();
  });
});

test.describe('PWA Features', () => {
  test('should have valid manifest', async ({ page }) => {
    const response = await page.goto('/manifest.webmanifest');

    if (response) {
      expect(response.status()).toBe(200);
      const manifest = await response.json();

      expect(manifest.name).toBe('Options Portfolio Monitor');
      expect(manifest.short_name).toBe('Options Monitor');
      expect(manifest.display).toBe('standalone');
      expect(manifest.icons).toBeDefined();
      expect(manifest.icons.length).toBeGreaterThan(0);
    }
  });

  test('should have appropriate meta tags for PWA', async ({ page }) => {
    await page.goto('/');

    // Check viewport meta
    const viewport = await page.getAttribute('meta[name="viewport"]', 'content');
    expect(viewport).toContain('width=device-width');

    // Check theme color
    const themeColor = await page.getAttribute('meta[name="theme-color"]', 'content');
    expect(themeColor).toBeDefined();
  });
});
