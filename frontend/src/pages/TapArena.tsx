import React, { useState, useEffect, useCallback } from 'react';
import { useGameStore } from '../store/gameStore';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingText {
  id: number;
  x: number;
  y: number;
}

export const TapArena: React.FC = () => {
  const { user, processTap } = useGameStore();
  const [floatingTexts, setFloatingTexts] = useState<FloatingText[]>([]);
  const tapAmount = user?.is_vip ? 3.5 : 1; // Example multiplier

  // Remove old floating texts
  useEffect(() => {
    if (floatingTexts.length === 0) return;
    const timer = setTimeout(() => {
      setFloatingTexts(prev => prev.slice(1));
    }, 1000);
    return () => clearTimeout(timer);
  }, [floatingTexts]);

  const handleTap = useCallback((e: React.MouseEvent<HTMLDivElement> | React.TouchEvent<HTMLDivElement>) => {
    // Prevent default to avoid double-firing on touch devices if mixing mouse/touch
    if (e.type === 'touchstart') e.preventDefault();
    if (!user || user.stamina <= 0) return;

    // Get coordinates for floating text
    let x = 0;
    let y = 0;
    
    if ('touches' in e) {
      // Touch Event
      // Handle multiple touches simultaneously (multi-tap)
      const newTexts: FloatingText[] = [];
      let totalAmount = 0;

      for (let i = 0; i < e.touches.length; i++) {
        totalAmount += 1;
        const rect = e.currentTarget.getBoundingClientRect();
        newTexts.push({
          id: Date.now() + i,
          x: e.touches[i].clientX - rect.left,
          y: e.touches[i].clientY - rect.top,
        });
      }
      
      setFloatingTexts(prev => [...prev, ...newTexts]);
      processTap(totalAmount);
    } else {
      // Mouse Event
      const rect = e.currentTarget.getBoundingClientRect();
      x = (e as React.MouseEvent).clientX - rect.left;
      y = (e as React.MouseEvent).clientY - rect.top;
      
      setFloatingTexts(prev => [...prev, { id: Date.now(), x, y }]);
      processTap(1);
    }
  }, [user, processTap]);

  if (!user) return <div className="loader-screen"><div className="spinner"></div></div>;

  const staminaPercentage = (user.stamina / user.max_stamina) * 100;

  return (
    <div className="play-area">
      {/* Balance */}
      <div className="balance-display">
        <div className="balance-title">Total Balance</div>
        <div className="balance-amount">
          <img src="/logo.png" alt="VTX" className="token-icon" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
          <span className="text-gradient-gold">
            {new Intl.NumberFormat('en-US').format(user.balance)}
          </span>
        </div>
      </div>

      {/* Tap Element */}
      <div 
        className="tap-coin-container"
        onMouseDown={handleTap}
        onTouchStart={handleTap}
      >
        {/* Placeholder Tap Object (You can replace with user.avatar_logo or VTX logo) */}
        <div className="tap-coin-image" style={{ background: 'linear-gradient(45deg, #14161e, rgba(0, 238, 255, 0.2))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
           <img src="https://picsum.photos/seed/vtx/300/300" alt="Main Coin" style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} />
        </div>

        {/* Floating Numbers */}
        <AnimatePresence>
          {floatingTexts.map(text => (
            <motion.div
              key={text.id}
              className="floating-number"
              style={{ left: text.x, top: text.y }}
              initial={{ y: 0, opacity: 1, scale: 1 }}
              animate={{ y: -120, opacity: 0, scale: 1.5 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            >
              +{tapAmount.toFixed(1)}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Stamina */}
      <div className="stamina-container">
        <div className="stamina-info">
          <span>Energy</span>
          <div className="stamina-value">
            <span style={{ color: 'var(--accent-neon)' }}>{user.stamina}</span> / {user.max_stamina}
          </div>
        </div>
        <div className="stamina-bar-bg">
          <div 
            className="stamina-bar-fill" 
            style={{ width: `${Math.max(2, staminaPercentage)}%` }} // keep bit of color
          />
        </div>
      </div>
    </div>
  );
};
