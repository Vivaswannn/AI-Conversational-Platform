import { beforeEach, describe, expect, it, vi } from 'vitest';

function relativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const days = Math.floor(diffMs / 86_400_000);
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return date.toLocaleDateString('en-US', { weekday: 'short' });
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

describe('relativeDate', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-04-19T12:00:00Z'));
  });

  it('returns Today for same day', () => {
    expect(relativeDate('2026-04-19T08:00:00Z')).toBe('Today');
  });

  it('returns Yesterday for previous day', () => {
    expect(relativeDate('2026-04-18T08:00:00Z')).toBe('Yesterday');
  });

  it('returns weekday name for within a week', () => {
    const result = relativeDate('2026-04-15T08:00:00Z');
    expect(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']).toContain(result);
  });

  it('returns month + day for older dates', () => {
    expect(relativeDate('2026-03-01T08:00:00Z')).toMatch(/Mar \d+/);
  });
});
