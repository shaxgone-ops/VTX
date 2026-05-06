import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { useGameStore } from '../store/gameStore';
import { Trophy, Medal } from 'lucide-react';

export const Leaderboard: React.FC = () => {
  const { user } = useGameStore();
  const [board, setBoard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTop = async () => {
      const res = await api.getLeaderboard();
      if (res.ok) setBoard(res.data);
      setLoading(false);
    };
    fetchTop();
  }, []);

  if (!user || loading) return <div className="loader-screen"><div className="spinner"></div></div>;

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ textAlign: 'center', marginBottom: 30 }}>
        <Trophy size={48} color="var(--accent-gold)" style={{ marginBottom: 10, filter: 'drop-shadow(0 0 10px rgba(255, 215, 0, 0.5))' }} />
        <h1>Wall of Fame</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Top players in VTX Arena</p>
      </div>

      <div className="glass-panel" style={{ padding: '10px' }}>
        {board.map((p, idx) => (
          <div 
            key={p.telegram_id}
            style={{
              display: 'flex',
              alignItems: 'center',
              padding: '12px 15px',
              borderBottom: idx === board.length - 1 ? 'none' : '1px solid var(--border-light)',
              background: p.telegram_id === user.telegram_id ? 'rgba(0, 238, 255, 0.1)' : 'transparent',
              borderRadius: p.telegram_id === user.telegram_id ? '8px' : '0'
            }}
          >
            <div style={{ width: 40, fontWeight: 'bold', color: idx < 3 ? 'var(--accent-gold)' : 'var(--text-muted)' }}>
              {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${p.rank}`}
            </div>
            
            <div className="avatar" style={{ width: 36, height: 36, fontSize: '1rem', marginRight: 15, background: idx < 3 ? 'var(--accent-gold)' : '' }}>
               {p.first_name.charAt(0).toUpperCase()}
            </div>
            
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{p.first_name} {p.telegram_id === user.telegram_id && '(You)'}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Lvl {p.level} {p.is_vip && '• VIP'}</div>
            </div>
            
            <div style={{ textAlign: 'right' }}>
               <div style={{ fontWeight: 'bold', color: 'var(--accent-neon)' }}>
                 {new Intl.NumberFormat('en-US', { notation: "compact" }).format(p.balance)}
               </div>
               <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                 {new Intl.NumberFormat('en-US', { notation: "compact" }).format(p.profit_per_hour)}/h
               </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
