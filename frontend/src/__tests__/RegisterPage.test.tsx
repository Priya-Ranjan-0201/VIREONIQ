import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import api from '@/lib/axios';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { toast } from 'sonner';

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
  },
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('rejects weak passwords client-side without calling backend', async () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/work email/i), {
      target: { value: 'student@vireoniq.com' },
    });
    fireEvent.change(screen.getByLabelText(/secure password/i), {
      target: { value: 'weak' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register securely/i }));

    expect(vi.mocked(api.post)).not.toHaveBeenCalled();
    expect(vi.mocked(toast.error)).toHaveBeenCalledWith(
      expect.stringMatching(/8\+ chars/i),
    );
  });

  it('submits strong password registration and redirects to login', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({ data: { id: 'u-1' } } as never);

    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText(/work email/i), {
      target: { value: 'student@vireoniq.com' },
    });
    fireEvent.change(screen.getByLabelText(/secure password/i), {
      target: { value: 'StrongPass!1' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register securely/i }));

    await waitFor(() => {
      expect(vi.mocked(api.post)).toHaveBeenCalledWith('/auth/register', {
        email: 'student@vireoniq.com',
        password: 'StrongPass!1',
        role_name: 'User',
      });
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});
