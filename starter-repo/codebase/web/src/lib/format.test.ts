import { describe, expect, it } from 'vitest';
import { formatVnd, formatVndShort, groupDigits, parseVnd } from './format';

describe('format', () => {
  it('formats full VND with dots', () => expect(formatVnd(1250000)).toBe('1.250.000đ'));
  it('formats short', () => {
    expect(formatVndShort(146_200_000)).toBe('146,2 tr');
    expect(formatVndShort(1_200_000_000)).toBe('1,2 tỷ');
  });
  it('parses and groups typed digits', () => {
    expect(parseVnd('150.000.000')).toBe(150_000_000);
    expect(parseVnd('')).toBeNull();
    expect(groupDigits('150000000')).toBe('150.000.000');
  });
});
