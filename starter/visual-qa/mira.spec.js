const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS = path.join(__dirname, 'artifacts');
fs.mkdirSync(ARTIFACTS, { recursive: true });

async function waitForProduct(page) {
  await page.goto('/index.html');
  await expect(page.locator('#miraReleaseOnboarding')).toBeVisible();
  await expect(page.locator('#miraReleaseOnboarding .mira-release-brand')).toBeVisible();
}

async function openFreshHome(page, width, height) {
  await page.addInitScript(() => {
    localStorage.setItem('mira.onboarding.1.0.completed', 'true');
    localStorage.setItem('mira.onboarding.release-v5.completed', 'true');
    localStorage.setItem('mira.onboarding.personalize-v3.completed', 'true');
  });
  await page.setViewportSize({ width, height });
  await page.goto('/index.html');
  await expect(page.locator('#panel-home')).toBeVisible();
  await expect(page.locator('.mira-home-eyebrow')).toHaveText('Upcoming');
  await expect(page.getByRole('heading', { name: 'Your day, at a glance.' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'To-do' })).toBeVisible();
}

test('desktop first-run walkthrough is readable and uses canonical logo', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await waitForProduct(page);
  const dialog = page.locator('#miraReleaseOnboarding .mira-release-dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.locator('.mira-release-brand')).toHaveAttribute('src', /mira-logo\.png$/);
  await expect(dialog).toContainText('MIRA is your assistant');
  await expect(dialog).toContainText('MIRROR');
  await page.screenshot({ path: path.join(ARTIFACTS, 'desktop-first-run.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2);
  expect(overflow).toBeFalsy();
});

test('mobile first-run walkthrough fits phone viewport', async ({ page }) => {
  await page.setViewportSize({ width: 412, height: 915 });
  await waitForProduct(page);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-first-run.png'), fullPage: true });
  const box = await page.locator('#miraReleaseOnboarding .mira-release-dialog').boundingBox();
  expect(box.width).toBeLessThanOrEqual(412);
});

test('desktop home is restrained and upcoming-first', async ({ page }) => {
  await openFreshHome(page, 1440, 1000);
  const shell = page.locator('#panel-home');
  await expect(shell).toContainText('Your day, at a glance.');
  await expect(shell).toContainText('To-do');
  await expect(page.locator('.mira-primary-nav button')).toHaveCount(4);
  await expect(page.locator('header>nav')).toBeHidden();
  await expect(shell).not.toContainText('UUID');
  await expect(shell).not.toContainText('JSON');
  await expect(page.locator('.mira-brand-lockup')).toHaveAttribute('src', /mira-logo\.png$/);
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

test('secondary product areas live in hierarchical More', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="more"]').click();
  const more = page.locator('#panel-more');
  await expect(more).toBeVisible();
  await expect(more).toContainText('Everyday');
  await expect(more).toContainText('Build & connect');
  await expect(more).toContainText('Receipts');
  await expect(more).toContainText('Bring in existing data');
  await expect(more).toContainText('Feature Studio');
  await expect(more).toContainText('Setup & settings');
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-more.png'), fullPage: true });
});

test('migration is a one-step-at-a-time progression', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="more"]').click();
  await page.getByRole('button', { name: /Bring in existing data/ }).click();
  const migration = page.locator('#panel-migration');
  await expect(migration).toBeVisible();
  await expect(migration).toContainText(/Connect Google|Finish setup/i);
  await expect(migration).toContainText(/Find your spreadsheets/i);
  await expect(migration).toContainText(/preview/i);
  await expect(migration).toContainText(/Import what is safe/i);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-migration.png'), fullPage: true });
});

test('inventory normal view hides implementation details', async ({ page }) => {
  await openFreshHome(page, 412, 915);
  await page.locator('.mira-primary-nav [data-primary="inventory"]').click();
  const inventory = page.locator('#panel-inventory');
  await expect(inventory).toBeVisible();
  const visibleText = await inventory.innerText();
  expect(visibleText).not.toMatch(/create asset \+ uuid|metadata json|api base/i);
  await page.screenshot({ path: path.join(ARTIFACTS, 'android-inventory.png'), fullPage: true });
});
