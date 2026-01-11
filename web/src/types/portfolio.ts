/**
 * Option Types and Portfolio Data Models
 */

export type OptionType = 'call' | 'put';
export type MoneyStatus = 'itm' | 'atm' | 'otm';
export type RuleType =
  | 'itm_alert'
  | 'otm_alert'
  | 'expiration_warning'
  | 'profit_target'
  | 'stop_loss'
  | 'price_threshold'
  | 'intrinsic_value';

export interface OptionPosition {
  id: string;
  symbol: string;
  optionType: OptionType;
  strikePrice: number;
  expirationDate: string; // ISO date string
  quantity: number;
  premiumPaid: number;
  purchaseDate: string;

  // Calculated fields (populated after analysis)
  currentStockPrice?: number;
  currentOptionPrice?: number;
  moneyStatus?: MoneyStatus;
  intrinsicValue?: number;
  timeValue?: number;
  daysToExpiration?: number;

  // Greeks (if available)
  delta?: number;
  gamma?: number;
  theta?: number;
  vega?: number;
  impliedVolatility?: number;
}

export interface PortfolioSummary {
  totalPositions: number;
  totalContracts: number;

  itmCount: number;
  atmCount: number;
  otmCount: number;

  callsCount: number;
  putsCount: number;
  longCount: number;
  shortCount: number;

  totalCostBasis: number;
  totalCurrentValue?: number;
  totalProfitLoss?: number;
  totalProfitLossPct?: number;

  totalIntrinsicValue: number;
  totalTimeValue?: number;

  expiringThisWeek: number;
  expiringThisMonth: number;

  activeAlerts: number;
  unacknowledgedAlerts: number;

  lastUpdated: string;
}

export interface AlertRule {
  id: string;
  name: string;
  ruleType: RuleType;
  enabled: boolean;

  thresholdValue?: number;
  thresholdDays?: number;
  thresholdPct?: number;

  applyToSymbols?: string[];
  applyToOptionType?: OptionType;

  priority: number; // 1-5
  notificationMessage?: string;

  createdAt: string;
  lastTriggered?: string;
}

export interface Alert {
  id: string;
  ruleId: string;
  ruleName: string;
  positionId: string;
  symbol: string;

  alertType: RuleType;
  message: string;
  priority: number;

  currentValue?: number;
  thresholdValue?: number;

  createdAt: string;
  acknowledged: boolean;
  acknowledgedAt?: string;
}

export interface ActionItem {
  priority: number;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  position: string;
  action: string;
  reason: string;
}

export interface BrokerageConnection {
  id: string;
  provider: string; // e.g., 'snaptrade', 'schwab'
  accountId: string;
  accountName: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSync?: string;
  error?: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
