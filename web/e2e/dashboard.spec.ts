import { test, expect } from '@playwright/test';

// Note: These tests require authentication to be mocked
// In a real scenario, you'd set up Clerk's testing utilities

test.describe('Dashboard (Authenticated)', () => {
  // Skip these tests if no auth bypass is set up
  test.skip(({ browserName }) => true, 'Requires auth mock setup');

  test('should display dashboard for authenticated users', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('should display empty state when no positions', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.getByText('No Positions Yet')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Add Position' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Connect Brokerage' })).toBeVisible();
  });

  test('should show mobile navigation', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');

    // Mobile nav should be visible
    await expect(page.getByRole('link', { name: 'Home' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Positions' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Add' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Alerts' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Connect' })).toBeVisible();
  });

  test('should have refresh button', async ({ page }) => {
    await page.goto('/dashboard');

    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await expect(refreshButton).toBeVisible();
  });
});

test.describe('Dashboard Summary Cards', () => {
  test.skip(({ browserName }) => true, 'Requires auth mock setup');

  test('should display summary metrics', async ({ page }) => {
    await page.goto('/dashboard');

    // These would show data if positions exist
    await expect(page.getByText('In The Money')).toBeVisible();
    await expect(page.getByText('Total P/L')).toBeVisible();
    await expect(page.getByText('Expiring Soon')).toBeVisible();
    await expect(page.getByText('Alerts')).toBeVisible();
  });
});

test.describe('Navigation', () => {
  test.skip(({ browserName }) => true, 'Requires auth mock setup');

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/dashboard');

    // Navigate to Positions
    await page.getByRole('link', { name: 'Positions' }).click();
    await expect(page).toHaveURL(/.*positions/);

    // Navigate to Add Position
    await page.getByRole('link', { name: 'Add' }).click();
    await expect(page).toHaveURL(/.*add/);

    // Navigate to Alerts
    await page.getByRole('link', { name: 'Alerts' }).click();
    await expect(page).toHaveURL(/.*alerts/);

    // Navigate back to Dashboard
    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
