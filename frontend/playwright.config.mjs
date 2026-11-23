import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'https://127.0.0.1:18443',
    ignoreHTTPSErrors: true,
    browserName: 'chromium',
    trace: 'off',
    screenshot: 'off',
  },
  webServer: [
    {
      command: `${process.env.PYTHON_E2E || '../venv/bin/python'} ../tests/navegador/servidor.py`,
      url: 'http://127.0.0.1:18080/salud',
      reuseExistingServer: false,
      timeout: 45000,
    },
    {
      command: 'node tests/e2e/servidor-https.mjs',
      url: 'https://127.0.0.1:18443/login',
      ignoreHTTPSErrors: true,
      reuseExistingServer: false,
      timeout: 45000,
    },
  ],
});
