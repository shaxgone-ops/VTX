import React, { useState } from 'react';
import { useGameStore } from '../store/gameStore';
import { Wallet, Coins, RefreshCw } from 'lucide-react';
import { formatCompactNumber } from '../utils';

export const Airdrop: React.FC = () => {
  const { user } = useGameStore();
  const [wallet, setWallet] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);

  const handleConnect = () => {
    setConnecting(true);
    // Simulate TON Connect connection
    setTimeout(() => {
      setWallet("UQDL...x8Y0");
      setConnecting(false);
    }, 1500);
  };

  const handleWithdraw = () => {
    alert("Token listing and withdrawals will be available soon! Join our community for updates.");
  };

  if (!user) return null;

  return (
    <div style={{ padding: '20px', paddingBottom: 100 }}>
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <Wallet size={48} color="var(--accent-neon)" style={{ marginBottom: 10, filter: 'drop-shadow(0 0 10px rgba(0, 238, 255, 0.5))' }} />
        <h1>Airdrop & Wallet</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Connect your TON wallet to claim your tokens</p>
      </div>

      <div className="glass-panel" style={{ padding: 25, borderRadius: 15, marginBottom: 20 }}>
        {wallet ? (
          <div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 5 }}>Connected Wallet</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ color: 'var(--accent-success)' }}>{wallet}</h2>
              <button className="btn-upgrade" style={{ padding: '8px 12px', background: 'var(--accent-danger)' }} onClick={() => setWallet(null)}>Disconnect</button>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center' }}>
            <button className="btn-upgrade" style={{ width: '100%', padding: '15px' }} onClick={handleConnect} disabled={connecting}>
              {connecting ? <RefreshCw className="spin" size={20} /> : "Connect TON Wallet"}
            </button>
          </div>
        )}
      </div>

      <div className="glass-panel" style={{ padding: 25, borderRadius: 15 }}>
        <h3 style={{ marginBottom: 15, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Coins size={24} color="var(--accent-gold)" /> Withdraw Balance
        </h3>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
          <span style={{ color: 'var(--text-secondary)' }}>Available Tokens:</span>
          <span className="text-gradient-gold" style={{ fontWeight: 'bold' }}>{formatCompactNumber(user.balance)} VTX</span>
        </div>

        <button 
          className="btn-upgrade affordable" 
          style={{ width: '100%', padding: '15px', opacity: wallet ? 1 : 0.5 }}
          onClick={handleWithdraw}
          disabled={!wallet}
        >
          {wallet ? "Withdraw to Wallet" : "Connect Wallet First"}
        </button>
        
        <p style={{ textAlign: 'center', marginTop: 15, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Token generation event (TGE) and listing dates will be announced on our official channels.
        </p>
      </div>
    </div>
  );
};
