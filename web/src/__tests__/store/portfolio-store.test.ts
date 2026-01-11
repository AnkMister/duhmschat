import { describe, it, expect, beforeEach } from 'vitest';
import { usePortfolioStore } from '@/store/portfolio-store';
import type { OptionPosition, Alert, AlertRule } from '@/types/portfolio';

// Reset store before each test
beforeEach(() => {
  usePortfolioStore.setState({
    positions: [],
    isLoading: false,
    error: null,
    summary: null,
    alerts: [],
    rules: [],
    actionItems: [],
    lastRefresh: null,
  });
});

describe('Portfolio Store - Positions', () => {
  const mockPosition: OptionPosition = {
    id: 'pos-1',
    symbol: 'AAPL',
    optionType: 'call',
    strikePrice: 180,
    expirationDate: '2024-04-19',
    quantity: 5,
    premiumPaid: 3.5,
    purchaseDate: '2024-03-15',
    moneyStatus: 'itm',
    currentStockPrice: 185,
    intrinsicValue: 5,
  };

  it('adds a position correctly', () => {
    const { addPosition, positions } = usePortfolioStore.getState();
    addPosition(mockPosition);

    expect(usePortfolioStore.getState().positions).toHaveLength(1);
    expect(usePortfolioStore.getState().positions[0]).toEqual(mockPosition);
  });

  it('sets multiple positions correctly', () => {
    const positions = [
      mockPosition,
      { ...mockPosition, id: 'pos-2', symbol: 'MSFT' },
    ];

    usePortfolioStore.getState().setPositions(positions);

    expect(usePortfolioStore.getState().positions).toHaveLength(2);
  });

  it('updates a position correctly', () => {
    usePortfolioStore.getState().addPosition(mockPosition);
    usePortfolioStore.getState().updatePosition('pos-1', { currentStockPrice: 190 });

    const updated = usePortfolioStore.getState().positions[0];
    expect(updated.currentStockPrice).toBe(190);
    expect(updated.symbol).toBe('AAPL'); // Other fields unchanged
  });

  it('removes a position correctly', () => {
    usePortfolioStore.getState().addPosition(mockPosition);
    usePortfolioStore.getState().removePosition('pos-1');

    expect(usePortfolioStore.getState().positions).toHaveLength(0);
  });

  it('getItmPositions returns only ITM positions', () => {
    const otmPosition = { ...mockPosition, id: 'pos-2', moneyStatus: 'otm' as const };

    usePortfolioStore.getState().setPositions([mockPosition, otmPosition]);

    const itm = usePortfolioStore.getState().getItmPositions();
    expect(itm).toHaveLength(1);
    expect(itm[0].id).toBe('pos-1');
  });

  it('getOtmPositions returns only OTM positions', () => {
    const otmPosition = { ...mockPosition, id: 'pos-2', moneyStatus: 'otm' as const };

    usePortfolioStore.getState().setPositions([mockPosition, otmPosition]);

    const otm = usePortfolioStore.getState().getOtmPositions();
    expect(otm).toHaveLength(1);
    expect(otm[0].id).toBe('pos-2');
  });

  it('getExpiringPositions returns positions within specified days', () => {
    const today = new Date();
    const in5Days = new Date(today.getTime() + 5 * 24 * 60 * 60 * 1000);
    const in20Days = new Date(today.getTime() + 20 * 24 * 60 * 60 * 1000);

    const expiringPosition = {
      ...mockPosition,
      id: 'pos-1',
      expirationDate: in5Days.toISOString().split('T')[0],
    };

    const farPosition = {
      ...mockPosition,
      id: 'pos-2',
      expirationDate: in20Days.toISOString().split('T')[0],
    };

    usePortfolioStore.getState().setPositions([expiringPosition, farPosition]);

    const expiring7 = usePortfolioStore.getState().getExpiringPositions(7);
    expect(expiring7).toHaveLength(1);
    expect(expiring7[0].id).toBe('pos-1');
  });
});

describe('Portfolio Store - Alerts', () => {
  const mockAlert: Alert = {
    id: 'alert-1',
    ruleId: 'rule-1',
    ruleName: 'ITM Alert',
    positionId: 'pos-1',
    symbol: 'AAPL',
    alertType: 'itm_alert',
    message: 'AAPL CALL is ITM',
    priority: 4,
    createdAt: '2024-03-15T10:00:00Z',
    acknowledged: false,
  };

  it('sets alerts correctly', () => {
    usePortfolioStore.getState().setAlerts([mockAlert]);

    expect(usePortfolioStore.getState().alerts).toHaveLength(1);
  });

  it('acknowledges an alert correctly', () => {
    usePortfolioStore.getState().setAlerts([mockAlert]);
    usePortfolioStore.getState().acknowledgeAlert('alert-1');

    const alert = usePortfolioStore.getState().alerts[0];
    expect(alert.acknowledged).toBe(true);
    expect(alert.acknowledgedAt).toBeDefined();
  });

  it('clears acknowledged alerts', () => {
    const unacknowledgedAlert = { ...mockAlert, id: 'alert-2' };

    usePortfolioStore.getState().setAlerts([
      { ...mockAlert, acknowledged: true },
      unacknowledgedAlert,
    ]);

    usePortfolioStore.getState().clearAcknowledgedAlerts();

    const alerts = usePortfolioStore.getState().alerts;
    expect(alerts).toHaveLength(1);
    expect(alerts[0].id).toBe('alert-2');
  });
});

describe('Portfolio Store - Rules', () => {
  const mockRule: AlertRule = {
    id: 'rule-1',
    name: 'ITM Alert',
    ruleType: 'itm_alert',
    enabled: true,
    priority: 4,
    createdAt: '2024-03-15T10:00:00Z',
  };

  it('adds a rule correctly', () => {
    usePortfolioStore.getState().addRule(mockRule);

    expect(usePortfolioStore.getState().rules).toHaveLength(1);
  });

  it('updates a rule correctly', () => {
    usePortfolioStore.getState().addRule(mockRule);
    usePortfolioStore.getState().updateRule('rule-1', { enabled: false });

    const rule = usePortfolioStore.getState().rules[0];
    expect(rule.enabled).toBe(false);
    expect(rule.name).toBe('ITM Alert'); // Other fields unchanged
  });

  it('removes a rule correctly', () => {
    usePortfolioStore.getState().addRule(mockRule);
    usePortfolioStore.getState().removeRule('rule-1');

    expect(usePortfolioStore.getState().rules).toHaveLength(0);
  });
});

describe('Portfolio Store - Loading State', () => {
  it('sets loading state correctly', () => {
    usePortfolioStore.getState().setLoading(true);
    expect(usePortfolioStore.getState().isLoading).toBe(true);

    usePortfolioStore.getState().setLoading(false);
    expect(usePortfolioStore.getState().isLoading).toBe(false);
  });

  it('sets error state correctly', () => {
    usePortfolioStore.getState().setError('Something went wrong');
    expect(usePortfolioStore.getState().error).toBe('Something went wrong');

    usePortfolioStore.getState().setError(null);
    expect(usePortfolioStore.getState().error).toBeNull();
  });

  it('sets last refresh correctly', () => {
    const timestamp = '2024-03-15T10:00:00Z';
    usePortfolioStore.getState().setLastRefresh(timestamp);

    expect(usePortfolioStore.getState().lastRefresh).toBe(timestamp);
  });
});
