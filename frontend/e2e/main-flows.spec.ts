import { test, expect } from './fixtures';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper to register via API
async function registerViaApi(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Registration failed: ${res.status}`);
  return res.json();
}

// Helper to login via API and get token
async function loginViaApi(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  return res.json();
}

// ============================================================
// FLUJO 1: Authentication & Onboarding
// ============================================================
test.describe('Flujo 1: Authentication & Onboarding', () => {
  test('should register a new user and redirect to dashboard', async ({ page }) => {
    const email = `e2e-register-${Date.now()}@example.com`;
    const password = 'TestPass123!';

    await page.goto('/login');
    
    // Click register tab/button
    const registerBtn = page.getByRole('button', { name: /registrarse|crear cuenta|register/i });
    if (await registerBtn.isVisible()) {
      await registerBtn.click();
    }

    // Fill registration form
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    
    // Look for confirm password or just submit
    const confirmField = page.getByLabel(/confirm|confirmar/i);
    if (await confirmField.isVisible()) {
      await confirmField.fill(password);
    }

    await page.getByRole('button', { name: /registrarse|crear|register/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should login with valid credentials', async ({ page }) => {
    const email = `e2e-login-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    
    // Register first
    await registerViaApi(email, password);

    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('nonexistent@example.com');
    await page.getByLabel(/password|contrase/i).first().fill('wrongpassword');
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();

    // Should show error message
    await expect(page.getByText(/incorrecta|invalid|error/i)).toBeVisible({ timeout: 5000 });
  });

  test('should logout and redirect to login', async ({ page }) => {
    const email = `e2e-logout-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);

    // Login
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });

    // Logout
    const logoutBtn = page.getByRole('button', { name: /cerrar|logout|salir/i });
    if (await logoutBtn.isVisible()) {
      await logoutBtn.click();
    } else {
      // Try clicking on user menu first
      const userMenu = page.getByRole('button', { name: /user|perfil|avatar/i });
      if (await userMenu.isVisible()) {
        await userMenu.click();
        await page.getByRole('button', { name: /cerrar|logout|salir/i }).click();
      }
    }

    await expect(page).toHaveURL(/\/login/, { timeout: 10000 });
  });
});

// ============================================================
// FLUJO 2: Profile Management
// ============================================================
test.describe('Flujo 2: Profile Management', () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-profile-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);
    
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should navigate to profile page', async ({ page }) => {
    await page.getByRole('link', { name: /perfil|profile/i }).click();
    await expect(page).toHaveURL(/\/profile/);
    await expect(page.getByRole('heading', { name: /perfil|profile/i })).toBeVisible();
  });

  test('should update profile information', async ({ page }) => {
    await page.getByRole('link', { name: /perfil|profile/i }).click();
    await page.waitForURL(/\/profile/);

    // Fill profile fields
    const nameField = page.getByLabel(/nombre|name/i);
    if (await nameField.isVisible()) {
      await nameField.fill('Test User');
    }

    const titleField = page.getByLabel(/titulo|title|cargo/i);
    if (await titleField.isVisible()) {
      await titleField.fill('Software Engineer');
    }

    const bioField = page.getByLabel(/bio|sobre|about/i);
    if (await bioField.isVisible()) {
      await bioField.fill('Experienced developer with passion for clean code');
    }

    // Save
    await page.getByRole('button', { name: /guardar|save/i }).click();
    
    // Should show success or stay on page
    await expect(page).toHaveURL(/\/profile/);
  });

  test('should add work experience', async ({ page }) => {
    await page.getByRole('link', { name: /perfil|profile/i }).click();
    await page.waitForURL(/\/profile/);

    // Click add experience
    const addExpBtn = page.getByRole('button', { name: /experiencia|experience|agregar|add/i }).first();
    if (await addExpBtn.isVisible()) {
      await addExpBtn.click();
    }

    // Fill experience form
    const companyField = page.getByLabel(/empresa|company/i);
    if (await companyField.isVisible()) {
      await companyField.fill('Test Corp');
    }

    const roleField = page.getByLabel(/rol|role|cargo|position/i);
    if (await roleField.isVisible()) {
      await roleField.fill('Senior Developer');
    }

    // Save
    await page.getByRole('button', { name: /guardar|save/i }).click();

    // Should show the experience
    await expect(page.getByText('Test Corp')).toBeVisible({ timeout: 5000 });
  });

  test('should add education', async ({ page }) => {
    await page.getByRole('link', { name: /perfil|profile/i }).click();
    await page.waitForURL(/\/profile/);

    // Click add education
    const addEduBtn = page.getByRole('button', { name: /educaci|education|agregar|add/i }).first();
    if (await addEduBtn.isVisible()) {
      await addEduBtn.click();
    }

    // Fill education form
    const schoolField = page.getByLabel(/instituci|school|universidad|university/i);
    if (await schoolField.isVisible()) {
      await schoolField.fill('Test University');
    }

    const degreeField = page.getByLabel(/grado|degree|titulo/i);
    if (await degreeField.isVisible()) {
      await degreeField.fill('Computer Science');
    }

    // Save
    await page.getByRole('button', { name: /guardar|save/i }).click();

    // Should show the education
    await expect(page.getByText('Test University')).toBeVisible({ timeout: 5000 });
  });

  test('should add skills', async ({ page }) => {
    await page.getByRole('link', { name: /perfil|profile/i }).click();
    await page.waitForURL(/\/profile/);

    // Click add skill
    const addSkillBtn = page.getByRole('button', { name: /habilidad|skill|agregar|add/i });
    if (await addSkillBtn.isVisible()) {
      await addSkillBtn.click();
    }

    // Fill skill form
    const skillField = page.getByLabel(/habilidad|skill|nombre|name/i);
    if (await skillField.isVisible()) {
      await skillField.fill('TypeScript');
    }

    // Save
    await page.getByRole('button', { name: /guardar|save|a/i }).click();

    // Should show the skill
    await expect(page.getByText('TypeScript')).toBeVisible({ timeout: 5000 });
  });
});

// ============================================================
// FLUJO 3: Project Management
// ============================================================
test.describe('Flujo 3: Project Management', () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-project-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);
    
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should navigate to projects page', async ({ page }) => {
    await page.getByRole('link', { name: /proyecto|project/i }).click();
    await expect(page).toHaveURL(/\/projects/);
  });

  test('should create a new project', async ({ page }) => {
    await page.getByRole('link', { name: /proyecto|project/i }).click();
    
    // Click new project
    await page.getByRole('link', { name: /nuevo|new|crear|create/i }).click();
    await page.waitForURL(/\/projects\/new/);

    // Fill project form
    const nameField = page.getByLabel(/nombre|name/i);
    if (await nameField.isVisible()) {
      await nameField.fill('Test Project');
    }

    const descField = page.getByLabel(/descripci|description/i);
    if (await descField.isVisible()) {
      await descField.fill('A test project for E2E testing');
    }

    // Submit
    await page.getByRole('button', { name: /crear|create|guardar|save/i }).click();

    // Should redirect to projects list or project detail
    await expect(page).toHaveURL(/\/projects/, { timeout: 10000 });
    await expect(page.getByText('Test Project')).toBeVisible({ timeout: 5000 });
  });

  test('should edit a project', async ({ page }) => {
    // Create project first
    await page.getByRole('link', { name: /proyecto|project/i }).click();
    await page.getByRole('link', { name: /nuevo|new|crear|create/i }).click();
    await page.waitForURL(/\/projects\/new/);
    
    await page.getByLabel(/nombre|name/i).fill('Edit Test Project');
    await page.getByLabel(/descripci|description/i).fill('Original description');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/projects/);

    // Edit the project
    await page.getByRole('link', { name: /editar|edit/i }).first().click();
    await page.waitForURL(/\/edit/);

    // Update description
    const descField = page.getByLabel(/descripci|description/i);
    if (await descField.isVisible()) {
      await descField.fill('Updated description');
    }

    await page.getByRole('button', { name: /guardar|save|actualizar|update/i }).click();
    
    // Should redirect back
    await expect(page).toHaveURL(/\/projects/, { timeout: 10000 });
  });

  test('should delete a project', async ({ page }) => {
    // Create project first
    await page.getByRole('link', { name: /proyecto|project/i }).click();
    await page.getByRole('link', { name: /nuevo|new|crear|create/i }).click();
    await page.waitForURL(/\/projects\/new/);
    
    await page.getByLabel(/nombre|name/i).fill('Delete Test Project');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/projects/);

    // Delete the project
    const deleteBtn = page.getByRole('button', { name: /eliminar|delete/i }).first();
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      // Confirm if dialog appears
      const confirmBtn = page.getByRole('button', { name: /confirm|si|yes|eliminar|delete/i });
      if (await confirmBtn.isVisible()) {
        await confirmBtn.click();
      }
    }

    // Should no longer show the project
    await expect(page.getByText('Delete Test Project')).not.toBeVisible({ timeout: 5000 });
  });
});

// ============================================================
// FLUJO 4: Facets (CV/Portfolio) - Core Feature
// ============================================================
test.describe('Flujo 4: Facets (CV/Portfolio)', () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-facet-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);
    
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should navigate to facets page', async ({ page }) => {
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await expect(page).toHaveURL(/\/facets/);
  });

  test('should create a new facet', async ({ page }) => {
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    
    // Click new facet
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);

    // Fill facet form
    const nameField = page.getByLabel(/nombre|name/i);
    if (await nameField.isVisible()) {
      await nameField.fill('Developer Portfolio');
    }

    const slugField = page.getByLabel(/slug|url/i);
    if (await slugField.isVisible()) {
      await slugField.fill('developer-portfolio');
    }

    // Submit
    await page.getByRole('button', { name: /crear|create|guardar|save/i }).click();

    // Should redirect to facet detail
    await expect(page).toHaveURL(/\/facets\/[^\/]+$/, { timeout: 10000 });
    await expect(page.getByText('Developer Portfolio')).toBeVisible({ timeout: 5000 });
  });

  test('should edit facet content', async ({ page }) => {
    // Create facet first
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    
    await page.getByLabel(/nombre|name/i).fill('Edit Test Facet');
    await page.getByLabel(/slug|url/i).fill('edit-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Click edit
    await page.getByRole('link', { name: /editar|edit/i }).click();
    await page.waitForURL(/\/edit/);

    // Modify content - select experiences, skills, etc.
    // This depends on the actual UI
    const saveBtn = page.getByRole('button', { name: /guardar|save/i });
    if (await saveBtn.isVisible()) {
      await saveBtn.click();
    }

    // Should redirect back
    await expect(page).not.toHaveURL(/\/edit/, { timeout: 10000 });
  });

  test('should delete a facet', async ({ page }) => {
    // Create facet first
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    
    await page.getByLabel(/nombre|name/i).fill('Delete Test Facet');
    await page.getByLabel(/slug|url/i).fill('delete-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Go back to list
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.waitForURL(/\/facets/);

    // Delete
    const deleteBtn = page.getByRole('button', { name: /eliminar|delete/i }).first();
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      const confirmBtn = page.getByRole('button', { name: /confirm|si|yes|eliminar|delete/i });
      if (await confirmBtn.isVisible()) {
        await confirmBtn.click();
      }
    }

    await expect(page.getByText('Delete Test Facet')).not.toBeVisible({ timeout: 5000 });
  });

  test('should configure facet theme', async ({ page }) => {
    // Create facet first
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    
    await page.getByLabel(/nombre|name/i).fill('Theme Test Facet');
    await page.getByLabel(/slug|url/i).fill('theme-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Navigate to theme/edit section
    await page.getByRole('link', { name: /editar|edit|tema|theme/i }).click();
    
    // Change theme if options exist
    const themeSelect = page.getByRole('combobox', { name: /tema|theme/i });
    if (await themeSelect.isVisible()) {
      await themeSelect.click();
      await page.getByRole('option').first().click();
    }

    // Save
    await page.getByRole('button', { name: /guardar|save/i }).click();
  });
});

// ============================================================
// FLUJO 5: Public Portfolio Page & Review System
// ============================================================
test.describe('Flujo 5: Public Portfolio & Review', () => {
  test('should access public portfolio page', async ({ page }) => {
    // Create user and facet via API
    const email = `e2e-public-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    const regRes = await registerViaApi(email, password);
    const tokens = await loginViaApi(email, password);

    // Create facet via API
    const facetRes = await fetch(`${API_URL}/facets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tokens.access_token}`,
      },
      body: JSON.stringify({ name: 'Public Facet', slug: 'public-facet-e2e' }),
    });
    const facet = await facetRes.json();

    // Access public page
    await page.goto(`/${facet.slug}`);
    await expect(page).toHaveURL(/\/public-facet-e2e/);
    
    // Should show facet content
    await expect(page.getByText('Public Facet')).toBeVisible({ timeout: 10000 });
  });

  test('should show 404 for non-existent portfolio', async ({ page }) => {
    await page.goto('/non-existent-facet-slug-12345');
    
    // Should show not found or redirect
    await expect(page.getByText(/not found|no encontrado|404/i)).toBeVisible({ timeout: 10000 });
  });

  test('should generate and access review link', async ({ page }) => {
    const email = `e2e-review-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);
    
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });

    // Create facet
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    await page.getByLabel(/nombre|name/i).fill('Review Test Facet');
    await page.getByLabel(/slug|url/i).fill('review-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Navigate to review links section
    await page.getByRole('link', { name: /review|revisi|compartir|share/i }).click();
    
    // Create review link
    await page.getByRole('button', { name: /crear|create|generar|generate/i }).click();
    
    // Get the generated link/token
    const tokenInput = page.getByRole('textbox');
    let token = '';
    if (await tokenInput.isVisible()) {
      token = await tokenInput.inputValue();
    }

    // Or look for a link
    const reviewLink = page.getByRole('link', { name: /review|revisar/i });
    if (await reviewLink.isVisible()) {
      const href = await reviewLink.getAttribute('href');
      if (href) {
        await page.goto(href);
      }
    } else if (token) {
      await page.goto(`/review/${token}`);
    }

    // Should show review page
    await expect(page).toHaveURL(/\/review\//, { timeout: 10000 });
  });
});

// ============================================================
// FLUJO 6: Analytics, SEO, Notifications & Job Fit
// ============================================================
test.describe('Flujo 6: Analytics, SEO, Notifications & Job Fit', () => {
  test.beforeEach(async ({ page }) => {
    const email = `e2e-analytics-${Date.now()}@example.com`;
    const password = 'TestPass123!';
    await registerViaApi(email, password);
    
    await page.goto('/login');
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/password|contrase/i).first().fill(password);
    await page.getByRole('button', { name: /iniciar|login|entrar/i }).click();
    await page.waitForURL(/\/dashboard/, { timeout: 10000 });
  });

  test('should navigate to analytics page', async ({ page }) => {
    await page.getByRole('link', { name: /analitica|analytics/i }).click();
    await expect(page).toHaveURL(/\/analytics/);
  });

  test('should navigate to notifications page', async ({ page }) => {
    await page.getByRole('link', { name: /notificaci|notification/i }).click();
    await expect(page).toHaveURL(/\/notifications/);
  });

  test('should configure facet SEO', async ({ page }) => {
    // Create facet first
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    await page.getByLabel(/nombre|name/i).fill('SEO Test Facet');
    await page.getByLabel(/slug|url/i).fill('seo-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Navigate to SEO section
    await page.getByRole('link', { name: /seo/i }).click();
    await page.waitForURL(/\/seo/);

    // Fill SEO fields
    const metaTitle = page.getByLabel(/meta.*title|titulo.*meta/i);
    if (await metaTitle.isVisible()) {
      await metaTitle.fill('My Professional Portfolio');
    }

    const metaDesc = page.getByLabel(/meta.*description|descripci.*meta/i);
    if (await metaDesc.isVisible()) {
      await metaDesc.fill('Professional portfolio showcasing my work and skills');
    }

    // Save
    await page.getByRole('button', { name: /guardar|save/i }).click();

    // Should stay on page or show success
    await expect(page).toHaveURL(/\/seo/, { timeout: 5000 });
  });

  test('should access job fit analysis', async ({ page }) => {
    // Create facet first
    await page.getByRole('link', { name: /faceta|facet/i }).click();
    await page.getByRole('link', { name: /nueva|new|crear|create/i }).click();
    await page.waitForURL(/\/facets\/new/);
    await page.getByLabel(/nombre|name/i).fill('Job Fit Test Facet');
    await page.getByLabel(/slug|url/i).fill('job-fit-test-facet');
    await page.getByRole('button', { name: /crear|create/i }).click();
    await page.waitForURL(/\/facets\/[^\/]+$/);

    // Navigate to job fit section
    await page.getByRole('link', { name: /job.*fit|mercado|market|analisis|analysis/i }).click();
    await page.waitForURL(/\/job-fit/);

    // Should show job fit analysis page
    await expect(page).toHaveURL(/\/job-fit/, { timeout: 5000 });
  });

  test('should mark all notifications as read', async ({ page }) => {
    await page.getByRole('link', { name: /notificaci|notification/i }).click();
    await page.waitForURL(/\/notifications/);

    // Mark all as read if button exists
    const markAllBtn = page.getByRole('button', { name: /marcar.*le|mark.*read/i });
    if (await markAllBtn.isVisible()) {
      await markAllBtn.click();
    }
  });
});
