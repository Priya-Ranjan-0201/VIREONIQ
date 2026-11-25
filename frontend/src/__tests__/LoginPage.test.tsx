import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import api from '@/lib/axios';
import { LoginPage } from '@/pages/auth/LoginPage';
import { useAuthStore } from '@/store/authStore';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('@/lib/axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.getState().logout();
  });

  it('renders login form fields and does not expose mock credentials when disabled', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    expect(screen.getByLabelText(/work email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.queryByText(/dev mock mode active/i)).not.toBeInTheDocument();
  });

  it('authenticates against backend API and navigates to dashboard', async () => {
    const mockedPost = vi.mocked(api.post);
    const mockedGet = vi.mocked(api.get);
    mockedPost.mockResolvedValueOnce({ data: { access_token: 'real-jwt-123' } } as never);
    mockedGet.mockResolvedValueOnce({
      data: { id: 'u-9', email: 'user@vireoniq.com', full_name: 'Alice' },
    } as never);

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/work email/i), {
      target: { value: 'user@vireoniq.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'StrongPass!1' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockedPost).toHaveBeenCalledWith('/auth/login', {
        email: 'user@vireoniq.com',
        password: 'StrongPass!1',
      });
    });

    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
      expect(useAuthStore.getState().token).toBe('real-jwt-123');
      expect(mockNavigate).toHaveBeenCalledWith('/app/dashboard');
    });
  });
});
