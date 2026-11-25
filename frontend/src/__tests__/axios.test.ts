import { describe, it, expect, beforeEach } from 'vitest';
import api from '@/lib/axios';
import { useAuthStore } from '@/store/authStore';

describe('axios client interceptors', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
  });

  it('attaches Authorization Bearer header when token exists in store', async () => {
    useAuthStore.getState().setAuth(
      { id: 'u-1', email: 'dev@vireoniq.com' },
      'secret-access-token',
    );

    const requestHandlers = (api.interceptors.request as unknown as {
      handlers: Array<{ fulfilled?: (cfg: { headers: Record<string, string> }) => { headers: Record<string, string> } }>;
    }).handlers;

    const handler = requestHandlers.find((h) => typeof h?.fulfilled === 'function')?.fulfilled;
    expect(handler).toBeDefined();

    const updatedConfig = handler!({ headers: {} });
    expect(updatedConfig.headers.Authorization).toBe('Bearer secret-access-token');
  });

  it('does not attach Authorization header when unauthenticated', () => {
    const requestHandlers = (api.interceptors.request as unknown as {
      handlers: Array<{ fulfilled?: (cfg: { headers: Record<string, string> }) => { headers: Record<string, string> } }>;
    }).handlers;

    const handler = requestHandlers.find((h) => typeof h?.fulfilled === 'function')?.fulfilled;
    const updatedConfig = handler!({ headers: {} });
    expect(updatedConfig.headers.Authorization).toBeUndefined();
  });

  it('clears auth store on HTTP 401 response error', async () => {
    useAuthStore.getState().setAuth(
      { id: 'u-1', email: 'dev@vireoniq.com' },
      'expired-token',
    );

    const responseHandlers = (api.interceptors.response as unknown as {
      handlers: Array<{ rejected?: (err: unknown) => Promise<never> }>;
    }).handlers;

    const rejectHandler = responseHandlers.find((h) => typeof h?.rejected === 'function')?.rejected;
    expect(rejectHandler).toBeDefined();

    await expect(rejectHandler!({ response: { status: 401 } })).rejects.toEqual({
      response: { status: 401 },
    });

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().token).toBeNull();
  });
});
