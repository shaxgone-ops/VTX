import React from 'react';
import { useGameStore } from '../store/gameStore';
import { formatCompactNumber } from '../utils';

export const TopBar: React.FC = () => {
  const { user } = useGameStore();

  if (!user) return null;

  return (
    <div className="top-bar">
      <div className="user-info">
        <div className="avatar">
          {user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
        </div>
        <div className="stats-col">
          <div className="username">{user.first_name || 'Player'}</div>
          <div className="level-badge">Lvl {user.level} {user.is_vip && '· VIP'}</div>
        </div>
      </div>
      
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Profit / hour</div>
        <div className="text-gradient-success" style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end', color: 'var(--accent-success)' }}>
          +{formatCompactNumber(user.profit_per_hour)} VTX
        </div>
      </div>
    </div>
  );
};
