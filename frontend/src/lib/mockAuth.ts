// ─── Mock Authentication Service ────────────────────────────────────────────
// This provides a fully offline auth system using localStorage.
// It activates automatically when the backend is unreachable.

const MOCK_USERS_KEY = 'vireoniq_mock_users';
const MOCK_TOKEN_PREFIX = 'mock_jwt_';

interface MockUser {
  id: string;
  email: string;
  passwordHash: string;
  role_id: string;
  is_active: boolean;
  is_email_verified: boolean;
}

// ── Pre-seeded Demo Credentials ───────────────────────────────────────────────
// Email: demo@vireoniq.com | Password: Demo@1234
const DEMO_USERS: MockUser[] = [
  {
    id: 'mock-user-test-001',
    email: 'test@example.com',
    passwordHash: btoa('password'),
    role_id: 'mock-role-user-001',
    is_active: true,
    is_email_verified: true,
  },
  {
    id: 'mock-user-demo-001',
    email: 'demo@vireoniq.com',
    passwordHash: btoa('Demo@1234'), // base64 - mock only, not real security
    role_id: 'mock-role-user-001',
    is_active: true,
    is_email_verified: true,
  },
  {
    id: 'mock-user-admin-001',
    email: 'admin@vireoniq.com',
    passwordHash: btoa('Admin@9876'),
    role_id: 'mock-role-admin-001',
    is_active: true,
    is_email_verified: true,
  },
];

function getUsers(): MockUser[] {
  try {
    const stored = localStorage.getItem(MOCK_USERS_KEY);
    const users: MockUser[] = stored ? JSON.parse(stored) : [];
    // Always ensure demo users exist
    const emails = users.map((u) => u.email);
    for (const demo of DEMO_USERS) {
      if (!emails.includes(demo.email)) users.push(demo);
    }
    return users;
  } catch {
    return [...DEMO_USERS];
  }
}

function saveUsers(users: MockUser[]): void {
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users));
}

function generateToken(userId: string): string {
  return `${MOCK_TOKEN_PREFIX}${userId}_${Date.now()}`;
}

export function mockRegister(email: string, password: string): { success: boolean; error?: string } {
  const users = getUsers();
  if (users.find((u) => u.email === email)) {
    return { success: false, error: 'Email already registered.' };
  }
  const newUser: MockUser = {
    id: `mock-user-${Date.now()}`,
    email,
    passwordHash: btoa(password),
    role_id: 'mock-role-user-001',
    is_active: true,
    is_email_verified: true,
  };
  users.push(newUser);
  saveUsers(users);
  return { success: true };
}

export function mockLogin(
  email: string,
  password: string
): { success: boolean; token?: string; user?: object; error?: string } {
  const users = getUsers();
  const user = users.find((u) => u.email === email);
  if (!user) return { success: false, error: 'Incorrect email or password.' };
  if (user.passwordHash !== btoa(password)) {
    return { success: false, error: 'Incorrect email or password.' };
  }
  const token = generateToken(user.id);
  return {
    success: true,
    token,
    user: {
      id: user.id,
      email: user.email,
      role_id: user.role_id,
      is_active: user.is_active,
      is_email_verified: user.is_email_verified,
    },
  };
}
