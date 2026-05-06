import { create } from 'zustand';
import { api, getTelegramId } from '../api/client';

export interface UserProfile {
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  level: number;
  balance: number;
  profit_per_hour: number;
  stamina: number;
  max_stamina: number;
  lifetime_taps: number;
  daily_taps: number;
  is_vip: boolean;
  offline_earned: number;
}

interface GameState {
  user: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  fetchProfile: () => Promise<void>;
  processTap: (amount: number) => Promise<boolean>;
  updateBalance: (amount: number) => void;
  updatePph: (delta: number) => void;
  claimOffline: () => void;
}

export const useGameStore = create<GameState>((set, get) => ({
  user: null,
  isLoading: true,
  error: null,

  fetchProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const tgId = getTelegramId();
      const res = await api.getProfile(tgId);
      if (res.ok) {
        set({ user: res.data, isLoading: false });
      } else {
        set({ error: res.message, isLoading: false });
      }
    } catch (err: any) {
      set({ error: err.message || 'Failed to load profile', isLoading: false });
    }
  },

  processTap: async (amount: number) => {
    // Optimistic UI update
    const currentUser = get().user;
    if (!currentUser) return false;
    
    if (currentUser.stamina < amount) return false;

    // Apply tokens locally instantly for smooth UI
    set((state) => ({
      user: state.user ? {
        ...state.user,
        balance: state.user.balance + amount, // Simplified, actual logic includes VIP multipliers
        stamina: state.user.stamina - amount,
      } as UserProfile : null
    }));

    try {
      const tgId = getTelegramId();
      const res = await api.tap(tgId, amount);
      if (res.ok) {
        // Sync with backend truth
        set((state) => ({
          user: state.user ? {
            ...state.user,
            balance: res.data.balance,
            stamina: res.data.stamina,
            level: res.data.level,
            profit_per_hour: res.data.profit_per_hour,
          } as UserProfile : null
        }));
        return true;
      }
      return false;
    } catch (err) {
      // Revert if failed (simplified, doing full fetch)
      get().fetchProfile();
      return false;
    }
  },

  updateBalance: (amount: number) => {
    set((state) => ({
      user: state.user ? { ...state.user, balance: state.user.balance - amount } : null
    }));
  },

  updatePph: (newPph: number) => {
    set((state) => ({
      user: state.user ? { ...state.user, profit_per_hour: newPph } : null
    }));
  },

  claimOffline: () => {
    set((state) => ({
      user: state.user ? { ...state.user, offline_earned: 0 } : null
    }));
  }
}));
