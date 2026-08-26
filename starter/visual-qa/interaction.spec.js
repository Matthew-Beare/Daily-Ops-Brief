const { test, expect } = require('@playwright/test');

async function boot(page, { onboarding = true, personalize = true, native = false } = {}) {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.addInitScript(({ onboarding, personalize, native }) => {
    if (onboarding) {
      localStorage.setItem('mira.onboarding.1.0.completed', 'true');
      localStorage.setItem('mira.onboarding.release-v5.completed', 'true');
    }
    if (personalize) localStorage.setItem('mira.onboarding.personalize-v3.completed', 'true');
    if (native) {
      globalThis.__openedExternal = [];
      globalThis.__wallDisplay = [];
      globalThis.__googleAuthorize = [];
      globalThis.MirrorNative = {
        openExternal(url) { globalThis.__openedExternal.push(String(url)); },
        setWallDisplay(enabled) { globalThis.__wallDisplay.push(Boolean(enabled)); },
        authorizeGoogle(capabilities) { globalThis.__googleAuthorize.push(String(capabilities)); },
        hasNfc() { return false; },
      };
    }
  }, { onboarding, personalize, native });
  await page.goto('/index.html');
  await expect(page.locator('.mira-primary-nav')).toBeVisible();
  await expect(page.locator('#panel-home')).toBeVisible();
  await expect.poll(() => errors).toEqual([]);
  return errors;
}

test('shared shell initializes once with four primary destinations', async ({ page }) => {
  await boot(page);
  await expect(page.locator('.mira-primary-nav')).toHaveCount(1);
  await expect(page.locator('.mira-primary-nav [data-primary]')).toHaveCount(4);
  await expect(page.locator('#panel-home')).toHaveCount(1);
  await expect(page.locator('#panel-more')).toHaveCount(1);
  await expect(page.locator('#panel-meals')).toHaveCount(0);
  await expect(page.locator('#panel-preferences')).toHaveCount(0);
  const loaded = await page.evaluate(() => [...document.scripts].map((s) => (s.getAttribute('src') || '').split('/').pop()).filter(Boolean));
  for (const file of ['provider-connect-v3.js', 'google-authority-v1.js', 'cloud-authority-compat.js', 'guided-migration.js', 'dashboard-v2.js', 'interaction-audit.js', 'brand-final.js']) {
    expect(loaded.filter((name) => name === file), `${file} should execute once`).toHaveLength(1);
  }
});

test('every visible enabled button participates in the action audit', async ({ page }) => {
  await boot(page);
  await page.waitForTimeout(150);
  const unaudited = await page.locator('button:visible:not(:disabled)').evaluateAll((buttons) => buttons
    .filter((button) => !button.dataset.actionAudit)
    .map((button) => ({ id: button.id, text: button.textContent.trim() })));
  expect(unaudited).toEqual([]);
});

test('Continue with Google invokes native Google instead of requiring a server address', async ({ page }) => {
  await boot(page, { native: true });
  await page.evaluate(() => globalThis.switchTab('providers'));
  const button = page.getByRole('button', { name: 'Continue with Google', exact: true });
  await expect(button).toBeEnabled();
  await button.click();
  await expect.poll(() => page.evaluate(() => globalThis.__googleAuthorize.length)).toBe(1);
  const requested = await page.evaluate(() => globalThis.__googleAuthorize[0]);
  expect(requested).toContain('drive');
  expect(requested).toContain('sheets');
  await expect(page.locator('#miraProviderFriendlyStatus')).toContainText(/permission|waiting/i);
});

test('missing cloud registration is visible rather than a dead button', async ({ page }) => {
  await boot(page, { native: false });
  await page.evaluate(() => globalThis.switchTab('providers'));
  await page.getByRole('button', { name: 'Continue with Google', exact: true }).click();
  await expect(page.locator('#miraProviderFriendlyStatus')).toContainText(/release|build|connection/i);
});

test('setup-dependent writes remain clickable and route to setup', async ({ page }) => {
  await boot(page, { onboarding: true });
  await page.evaluate(() => { localStorage.removeItem('mira.provider.connection.v3'); globalThis.switchTab('inventory'); });
  const save = page.getByRole('button', { name: 'Save item', exact: true });
  await expect(save).toBeEnabled();
  await save.click();
  await expect(page.locator('#miraReleaseOnboarding, #miraV1Onboarding').first()).toBeVisible();
});

test('normal surfaces use plain language and hide implementation IDs', async ({ page }) => {
  await boot(page);
  for (const target of ['home', 'inventory', 'more']) {
    await page.evaluate((target) => globalThis.MiraShell.go(target), target);
    const panel = page.locator(`#panel-${target}`);
    await expect(panel).toBeVisible();
    const text = await panel.innerText();
    expect(text, target).not.toMatch(/\bUUID\b|metadata JSON|API base URL/i);
  }
});

test('home prioritizes Upcoming, to-do and three large capture actions', async ({ page }) => {
  await boot(page);
  await expect(page.locator('.mira-home-eyebrow')).toHaveText('Upcoming');
  await expect(page.locator('.mira-quick-action')).toHaveCount(3);
  await expect(page.getByText('To-do', { exact: true })).toBeVisible();
  await expect(page.locator('.mira-primary-nav')).not.toContainText(/Migration|Integrations|Settings|Photos/);
});

test('canonical uploaded logo is used in the shell and onboarding', async ({ page }) => {
  await boot(page, { onboarding: false });
  await expect(page.locator('.mira-brand-lockup')).toHaveAttribute('src', /mira-logo\.png$/);
  const wizard = page.locator('#miraReleaseOnboarding');
  await expect(wizard).toBeVisible();
  await expect(wizard.locator('.mira-release-brand')).toHaveAttribute('src', /mira-logo\.png$/);
});

test('Android wall display toggles native immersive mode', async ({ page }) => {
  await boot(page, { native: true });
  await page.evaluate(async () => { await globalThis.MiraExperienceV3.enableKiosk(false); });
  await expect(page.locator('html')).toHaveClass(/mira-kiosk/);
  await expect.poll(() => page.evaluate(() => globalThis.__wallDisplay.at(-1))).toBe(true);
  await page.evaluate(async () => { await globalThis.MiraExperienceV3.disableKiosk(); });
  await expect(page.locator('html')).not.toHaveClass(/mira-kiosk/);
  await expect.poll(() => page.evaluate(() => globalThis.__wallDisplay.at(-1))).toBe(false);
});
