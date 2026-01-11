import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | string, decimals = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
}

export function formatPercent(value: number | string, decimals = 1): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return `${num >= 0 ? '+' : ''}${num.toFixed(decimals)}%`;
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(d);
}

export function daysUntil(date: string | Date): number {
  const d = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  d.setHours(0, 0, 0, 0);
  return Math.ceil((d.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

export function getMoneyStatusColor(status: 'itm' | 'atm' | 'otm' | null): string {
  switch (status) {
    case 'itm':
      return 'text-itm';
    case 'atm':
      return 'text-atm';
    case 'otm':
      return 'text-otm';
    default:
      return 'text-muted-foreground';
  }
}

export function getMoneyStatusBg(status: 'itm' | 'atm' | 'otm' | null): string {
  switch (status) {
    case 'itm':
      return 'bg-itm-muted border-itm';
    case 'atm':
      return 'bg-atm-muted border-atm';
    case 'otm':
      return 'bg-otm-muted border-otm';
    default:
      return 'bg-muted border-muted';
  }
}

export function getMoneyStatusLabel(status: 'itm' | 'atm' | 'otm' | null): string {
  switch (status) {
    case 'itm':
      return 'In The Money';
    case 'atm':
      return 'At The Money';
    case 'otm':
      return 'Out of The Money';
    default:
      return 'Unknown';
  }
}
