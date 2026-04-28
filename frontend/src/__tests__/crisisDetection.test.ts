import { describe, expect, it } from 'vitest';

function isCrisisResponse(content: string): boolean {
  return content.includes('988');
}

describe('crisis detection', () => {
  it('detects 988 hotline in response', () => {
    expect(isCrisisResponse('Please call 988 for immediate support')).toBe(true);
  });

  it('does not flag normal responses', () => {
    expect(isCrisisResponse('I hear you and I am here to help.')).toBe(false);
  });

  it('detects 988 anywhere in the string', () => {
    expect(isCrisisResponse('National Suicide Prevention Lifeline: 988.')).toBe(true);
  });
});
