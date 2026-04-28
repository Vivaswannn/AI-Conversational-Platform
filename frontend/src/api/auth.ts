import type { UserOut } from '../types';

const BASE = import.meta.env.VITE_API_URL ?? '';

/** FastAPI can return `detail` as a string (app errors) OR an array of
 *  validation objects (422 Unprocessable Entity from Pydantic).
 *  This helper always returns a human-readable string.
 */
function extractDetail(body: unknown, fallback: string): string {
  if (!body || typeof body !== 'object') return fallback;
  const { detail } = body as Record<string, unknown>;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    // Each item: { loc: string[], msg: string, type: string }
    const first = detail[0] as Record<string, unknown>;
    if (typeof first.msg === 'string') return first.msg;
  }
  return fallback;
}

export async function register(email: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractDetail(body, 'Registration failed'));
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(extractDetail(body, 'Invalid email or password'));
  }
  return res.json();
}

export async function getMe(token: string): Promise<UserOut> {
  const res = await fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Unauthorized');
  return res.json();
}
