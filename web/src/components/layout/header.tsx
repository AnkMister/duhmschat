'use client';

import { UserButton } from '@clerk/nextjs';
import { RefreshCw, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { usePortfolioStore } from '@/store/portfolio-store';

interface HeaderProps {
  title?: string;
  showRefresh?: boolean;
  onRefresh?: () => void;
}

export function Header({ title = 'Options Monitor', showRefresh = true, onRefresh }: HeaderProps) {
  const alerts = usePortfolioStore((state) => state.alerts);
  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length;
  const isLoading = usePortfolioStore((state) => state.isLoading);

  return (
    <header className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="flex items-center justify-between h-14 px-4">
        <h1 className="text-lg font-semibold truncate">{title}</h1>

        <div className="flex items-center gap-2">
          {showRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          )}

          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-4 w-4" />
            {unacknowledgedCount > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
              >
                {unacknowledgedCount > 9 ? '9+' : unacknowledgedCount}
              </Badge>
            )}
          </Button>

          <UserButton
            appearance={{
              elements: {
                avatarBox: 'h-8 w-8',
              },
            }}
          />
        </div>
      </div>
    </header>
  );
}
