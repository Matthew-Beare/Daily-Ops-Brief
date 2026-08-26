const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS = path.join(__dirname, 'artifacts');
fs.mkdirSync(ARTIFACTS, { recursive: true });

async function waitForProduct(page) {
  await page.goto('/index.html');
  await expect(page.locator('header h1')).toHaveText('MIRA // MIRROR');
  await expect(page.locator('header p')).toContainText('Reflecting reality.');
  await expect(page.locator('#miraV1Onboarding')).toBeVisible();
}

test('desktop first-run walkthrough is readable and branded', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await waitForProduct(page);
  await expect(page.locator('#miraV1Onboarding .mira-v1-dialog')).toBeVisible();
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

test('shared application exposes receipts, settings and feature studio without onboarding', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('mira.onboarding.1.0.completed', 'true'));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/index.html');
  await expect(page.locator('header h1')).toHaveText('MIRA // MIRROR');
  await expect(page.getByRole('button', { name: 'Receipts' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Setup & Settings' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Feature Studio' })).toBeVisible();
  await page.getByRole('button', { name: 'Setup & Settings' }).click();
  await expect(page.locator('#panel-setup')).toBeVisible();
  await expect(page.locator('#panel-setup')).toContainText('ChatGPT');
  await expect(page.locator('#panel-setup')).toContainText('Google Workspace');
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-settings.png'), fullPage: true });
});

test('shared application mobile navigation remains usable', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('mira.onboarding.1.0.completed', 'true'));
  await page.setViewportSize({ width: 412, height: 915 });
  await page.goto('/index.html');
  await expect(page.getByRole('button', { name: 'Receipts' })).toBeVisible();
  await page.getByRole('button', { name: 'Receipts' }).click();
  await expect(page.locator('#panel-receipts')).toContainText('Reconcile a receipt');
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-receipts.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});
