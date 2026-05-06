import React, { useEffect, useState } from 'react';
import { api, getTelegramId } from '../api/client';
import { useGameStore } from '../store/gameStore';
import { CheckCircle2, Gift } from 'lucide-react';

export const Earn: React.FC = () => {
  const { user } = useGameStore();
  const [combo, setCombo] = useState<any>(null);
  const [referrals, setReferrals] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const cmb = await api.getDailyCombo();
      if (cmb.ok) setCombo(cmb.data);

      const ref = await api.getReferrals(getTelegramId());
      if (ref.ok) setReferrals(ref.data);
    };
    fetchData();
  }, []);

  const claimCombo = async () => {
    const res = await api.checkDailyCombo(getTelegramId());
    alert(res.message);
  };

  if (!user) return null;

  return (
    <div style={{ padding: '20px' }}>
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: 15, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Gift color="var(--accent-gold)" /> Daily Combo
        </h2>
        {combo?.active ? (
          <div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 15 }}>
              Find 3 cards today and upgrade them to claim the big reward!
            </p>
            <div style={{ display: 'flex', gap: 10, marginBottom: 15 }}>
              {combo.cards.map((c: any) => (
                <div key={c.card_id} style={{ flex: 1, height: 80, borderRadius: 10, background: '#1a1d29', border: '1px solid var(--border-light)', overflow: 'hidden' }}>
                    <img src={c.image_url} alt="" style={{width: '100%', height: '100%', objectFit: 'cover', opacity: 0.5}} />
                </div>
              ))}
            </div>
            
            <button className="btn-upgrade affordable" style={{ width: '100%' }} onClick={claimCombo}>
              Check && Claim +{new Intl.NumberFormat('en-US').format(combo.reward)}
            </button>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No combo active today.</p>
        )}
      </div>

      <div className="glass-panel" style={{ padding: '20px' }}>
        <h2 style={{ marginBottom: 15 }}>Friends</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 15 }}>
          Invite friends to earn bonuses! You get <b>{referrals?.reward_per_friend || 100} VTX</b> per friend.
        </p>

        <button 
          className="btn-upgrade" 
          style={{ width: '100%', marginBottom: 20 }}
          onClick={() => {
            if (window.Telegram?.WebApp) {
              window.Telegram.WebApp.openTelegramLink(
                `https://t.me/share/url?url=${encodeURIComponent(referrals?.invite_link || '')}`
              );
            }
          }}
        >
          Invite a Friend
        </button>

        <h3 style={{ fontSize: '1rem', color: 'var(--text-muted)', marginBottom: 10 }}>
          Your Invites: {referrals?.total_invited || 0}
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {referrals?.friends?.map((f: any, idx: number) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: 12, background: 'var(--bg-card)', borderRadius: 10 }}>
              <span style={{ fontWeight: 600 }}>{f.first_name}</span>
              <span style={{ color: 'var(--accent-gold)' }}>Lvl {f.level}</span>
            </div>
          ))}
          {referrals?.friends?.length === 0 && (
             <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>You haven't invited anyone yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};
