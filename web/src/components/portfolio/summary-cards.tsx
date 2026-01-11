'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn, formatCurrency, formatPercent } from '@/lib/utils';
import type { PortfolioSummary } from '@/types/portfolio';
import {
  Target,
  TrendingUp,
  TrendingDown,
  Clock,
  Bell,
  PieChart,
} from 'lucide-react';

interface SummaryCardsProps {
  summary: PortfolioSummary | null;
  isLoading?: boolean;
}

export function SummaryCards({ summary, isLoading }: SummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-muted rounded w-24" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const isProfit = (summary.totalProfitLoss ?? 0) >= 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* ITM Positions */}
      <Card className={cn(
        'border-2',
        summary.itmCount > 0 ? 'border-itm bg-itm-muted/50' : ''
      )}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">In The Money</CardTitle>
          <Target className={cn(
            'h-4 w-4',
            summary.itmCount > 0 ? 'text-itm' : 'text-muted-foreground'
          )} />
        </CardHeader>
        <CardContent>
          <div className={cn(
            'text-2xl font-bold',
            summary.itmCount > 0 ? 'text-itm' : ''
          )}>
            {summary.itmCount}
          </div>
          <p className="text-xs text-muted-foreground">
            of {summary.totalPositions} positions
          </p>
        </CardContent>
      </Card>

      {/* Total P/L */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total P/L</CardTitle>
          {isProfit ? (
            <TrendingUp className="h-4 w-4 text-itm" />
          ) : (
            <TrendingDown className="h-4 w-4 text-otm" />
          )}
        </CardHeader>
        <CardContent>
          <div className={cn(
            'text-2xl font-bold',
            isProfit ? 'text-itm' : 'text-otm'
          )}>
            {summary.totalProfitLoss != null
              ? formatCurrency(summary.totalProfitLoss)
              : 'N/A'}
          </div>
          {summary.totalProfitLossPct != null && (
            <p className={cn(
              'text-xs',
              isProfit ? 'text-itm' : 'text-otm'
            )}>
              {formatPercent(summary.totalProfitLossPct)}
            </p>
          )}
        </CardContent>
      </Card>

      {/* Expiring Soon */}
      <Card className={cn(
        summary.expiringThisWeek > 0 ? 'border-atm border-2' : ''
      )}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
          <Clock className={cn(
            'h-4 w-4',
            summary.expiringThisWeek > 0 ? 'text-atm' : 'text-muted-foreground'
          )} />
        </CardHeader>
        <CardContent>
          <div className={cn(
            'text-2xl font-bold',
            summary.expiringThisWeek > 0 ? 'text-atm' : ''
          )}>
            {summary.expiringThisWeek}
          </div>
          <p className="text-xs text-muted-foreground">
            within 7 days
          </p>
        </CardContent>
      </Card>

      {/* Alerts */}
      <Card className={cn(
        summary.unacknowledgedAlerts > 0 ? 'border-otm border-2' : ''
      )}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Alerts</CardTitle>
          <Bell className={cn(
            'h-4 w-4',
            summary.unacknowledgedAlerts > 0 ? 'text-otm' : 'text-muted-foreground'
          )} />
        </CardHeader>
        <CardContent>
          <div className={cn(
            'text-2xl font-bold',
            summary.unacknowledgedAlerts > 0 ? 'text-otm' : ''
          )}>
            {summary.unacknowledgedAlerts}
          </div>
          <p className="text-xs text-muted-foreground">
            need attention
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

interface BreakdownCardProps {
  summary: PortfolioSummary;
}

export function BreakdownCard({ summary }: BreakdownCardProps) {
  const total = summary.totalPositions || 1;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Portfolio Breakdown</CardTitle>
        <PieChart className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent className="space-y-4">
        {/* ITM/ATM/OTM */}
        <div>
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Status</span>
            <span>ITM: {summary.itmCount} | ATM: {summary.atmCount} | OTM: {summary.otmCount}</span>
          </div>
          <div className="flex h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="bg-itm transition-all"
              style={{ width: `${(summary.itmCount / total) * 100}%` }}
            />
            <div
              className="bg-atm transition-all"
              style={{ width: `${(summary.atmCount / total) * 100}%` }}
            />
            <div
              className="bg-otm transition-all"
              style={{ width: `${(summary.otmCount / total) * 100}%` }}
            />
          </div>
        </div>

        {/* Calls/Puts */}
        <div>
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Type</span>
            <span>Calls: {summary.callsCount} | Puts: {summary.putsCount}</span>
          </div>
          <div className="flex h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="bg-blue-500 transition-all"
              style={{ width: `${(summary.callsCount / total) * 100}%` }}
            />
            <div
              className="bg-purple-500 transition-all"
              style={{ width: `${(summary.putsCount / total) * 100}%` }}
            />
          </div>
        </div>

        {/* Long/Short */}
        <div>
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Direction</span>
            <span>Long: {summary.longCount} | Short: {summary.shortCount}</span>
          </div>
          <div className="flex h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="bg-green-500 transition-all"
              style={{ width: `${(summary.longCount / total) * 100}%` }}
            />
            <div
              className="bg-red-500 transition-all"
              style={{ width: `${(summary.shortCount / total) * 100}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
