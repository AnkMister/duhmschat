'use client';

import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';

export function Toaster() {
  const { toasts, dismiss } = useToast();

  return (
    <div className="fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-4 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'pointer-events-auto rounded-lg border p-4 shadow-lg transition-all animate-in slide-in-from-bottom-5',
            toast.variant === 'destructive'
              ? 'border-destructive bg-destructive text-destructive-foreground'
              : toast.variant === 'success'
              ? 'border-itm bg-itm-muted text-itm'
              : 'border-border bg-background text-foreground'
          )}
        >
          <div className="flex items-start gap-3">
            <div className="flex-1">
              {toast.title && (
                <div className="font-semibold">{toast.title}</div>
              )}
              {toast.description && (
                <div className="text-sm opacity-90">{toast.description}</div>
              )}
            </div>
            <button
              onClick={() => dismiss(toast.id)}
              className="rounded-md p-1 opacity-70 hover:opacity-100 focus:outline-none focus:ring-2"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          {toast.action && <div className="mt-2">{toast.action}</div>}
        </div>
      ))}
    </div>
  );
}
