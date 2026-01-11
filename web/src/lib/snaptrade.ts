/**
 * SnapTrade API Integration
 *
 * SnapTrade provides secure OAuth-based connections to brokerages.
 * This module handles user registration, connection, and data fetching.
 *
 * Documentation: https://docs.snaptrade.com/
 */

const SNAPTRADE_API_URL = 'https://api.snaptrade.com/api/v1';

interface SnapTradeConfig {
  clientId: string;
  consumerKey: string;
}

interface SnapTradeUser {
  userId: string;
  userSecret: string;
}

interface BrokerageAuthorization {
  id: string;
  brokerage: {
    id: string;
    name: string;
    slug: string;
  };
  accounts: Array<{
    id: string;
    number: string;
    name: string;
  }>;
}

interface HoldingPosition {
  symbol: {
    id: string;
    symbol: string;
    rawSymbol: string;
    description: string;
    currency: { id: string; code: string };
    exchange: { id: string; code: string; name: string };
    type: { id: string; code: string; description: string };
  };
  units: number;
  price: number;
  openPnl: number;
  fractionalUnits: number;
}

interface OptionPosition {
  symbol: {
    id: string;
    symbol: string;
    rawSymbol: string;
    optionSymbol?: {
      id: string;
      ticker: string;
      optionType: 'CALL' | 'PUT';
      strikePrice: number;
      expirationDate: string;
    };
  };
  units: number;
  price: number;
  openPnl: number;
}

class SnapTradeClient {
  private clientId: string;
  private consumerKey: string;

  constructor(config: SnapTradeConfig) {
    this.clientId = config.clientId;
    this.consumerKey = config.consumerKey;
  }

  private generateSignature(timestamp: string): string {
    // In production, use crypto to generate HMAC-SHA256 signature
    // signature = HMAC-SHA256(consumerKey, clientId + timestamp)
    // For now, return placeholder (implement with crypto)
    return `${this.consumerKey}_${timestamp}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const signature = this.generateSignature(timestamp);

    const response = await fetch(`${SNAPTRADE_API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Signature': signature,
        'Timestamp': timestamp,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `SnapTrade API error: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Register a new user with SnapTrade
   */
  async registerUser(userId: string): Promise<SnapTradeUser> {
    return this.request<SnapTradeUser>('/snapTrade/registerUser', {
      method: 'POST',
      body: JSON.stringify({ userId }),
    });
  }

  /**
   * Get login link for user to connect brokerage
   */
  async getLoginLink(
    userId: string,
    userSecret: string,
    broker?: string
  ): Promise<{ loginLink: string }> {
    const params = new URLSearchParams({
      userId,
      userSecret,
      ...(broker && { broker }),
    });

    return this.request(`/snapTrade/login?${params}`);
  }

  /**
   * List connected brokerage authorizations
   */
  async listAuthorizations(
    userId: string,
    userSecret: string
  ): Promise<BrokerageAuthorization[]> {
    const params = new URLSearchParams({ userId, userSecret });
    return this.request(`/authorizations?${params}`);
  }

  /**
   * Get account holdings including options
   */
  async getHoldings(
    userId: string,
    userSecret: string,
    accountId: string
  ): Promise<{ positions: HoldingPosition[]; optionPositions: OptionPosition[] }> {
    const params = new URLSearchParams({ userId, userSecret });
    return this.request(`/accounts/${accountId}/holdings?${params}`);
  }

  /**
   * Get account options positions
   */
  async getOptionsPositions(
    userId: string,
    userSecret: string,
    accountId: string
  ): Promise<OptionPosition[]> {
    const params = new URLSearchParams({ userId, userSecret });
    return this.request(`/accounts/${accountId}/options?${params}`);
  }

  /**
   * Delete user and all connections
   */
  async deleteUser(userId: string): Promise<void> {
    await this.request(`/snapTrade/deleteUser`, {
      method: 'DELETE',
      body: JSON.stringify({ userId }),
    });
  }

  /**
   * Refresh account data
   */
  async refreshAccount(
    userId: string,
    userSecret: string,
    accountId: string
  ): Promise<void> {
    const params = new URLSearchParams({ userId, userSecret });
    await this.request(`/accounts/${accountId}/refresh?${params}`, {
      method: 'POST',
    });
  }
}

// Export singleton instance
let client: SnapTradeClient | null = null;

export function getSnapTradeClient(): SnapTradeClient {
  if (!client) {
    const clientId = process.env.SNAPTRADE_CLIENT_ID;
    const consumerKey = process.env.SNAPTRADE_CONSUMER_KEY;

    if (!clientId || !consumerKey) {
      throw new Error('SnapTrade credentials not configured');
    }

    client = new SnapTradeClient({ clientId, consumerKey });
  }

  return client;
}

export type {
  SnapTradeUser,
  BrokerageAuthorization,
  HoldingPosition,
  OptionPosition,
};
