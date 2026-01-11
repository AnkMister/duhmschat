'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn, formatCurrency, formatPercent, daysUntil, getMoneyStatusBg } from '@/lib/utils';
import type { OptionPosition } from '@/types/portfolio';
import { TrendingUp, TrendingDown, Clock, ChevronRight } from 'lucide-react';

interface PositionCardProps {
  position: OptionPosition;
  onSelect?: (position: OptionPosition) => void;
  compact?: boolean;
}

export function PositionCard({ position, onSelect, compact = false }: PositionCardProps) {
  const daysLeft = daysUntil(position.expirationDate);
  const isExpiringSoon = daysLeft <= 7 && daysLeft >= 0;
  const isExpired = daysLeft < 0;

  const profitLoss = position.currentOptionPrice
    ? (position.currentOptionPrice - position.premiumPaid) * position.quantity * 100
    : null;

  const profitLossPct = position.premiumPaid > 0 && position.currentOptionPrice
    ? ((position.currentOptionPrice - position.premiumPaid) / position.premiumPaid) * 100
    : null;

  const isProfit = profitLoss !== null && profitLoss >= 0;

  const statusVariant = position.moneyStatus === 'itm' ? 'itm' :
    position.moneyStatus === 'otm' ? 'otm' :
    position.moneyStatus === 'atm' ? 'atm' : 'outline';

  if (compact) {
    return (
      <button
        onClick={() => onSelect?.(position)}
        className={cn(
          'w-full text-left p-3 rounded-lg border transition-colors',
          'hover:bg-accent focus:outline-none focus:ring-2 focus:ring-ring',
          getMoneyStatusBg(position.moneyStatus ?? null)
        )}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{position.symbol}</span>
            <Badge variant={statusVariant} className="text-xs">
              {position.optionType.toUpperCase()}
            </Badge>
          </div>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex items-center justify-between mt-1 text-sm text-muted-foreground">
          <span>${position.strikePrice} strike</span>
          <span className={cn(isExpiringSoon && 'text-atm font-medium')}>
            {daysLeft}d left
          </span>
        </div>
      </button>
    );
  }

  return (
    <Card
      className={cn(
        'transition-all hover:shadow-md cursor-pointer',
        position.moneyStatus === 'itm' && 'border-itm border-2'
      )}
      onClick={() => onSelect?.(position)}
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold">{position.symbol}</span>
              <Badge variant={statusVariant}>
                {position.optionType.toUpperCase()}
              </Badge>
            </div>
            <div className="text-sm text-muted-foreground">
              ${position.strikePrice} strike
            </div>
          </div>
          <Badge
            variant={position.moneyStatus === 'itm' ? 'itm' :
              position.moneyStatus === 'otm' ? 'otm' : 'atm'}
          >
            {position.moneyStatus?.toUpperCase() || '?'}
          </Badge>
        </div>

        {/* Current Price vs Stock */}
        {position.currentStockPrice && (
          <div className="flex items-center justify-between text-sm mb-3">
            <span className="text-muted-foreground">Stock Price</span>
            <span className="font-medium">
              {formatCurrency(position.currentStockPrice)}
            </span>
          </div>
        )}

        {/* Intrinsic Value (for ITM) */}
        {position.intrinsicValue && position.intrinsicValue > 0 && (
          <div className="flex items-center justify-between text-sm mb-3">
            <span className="text-muted-foreground">Intrinsic Value</span>
            <span className="font-medium text-itm">
              {formatCurrency(position.intrinsicValue)}/share
            </span>
          </div>
        )}

        {/* P/L */}
        {profitLoss !== null && (
          <div className={cn(
            'flex items-center justify-between p-2 rounded-md mb-3',
            isProfit ? 'bg-itm-muted' : 'bg-otm-muted'
          )}>
            <div className="flex items-center gap-1">
              {isProfit ? (
                <TrendingUp className="h-4 w-4 text-itm" />
              ) : (
                <TrendingDown className="h-4 w-4 text-otm" />
              )}
              <span className="text-sm">P/L</span>
            </div>
            <div className="text-right">
              <span className={cn(
                'font-semibold',
                isProfit ? 'text-itm' : 'text-otm'
              )}>
                {formatCurrency(profitLoss)}
              </span>
              {profitLossPct !== null && (
                <span className={cn(
                  'text-xs ml-1',
                  isProfit ? 'text-itm' : 'text-otm'
                )}>
                  ({formatPercent(profitLossPct)})
                </span>
              )}
            </div>
          </div>
        )}

        {/* Expiration */}
        <div className={cn(
          'flex items-center justify-between text-sm p-2 rounded-md',
          isExpired ? 'bg-otm-muted' :
            isExpiringSoon ? 'bg-atm-muted' : 'bg-muted'
        )}>
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>Expires</span>
          </div>
          <span className={cn(
            'font-medium',
            isExpired ? 'text-otm' :
              isExpiringSoon ? 'text-atm' : ''
          )}>
            {isExpired ? 'EXPIRED' :
              daysLeft === 0 ? 'TODAY' :
                daysLeft === 1 ? 'TOMORROW' :
                  `${daysLeft} days`}
          </span>
        </div>

        {/* Quantity */}
        <div className="flex items-center justify-between text-sm mt-3 text-muted-foreground">
          <span>{Math.abs(position.quantity)} contract{Math.abs(position.quantity) !== 1 ? 's' : ''}</span>
          <span>{position.quantity > 0 ? 'Long' : 'Short'}</span>
        </div>
      </CardContent>
    </Card>
  );
}
