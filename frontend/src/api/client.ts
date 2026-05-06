import axios from 'axios';
import WebApp from '@twa-dev/sdk';

// Get base URL from env or fallback to Render backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://vtx-px5f.onrender.com/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get logic user ID from WebApp initData
export const getTelegramId = (): number => {
  if (typeof window !== 'undefined' && WebApp.initDataUnsafe?.user) {
    return WebApp.initDataUnsafe.user.id;
  }
  // For local testing outside Telegram, return admin ID or a fallback
  return 6735799833; 
};

export const api = {
  getProfile: async (id: number) => {
    const response = await apiClient.get(`/user/${id}`);
    return response.data;
  },
  
  tap: async (id: number, amount: number) => {
    const response = await apiClient.post('/tap', { telegram_id: id, tap_amount: amount });
    return response.data;
  },
  
  getCards: async (id: number, category?: string) => {
    const url = category ? `/cards/${id}?category=${category}` : `/cards/${id}`;
    const response = await apiClient.get(url);
    return response.data;
  },
  
  getCategories: async () => {
    const response = await apiClient.get('/categories');
    return response.data;
  },
  
  upgradeCard: async (userId: number, cardId: number) => {
    const response = await apiClient.post('/cards/upgrade', { telegram_id: userId, card_id: cardId });
    return response.data;
  },

  getLeaderboard: async () => {
    const response = await apiClient.get('/leaderboard');
    return response.data;
  },

  getDailyCombo: async () => {
    const response = await apiClient.get('/daily-combo');
    return response.data;
  },

  checkDailyCombo: async (userId: number) => {
    const response = await apiClient.post('/daily-combo/check', { telegram_id: userId });
    return response.data;
  }
};
