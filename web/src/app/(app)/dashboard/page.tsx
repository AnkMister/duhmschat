'use client';

import { useEffect } from 'react';
import { Header } from '@/components/layout/header';
import { SummaryCards, BreakdownCard } from '@/components/portfolio/summary-cards';
import { PositionCard } from '@/components/portfolio/position-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { usePortfolioStore } from '@/store/portfolio-store';
import { cn } from '@/lib/utils';
import { Target, Clock, AlertTriangle, ChevronRight, Plus } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const {
    positions,
    summary,
    actionItems,
    isLoading,
    setLoading,
    setLastRefresh,
  } = usePortfolioStore();

  const itmPositions = positions.filter((p) => p.moneyStatus === 'itm');
  const expiringPositions = positions.filter((p) => {
    const days = Math.ceil(
      (new Date(p.expirationDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    );
    return days >= 0 && days <= 7;
  });

  const handleRefresh = async () => {
    setLoading(true);
    // TODO: Call API to refresh prices
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLastRefresh(new Date().toISOString());
    setLoading(false);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header title="Dashboard" onRefresh={handleRefresh} />

      <main className="flex-1 p-4 space-y-6">
        {/* Summary Cards */}
        <SummaryCards summary={summary} isLoading={isLoading} />

        {/* Empty State */}
        {positions.length === 0 && !isLoading && (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Target className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Positions Yet</h3>
              <p className="text-muted-foreground text-center mb-4">
                Add your first options position or connect your brokerage to get started.
              </p>
              <div className="flex gap-2">
                <Button asChild>
                  <Link href="/add">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Position
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/connect">Connect Brokerage</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* ITM Positions */}
        {itmPositions.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-itm" />
                <h2 className="text-lg font-semibold">In The Money</h2>
                <Badge variant="itm">{itmPositions.length}</Badge>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/positions?status=itm">
                  View All <ChevronRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {itmPositions.slice(0, 3).map((position) => (
                <PositionCard key={position.id} position={position} />
              ))}
            </div>
          </section>
        )}

        {/* Expiring Soon */}
        {expiringPositions.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-atm" />
                <h2 className="text-lg font-semibold">Expiring Soon</h2>
                <Badge variant="atm">{expiringPositions.length}</Badge>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/positions?expiring=7">
                  View All <ChevronRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </div>
            <div className="space-y-2">
              {expiringPositions.slice(0, 3).map((position) => (
                <PositionCard key={position.id} position={position} compact />
              ))}
            </div>
          </section>
        )}

        {/* Action Items */}
        {actionItems.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="h-5 w-5 text-atm" />
              <h2 className="text-lg font-semibold">Action Items</h2>
            </div>
            <Card>
              <CardContent className="p-0 divide-y">
                {actionItems.slice(0, 5).map((item, index) => (
                  <div
                    key={index}
                    className={cn(
                      'p-4',
                      item.urgency === 'critical' && 'bg-otm-muted/50',
                      item.urgency === 'high' && 'bg-atm-muted/50'
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              item.urgency === 'critical' || item.urgency === 'high'
                                ? 'destructive'
                                : 'secondary'
                            }
                          >
                            {item.urgency.toUpperCase()}
                          </Badge>
                          <span className="font-medium">{item.position}</span>
                        </div>
                        <p className="text-sm mt-1">{item.action}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {item.reason}
                        </p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>
        )}

        {/* Portfolio Breakdown */}
        {positions.length > 0 && summary && (
          <section>
            <h2 className="text-lg font-semibold mb-3">Portfolio Breakdown</h2>
            <BreakdownCard summary={summary} />
          </section>
        )}
      </main>
    </div>
  );
}
