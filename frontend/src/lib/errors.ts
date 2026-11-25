import axios from 'axios';

interface ApiErrorPayload {
  detail?: string;
}

export function isNetworkError(error: unknown): boolean {
  return axios.isAxiosError(error) ? !error.response : !(error && typeof error === 'object' && 'response' in error && (error as { response?: unknown }).response);
}

export function extractApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
  } else if (error && typeof error === 'object' && 'response' in error) {
    const resp = (error as { response?: { data?: { detail?: unknown } } }).response;
    const detail = resp?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
  }
  return fallback;
}
