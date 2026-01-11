import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PositionCard } from '@/components/portfolio/position-card';
import type { OptionPosition } from '@/types/portfolio';

const mockItmPosition: OptionPosition = {
  id: 'pos-1',
  symbol: 'AAPL',
  optionType: 'call',
  strikePrice: 180,
  expirationDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  quantity: 5,
  premiumPaid: 3.5,
  purchaseDate: '2024-03-15',
  moneyStatus: 'itm',
  currentStockPrice: 185,
  currentOptionPrice: 8.5,
  intrinsicValue: 5,
  daysToExpiration: 7,
};

const mockOtmPosition: OptionPosition = {
  ...mockItmPosition,
  id: 'pos-2',
  moneyStatus: 'otm',
  currentStockPrice: 175,
  intrinsicValue: 0,
  currentOptionPrice: 1.5,
};

describe('PositionCard', () => {
  it('renders position symbol and type', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('CALL')).toBeInTheDocument();
  });

  it('displays strike price', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('$180 strike')).toBeInTheDocument();
  });

  it('shows ITM badge for ITM positions', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('ITM')).toBeInTheDocument();
  });

  it('shows OTM badge for OTM positions', () => {
    render(<PositionCard position={mockOtmPosition} />);

    expect(screen.getByText('OTM')).toBeInTheDocument();
  });

  it('displays current stock price', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('$185.00')).toBeInTheDocument();
  });

  it('displays intrinsic value for ITM positions', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('$5.00/share')).toBeInTheDocument();
  });

  it('calculates and displays profit/loss', () => {
    render(<PositionCard position={mockItmPosition} />);

    // P/L = (8.5 - 3.5) * 5 * 100 = $2,500
    expect(screen.getByText('$2,500.00')).toBeInTheDocument();
  });

  it('displays days to expiration', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('7 days')).toBeInTheDocument();
  });

  it('displays contract quantity', () => {
    render(<PositionCard position={mockItmPosition} />);

    expect(screen.getByText('5 contracts')).toBeInTheDocument();
    expect(screen.getByText('Long')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const onSelect = vi.fn();
    render(<PositionCard position={mockItmPosition} onSelect={onSelect} />);

    const card = screen.getByText('AAPL').closest('[class*="card"]');
    if (card) fireEvent.click(card);

    expect(onSelect).toHaveBeenCalledWith(mockItmPosition);
  });

  describe('compact mode', () => {
    it('renders compact version correctly', () => {
      render(<PositionCard position={mockItmPosition} compact />);

      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('$180 strike')).toBeInTheDocument();
    });

    it('shows chevron in compact mode', () => {
      render(<PositionCard position={mockItmPosition} compact />);

      // Chevron icon should be present
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });
  });

  describe('expiring soon warning', () => {
    it('highlights positions expiring within 7 days', () => {
      const expiringPosition: OptionPosition = {
        ...mockItmPosition,
        expirationDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      };

      render(<PositionCard position={expiringPosition} />);

      // Should show expiration warning styling
      expect(screen.getByText('3 days')).toBeInTheDocument();
    });

    it('shows TODAY for same-day expiration', () => {
      const expiringToday: OptionPosition = {
        ...mockItmPosition,
        expirationDate: new Date().toISOString().split('T')[0],
      };

      render(<PositionCard position={expiringToday} />);

      expect(screen.getByText('TODAY')).toBeInTheDocument();
    });

    it('shows TOMORROW for next-day expiration', () => {
      const expiringTomorrow: OptionPosition = {
        ...mockItmPosition,
        expirationDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      };

      render(<PositionCard position={expiringTomorrow} />);

      expect(screen.getByText('TOMORROW')).toBeInTheDocument();
    });
  });

  describe('short positions', () => {
    it('displays Short label for negative quantity', () => {
      const shortPosition: OptionPosition = {
        ...mockItmPosition,
        quantity: -3,
      };

      render(<PositionCard position={shortPosition} />);

      expect(screen.getByText('Short')).toBeInTheDocument();
      expect(screen.getByText('3 contracts')).toBeInTheDocument();
    });
  });

  describe('PUT options', () => {
    it('displays PUT badge for put options', () => {
      const putPosition: OptionPosition = {
        ...mockItmPosition,
        optionType: 'put',
      };

      render(<PositionCard position={putPosition} />);

      expect(screen.getByText('PUT')).toBeInTheDocument();
    });
  });
});
