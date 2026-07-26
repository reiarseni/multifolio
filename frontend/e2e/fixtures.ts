import { test as base, expect } from '@playwright/test';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const test = base.extend<{
  testUser: { email: string; password: string };
  authPage: { login: () => Promise<void>; register: (email: string, password: string) => Promise<void> };
}>({
  testUser: async ({}, use) => {
    const email = `test-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await use({ email, password });
  },

  authPage: async ({ page }, use) => {
    const login = async () => {
      await page.goto('/login');
    };

    const register = async (email: string, password: string) => {
      await page.goto('/login');
      await page.getByRole('button', { name: /registrarse|crear cuenta|register/i }).click();
      await page.getByLabel(/email/i).fill(email);
      await page.getByLabel(/password|contrase/i).fill(password);
      await page.getByLabel(/confirm/i).fill(password);
      await page.getByRole('button', { name: /registrarse|register/i }).click();
      await page.waitForURL(/\/dashboard/);
    };

    await use({ login, register });
  },
});

export { expect };
