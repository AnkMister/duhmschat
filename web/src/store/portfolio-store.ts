import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { OptionPosition, PortfolioSummary, Alert, AlertRule, ActionItem } from '@/types/portfolio';

interface PortfolioState {
  // Positions
  positions: OptionPosition[];
  isLoading: boolean;
  error: string | null;

  // Summary
  summary: PortfolioSummary | null;

  // Alerts
  alerts: Alert[];
  rules: AlertRule[];

  // Actions
  actionItems: ActionItem[];

  // Last refresh timestamp
  lastRefresh: string | null;

  // Actions
  setPositions: (positions: OptionPosition[]) => void;
  addPosition: (position: OptionPosition) => void;
  updatePosition: (id: string, updates: Partial<OptionPosition>) => void;
  removePosition: (id: string) => void;

  setSummary: (summary: PortfolioSummary) => void;

  setAlerts: (alerts: Alert[]) => void;
  acknowledgeAlert: (id: string) => void;
  clearAcknowledgedAlerts: () => void;

  setRules: (rules: AlertRule[]) => void;
  addRule: (rule: AlertRule) => void;
  updateRule: (id: string, updates: Partial<AlertRule>) => void;
  removeRule: (id: string) => void;

  setActionItems: (items: ActionItem[]) => void;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLastRefresh: (timestamp: string) => void;

  // Derived getters (using selectors)
  getItmPositions: () => OptionPosition[];
  getOtmPositions: () => OptionPosition[];
  getExpiringPositions: (days: number) => OptionPosition[];
}

export const usePortfolioStore = create<PortfolioState>()(
  persist(
    (set, get) => ({
      // Initial state
      positions: [],
      isLoading: false,
      error: null,
      summary: null,
      alerts: [],
      rules: [],
      actionItems: [],
      lastRefresh: null,

      // Position actions
      setPositions: (positions) => set({ positions }),

      addPosition: (position) =>
        set((state) => ({
          positions: [...state.positions, position],
        })),

      updatePosition: (id, updates) =>
        set((state) => ({
          positions: state.positions.map((p) =>
            p.id === id ? { ...p, ...updates } : p
          ),
        })),

      removePosition: (id) =>
        set((state) => ({
          positions: state.positions.filter((p) => p.id !== id),
        })),

      // Summary actions
      setSummary: (summary) => set({ summary }),

      // Alert actions
      setAlerts: (alerts) => set({ alerts }),

      acknowledgeAlert: (id) =>
        set((state) => ({
          alerts: state.alerts.map((a) =>
            a.id === id
              ? { ...a, acknowledged: true, acknowledgedAt: new Date().toISOString() }
              : a
          ),
        })),

      clearAcknowledgedAlerts: () =>
        set((state) => ({
          alerts: state.alerts.filter((a) => !a.acknowledged),
        })),

      // Rule actions
      setRules: (rules) => set({ rules }),

      addRule: (rule) =>
        set((state) => ({
          rules: [...state.rules, rule],
        })),

      updateRule: (id, updates) =>
        set((state) => ({
          rules: state.rules.map((r) =>
            r.id === id ? { ...r, ...updates } : r
          ),
        })),

      removeRule: (id) =>
        set((state) => ({
          rules: state.rules.filter((r) => r.id !== id),
        })),

      // Action items
      setActionItems: (items) => set({ actionItems: items }),

      // Loading/error state
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      setLastRefresh: (lastRefresh) => set({ lastRefresh }),

      // Derived getters
      getItmPositions: () => {
        return get().positions.filter((p) => p.moneyStatus === 'itm');
      },

      getOtmPositions: () => {
        return get().positions.filter((p) => p.moneyStatus === 'otm');
      },

      getExpiringPositions: (days) => {
        const now = new Date();
        const cutoff = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

        return get().positions.filter((p) => {
          const expDate = new Date(p.expirationDate);
          return expDate >= now && expDate <= cutoff;
        });
      },
    }),
    {
      name: 'options-portfolio-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        positions: state.positions,
        rules: state.rules,
        alerts: state.alerts.filter((a) => !a.acknowledged),
      }),
    }
  )
);

// Selectors for better performance
export const selectPositions = (state: PortfolioState) => state.positions;
export const selectItmPositions = (state: PortfolioState) =>
  state.positions.filter((p) => p.moneyStatus === 'itm');
export const selectOtmPositions = (state: PortfolioState) =>
  state.positions.filter((p) => p.moneyStatus === 'otm');
export const selectSummary = (state: PortfolioState) => state.summary;
export const selectAlerts = (state: PortfolioState) => state.alerts;
export const selectUnacknowledgedAlerts = (state: PortfolioState) =>
  state.alerts.filter((a) => !a.acknowledged);
export const selectActionItems = (state: PortfolioState) => state.actionItems;
export const selectIsLoading = (state: PortfolioState) => state.isLoading;
