import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WebApp from '@twa-dev/sdk';
import { useGameStore } from './store/gameStore';

import { TopBar } from './components/TopBar';
import { BottomNav } from './components/BottomNav';

import { TapArena } from './pages/TapArena';
import { Market } from './pages/Market';
import { Earn } from './pages/Earn';
import { Leaderboard } from './pages/Leaderboard';
import { Airdrop } from './pages/Airdrop';
import { formatCompactNumber } from './utils';

const App: React.FC = () => {
  const { fetchProfile, user, isLoading, error } = useGameStore();

  useEffect(() => {
    // Expand Telegram WebApp to full height
    if (typeof window !== 'undefined' && WebApp.initDataUnsafe) {
      WebApp.ready();
      WebApp.expand();
      WebApp.setHeaderColor('#0a0b10');
      WebApp.setBackgroundColor('#0a0b10');
    }

    // Load initial profile data
    fetchProfile();
  }, [fetchProfile]);

  if (isLoading) {
    return <div className="loader-screen">
      <div className="spinner"></div>
      <p style={{ color: 'var(--text-secondary)', marginTop: 20 }}>Syncing with Arena...</p>
    </div>;
  }

  if (error) {
    return <div className="loader-screen">
      <h2 style={{ color: 'var(--accent-danger)' }}>Connection Error</h2>
      <p>{error}</p>
      <button className="btn-upgrade" style={{ marginTop: 20 }} onClick={fetchProfile}>Retry</button>
    </div>;
  }

  return (
    <Router>
      <div className="app-container">
        {/* Absolute position offline reward modal */}
        {user?.offline_earned && user.offline_earned > 0 ? (
          <div style={{ position: 'fixed', inset: 0, zIndex: 99999, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="glass-panel" style={{ padding: 30, textAlign: 'center', maxWidth: 350 }}>
              <h2>Offline Profits!</h2>
              <p style={{ margin: '20px 0', color: 'var(--text-secondary)' }}>You gained tokens while you were away!</p>
              <h1 className="text-gradient-gold">+{formatCompactNumber(user.offline_earned)}</h1>
              <button 
                 className="btn-upgrade affordable" 
                 style={{ width: '100%', marginTop: 20 }}
                 onClick={() => useGameStore.getState().claimOffline()}
              >
                Awesome!
              </button>
            </div>
          </div>
        ) : null}

        <TopBar />
        
        <div className="main-content">
          <Routes>
            <Route path="/" element={<TapArena />} />
            <Route path="/market" element={<Market />} />
            <Route path="/earn" element={<Earn />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/airdrop" element={<Airdrop />} />
          </Routes>
        </div>

        <BottomNav />
      </div>
    </Router>
  );
};

export default App;
