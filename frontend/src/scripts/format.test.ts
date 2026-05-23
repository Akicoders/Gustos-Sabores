import { describe, it, expect } from 'vitest';
import { formatMoney } from './format';

describe('formatMoney', () => {
  it('formats a number with two decimals', () => {
    expect(formatMoney(28)).toContain('28.00');
  });

  it('uses a thousands separator', () => {
    expect(formatMoney(1234.5)).toContain('1,234.50');
  });

  it('falls back to zero for non-finite values', () => {
    expect(formatMoney(Number.NaN)).toBe(formatMoney(0));
    expect(formatMoney(Number.POSITIVE_INFINITY)).toBe(formatMoney(0));
  });
});
