import { describe, it, expect, beforeEach } from 'vitest';
import { isMockAuthEnabled, mockLogin, mockRegister } from '@/lib/mockAuth';
import { useAuthStore } from '@/store/authStore';

describe('authStore and mockAuth security gating', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it('sets and clears authenticated user state', () => {
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().token).toBeNull();

    useAuthStore.getState().setAuth(
      { id: 'u-1', email: 'engineer@vireoniq.com', full_name: 'Test Engineer' },
      'jwt-token-sample',
    );

    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user?.email).toBe('engineer@vireoniq.com');
    expect(useAuthStore.getState().token).toBe('jwt-token-sample');

    useAuthStore.getState().logout();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
    expect(useAuthStore.getState().token).toBeNull();
  });

  it('keeps offline mock auth disabled unless explicitly opted in', () => {
    expect(isMockAuthEnabled()).toBe(false);
    const loginRes = mockLogin('demo@vireoniq.com', 'Demo@1234');
    expect(loginRes.success).toBe(false);
    expect(loginRes.token).toBeUndefined();
    expect(loginRes.error).toMatch(/disabled/i);

    const regRes = mockRegister('new@vireoniq.com', 'Secret123!');
    expect(regRes.success).toBe(false);
    expect(regRes.error).toMatch(/disabled/i);
  });
});
