const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS = path.join(__dirname, 'artifacts');
fs.mkdirSync(ARTIFACTS, { recursive: true });

async function waitForProduct(page) {
  await page.goto('/index.html');
  await expect(page.locator('.mira-brand-mark')).toBeVisible();
  await expect(page.locator('.mira-wordmark strong')).toHaveText('MIRA');
  await expect(page.locator('#miraV1Onboarding')).toBeVisible();
}

async function openFreshHome(page, width, height) {
  await page.addInitScript(() => localStorage.setItem('mira.onboarding.1.0.completed', 'true'));
  await page.setViewportSize({ width, height });
  await page.goto('/index.html');
  await expect(page.locator('#panel-home')).toBeVisible();
  await expect(page.getByText('Upcoming', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'What matters next' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'To do' })).toBeVisible();
}

test('desktop first-run walkthrough is readable and carries the MIRA mark', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await waitForProduct(page);
  await expect(page.locator('#miraV1Onboarding .mira-v1-dialog')).toBeVisible();
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-first-run.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});

test('mobile first-run walkthrough fits phone viewport without colliding with shell', async ({ page }) => {
  await page.setViewportSize({ width: 412, height: 915 });
  await waitForProduct(page);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-first-run.png'), fullPage: true });
  const dialog = page.locator('#miraV1Onboarding .mira-v1-dialog');
  const box = await dialog.boundingBox();
  expect(box.width).toBeLessThanOrEqual(412);
});

test('desktop home is restrained, upcoming-first, and hides developer vocabulary', async ({ page }) => {
  await openFreshHome(page, 1440, 1000);
  const shell = page.locator('#panel-home');
  await expect(shell).toContainText('What matters next');
  await expect(shell).toContainText('To do');
  await expect(page.locator('.mira-bottom-nav button')).toHaveCount(4);
  await expect(page.locator('header nav')).toBeHidden();
  await expect(shell).not.toContainText('UUID');
  await expect(shell).not.toContainText('JSON');
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-home.png'), fullPage: true });
});

test('mobile home keeps four large navigation choices and no horizontal overflow', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await expect(page.locator('.mira-bottom-nav button')).toHaveCount(4);
  await expect(page.locator('.mira-quick')).toHaveCount(4);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-home.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});

test('advanced product areas live behind More instead of top-level button soup', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.getByRole('button', { name: 'More' }).click();
  await expect(page.locator('.mira-sheet')).toContainText('Migration');
  await expect(page.locator('.mira-sheet')).toContainText('Feature Studio');
  await expect(page.locator('.mira-sheet')).toContainText('Settings');
  await page.getByRole('button', { name: 'Migration' }).click();
  await expect(page.locator('#panel-migration')).toBeVisible();
  await expect(page.locator('#panel-migration')).toContainText('Connect Google');
  await expect(page.locator('#panel-migration')).toContainText('Choose and preview');
  await expect(page.locator('#panel-migration')).toContainText('Import');
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-migration.png'), fullPage: true });
});

test('inventory normal view does not expose UUID or JSON implementation details', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.getByRole('button', { name: 'Inventory' }).click();
  await expect(page.locator('#panel-inventory')).toBeVisible();
  await expect(page.locator('#panel-inventory')).toContainText('Inventory');
  await expect(page.locator('#panel-inventory')).not.toContainText('Create asset + UUID');
  const visibleText = await page.locator('#panel-inventory').innerText();
  expect(visibleText).not.toMatch(/metadata json/i);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-inventory.png'), fullPage: true });
});
