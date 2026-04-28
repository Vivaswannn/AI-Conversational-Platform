import { beforeEach, describe, expect, it } from 'vitest';
import { useAuthStore } from '../store/authStore';

beforeEach(() => {
  localStorage.clear();
  useAuthStore.setState({ token: null, user: null });
});

describe('authStore', () => {
  it('starts with null token when localStorage is empty', () => {
    expect(useAuthStore.getState().token).toBeNull();
  });

  it('setToken persists token to localStorage', () => {
    useAuthStore.getState().setToken('abc123');
    expect(useAuthStore.getState().token).toBe('abc123');
    expect(localStorage.getItem('token')).toBe('abc123');
  });

  it('logout clears token and user', () => {
    useAuthStore.getState().setToken('abc123');
    useAuthStore.getState().setUser({ id: '1', email: 'a@b.com', is_active: true, created_at: '2024-01-01T00:00:00Z' });
    useAuthStore.getState().logout();
    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});
