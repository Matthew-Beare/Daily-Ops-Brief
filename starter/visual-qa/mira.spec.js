const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS = path.join(__dirname, 'artifacts');
fs.mkdirSync(ARTIFACTS, { recursive: true });

async function waitForProduct(page) {
  await page.goto('/index.html');
  await expect(page.locator('.mira-brand-lockup')).toBeVisible();
  await expect(page.locator('#miraV1Onboarding')).toBeVisible();
}

async function openFreshHome(page, width, height) {
  await page.addInitScript(() => localStorage.setItem('mira.onboarding.1.0.completed', 'true'));
  await page.setViewportSize({ width, height });
  await page.goto('/index.html');
  await expect(page.locator('#panel-home')).toBeVisible();
  await expect(page.getByText('Upcoming', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Your day, at a glance.' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'To-do' })).toBeVisible();
}

test('desktop first-run walkthrough is readable and branded', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await waitForProduct(page);
  await expect(page.locator('#miraV1Onboarding .mira-v1-dialog')).toBeVisible();
  await expect(page.locator('#miraV1Onboarding .mira-brand-mark')).toBeVisible();
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-first-run.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});

test('mobile first-run walkthrough fits phone viewport', async ({ page }) => {
  await page.setViewportSize({ width: 412, height: 915 });
  await waitForProduct(page);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-first-run.png'), fullPage: true });
  const dialog = page.locator('#miraV1Onboarding .mira-v1-dialog');
  const box = await dialog.boundingBox();
  expect(box.width).toBeLessThanOrEqual(412);
});

test('desktop home is restrained, upcoming-first, and hides implementation vocabulary', async ({ page }) => {
  await openFreshHome(page, 1440, 1000);
  const shell = page.locator('#panel-home');
  await expect(shell).toContainText('Your day, at a glance.');
  await expect(shell).toContainText('To-do');
  await expect(page.locator('.mira-primary-nav button')).toHaveCount(4);
  await expect(page.locator('header>nav')).toBeHidden();
  await expect(shell).not.toContainText('UUID');
  await expect(shell).not.toContainText('JSON');
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-home.png'), fullPage: true });
});

test('mobile home has three dominant actions and no horizontal overflow', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await expect(page.locator('.mira-primary-nav button')).toHaveCount(4);
  await expect(page.locator('.mira-quick-action')).toHaveCount(3);
  await expect(page.getByRole('button', { name: 'Scan' }).first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add item' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Receipt' })).toBeVisible();
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-home.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});

test('secondary product areas live in a hierarchical More page', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="more"]').click();
  await expect(page.locator('#panel-more')).toBeVisible();
  await expect(page.locator('#panel-more')).toContainText('Receipts');
  await expect(page.locator('#panel-more')).toContainText('Bring in existing data');
  await expect(page.locator('#panel-more')).toContainText('Feature Studio');
  await expect(page.locator('#panel-more')).toContainText('Setup & settings');
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-more.png'), fullPage: true });
});

test('migration is a visible one-step-at-a-time progression', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="more"]').click();
  await page.getByRole('button', { name: /Bring in existing data/ }).click();
  await expect(page.locator('#panel-migration')).toBeVisible();
  await expect(page.locator('#panel-migration')).toContainText('Connect Google');
  await expect(page.locator('#panel-migration')).toContainText('Find your spreadsheets');
  await expect(page.locator('#panel-migration')).toContainText('Choose and preview');
  await expect(page.locator('#panel-migration')).toContainText('Import what is safe');
  await expect(page.locator('#panel-migration details')).toContainText('Advanced migration details');
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-migration.png'), fullPage: true });
});

test('inventory normal view hides UUID and JSON implementation details', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="inventory"]').click();
  await expect(page.locator('#panel-inventory')).toBeVisible();
  await expect(page.locator('#panel-inventory')).toContainText('Inventory');
  const visibleText = await page.locator('#panel-inventory').innerText();
  expect(visibleText).not.toMatch(/create asset \+ uuid/i);
  expect(visibleText).not.toMatch(/metadata json/i);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-inventory.png'), fullPage: true });
});
