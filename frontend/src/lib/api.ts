export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const AUTH_STORAGE_KEY = 'paperloom-auth';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);

    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    const token = parsed?.state?.token;

    return typeof token === 'string' && token ? token : null;
  } catch {
    return null;
  }
}

export function getStoredUsername(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);

    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    const username = parsed?.state?.username;

    return typeof username === 'string' && username ? username : null;
  } catch {
    return null;
  }
}

export function getAuthHeaders(): Record<string, string> {
  const token = getStoredToken();

  return token ? { Authorization: `Bearer ${token}` } : {};
}

const STATUS_MESSAGES: Record<number, string> = {
  401: 'Your session has expired. Please sign in again.',
  403: 'You do not have access to this resource.',
  404: 'The requested resource was not found.',
  413: 'File is too large. The maximum size is 50 MB.',
  415: 'Only PDF files are supported.',
};

export async function extractErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  let detail: unknown = null;

  try {
    const data = await response.json();

    if (typeof data?.detail === 'string') {
      detail = data.detail;
    } else if (Array.isArray(data?.detail) && data.detail.length > 0) {
      const first = data.detail[0] as { msg?: unknown } | null;

      if (first && typeof first.msg === 'string') {
        detail = first.msg;
      }
    }
  } catch {
    // Response body was not JSON; fall through to status-based message.
  }

  if (typeof detail === 'string' && detail.trim()) {
    if (response.status === 401) {
      return STATUS_MESSAGES[401];
    }

    return detail;
  }

  return STATUS_MESSAGES[response.status] ?? fallback;
}
