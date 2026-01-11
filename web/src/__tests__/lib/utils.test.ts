import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  cn,
  formatCurrency,
  formatPercent,
  formatDate,
  daysUntil,
  getMoneyStatusColor,
  getMoneyStatusBg,
  getMoneyStatusLabel,
} from '@/lib/utils';

describe('cn (className merge)', () => {
  it('merges class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz');
  });

  it('merges tailwind classes correctly', () => {
    expect(cn('p-4', 'p-6')).toBe('p-6');
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500');
  });

  it('handles arrays and objects', () => {
    expect(cn(['foo', 'bar'], { baz: true, qux: false })).toBe('foo bar baz');
  });
});

describe('formatCurrency', () => {
  it('formats positive numbers correctly', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('formats negative numbers correctly', () => {
    expect(formatCurrency(-1234.56)).toBe('-$1,234.56');
  });

  it('formats zero correctly', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('handles string input', () => {
    expect(formatCurrency('1234.56')).toBe('$1,234.56');
  });

  it('respects decimal places parameter', () => {
    expect(formatCurrency(1234.567, 3)).toBe('$1,234.567');
    expect(formatCurrency(1234.5, 0)).toBe('$1,235');
  });

  it('formats large numbers correctly', () => {
    expect(formatCurrency(1000000)).toBe('$1,000,000.00');
  });

  it('formats small decimals correctly', () => {
    expect(formatCurrency(0.05)).toBe('$0.05');
  });
});

describe('formatPercent', () => {
  it('formats positive percentages with + sign', () => {
    expect(formatPercent(15.5)).toBe('+15.5%');
  });

  it('formats negative percentages correctly', () => {
    expect(formatPercent(-15.5)).toBe('-15.5%');
  });

  it('formats zero correctly', () => {
    expect(formatPercent(0)).toBe('+0.0%');
  });

  it('handles string input', () => {
    expect(formatPercent('15.5')).toBe('+15.5%');
  });

  it('respects decimal places parameter', () => {
    expect(formatPercent(15.567, 2)).toBe('+15.57%');
    expect(formatPercent(15.567, 0)).toBe('+16%');
  });
});

describe('formatDate', () => {
  it('formats date string correctly', () => {
    expect(formatDate('2024-03-15')).toBe('Mar 15, 2024');
  });

  it('formats Date object correctly', () => {
    expect(formatDate(new Date(2024, 2, 15))).toBe('Mar 15, 2024');
  });

  it('handles different months', () => {
    expect(formatDate('2024-01-01')).toBe('Jan 1, 2024');
    expect(formatDate('2024-12-31')).toBe('Dec 31, 2024');
  });
});

describe('daysUntil', () => {
  beforeEach(() => {
    // Mock current date to 2024-03-15
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2024, 2, 15));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('calculates days until future date', () => {
    expect(daysUntil('2024-03-22')).toBe(7);
  });

  it('returns 0 for today', () => {
    expect(daysUntil('2024-03-15')).toBe(0);
  });

  it('returns negative for past dates', () => {
    expect(daysUntil('2024-03-08')).toBe(-7);
  });

  it('handles Date objects', () => {
    expect(daysUntil(new Date(2024, 2, 22))).toBe(7);
  });
});

describe('getMoneyStatusColor', () => {
  it('returns correct color for ITM', () => {
    expect(getMoneyStatusColor('itm')).toBe('text-itm');
  });

  it('returns correct color for ATM', () => {
    expect(getMoneyStatusColor('atm')).toBe('text-atm');
  });

  it('returns correct color for OTM', () => {
    expect(getMoneyStatusColor('otm')).toBe('text-otm');
  });

  it('returns muted color for null', () => {
    expect(getMoneyStatusColor(null)).toBe('text-muted-foreground');
  });
});

describe('getMoneyStatusBg', () => {
  it('returns correct background for ITM', () => {
    expect(getMoneyStatusBg('itm')).toBe('bg-itm-muted border-itm');
  });

  it('returns correct background for ATM', () => {
    expect(getMoneyStatusBg('atm')).toBe('bg-atm-muted border-atm');
  });

  it('returns correct background for OTM', () => {
    expect(getMoneyStatusBg('otm')).toBe('bg-otm-muted border-otm');
  });

  it('returns muted background for null', () => {
    expect(getMoneyStatusBg(null)).toBe('bg-muted border-muted');
  });
});

describe('getMoneyStatusLabel', () => {
  it('returns correct label for ITM', () => {
    expect(getMoneyStatusLabel('itm')).toBe('In The Money');
  });

  it('returns correct label for ATM', () => {
    expect(getMoneyStatusLabel('atm')).toBe('At The Money');
  });

  it('returns correct label for OTM', () => {
    expect(getMoneyStatusLabel('otm')).toBe('Out of The Money');
  });

  it('returns Unknown for null', () => {
    expect(getMoneyStatusLabel(null)).toBe('Unknown');
  });
});
