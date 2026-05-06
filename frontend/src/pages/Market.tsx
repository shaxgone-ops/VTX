import React, { useState, useEffect } from 'react';
import { api, getTelegramId } from '../api/client';
import { useGameStore } from '../store/gameStore';
import { ArrowUpCircle, Zap } from 'lucide-react';

export const Market: React.FC = () => {
  const { user, updateBalance, updatePph } = useGameStore();
  const [categories, setCategories] = useState<any[]>([]);
  const [currentCat, setCurrentCat] = useState<string>('');
  const [cards, setCards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCats = async () => {
      const res = await api.getCategories();
      if (res.ok && res.data.length > 0) {
        setCategories(res.data);
        setCurrentCat(res.data[0].key);
      }
    };
    fetchCats();
  }, []);

  useEffect(() => {
    if (!currentCat) return;
    const fetchCards = async () => {
      setLoading(true);
      const tgId = getTelegramId();
      const res = await api.getCards(tgId, currentCat);
      if (res.ok) {
        setCards(res.data);
      }
      setLoading(false);
    };
    fetchCards();
  }, [currentCat]);

  const handleUpgrade = async (cardId: number, index: number) => {
    if (!user) return;
    const tgId = getTelegramId();
    
    // Quick optimistic check
    const card = cards[index];
    if (user.balance < card.next_cost) return; // Toast missing

    const res = await api.upgradeCard(tgId, cardId);
    if (res.ok) {
      // update user locally
      updateBalance(res.data.cost);
      updatePph(res.data.profit_per_hour);
      
      // Update card in list
      const newCards = [...cards];
      newCards[index] = {
        ...newCards[index],
        stage: res.data.new_stage,
        current_profit: res.data.new_profit,
        // (Next cost fetching logic requires either backend returning next_cost or refetching)
      };
      setCards(newCards);
      
      // refetch to be safe and accurate
      const currentListRes = await api.getCards(tgId, currentCat);
      if(currentListRes.ok) setCards(currentListRes.data);
    } else {
      alert(res.message);
    }
  };

  if (!user || !categories.length) return <div className="loader-screen"><div className="spinner"></div></div>;

  return (
    <div>
      {/* Category Tabs */}
      <div className="category-tabs">
        {categories.map(c => (
          <button 
            key={c.key} 
            className={`tab-btn ${currentCat === c.key ? 'active' : ''}`}
            onClick={() => setCurrentCat(c.key)}
          >
            {c.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', marginTop: 50 }}><div className="spinner" style={{ margin: '0 auto' }}></div></div>
      ) : (
        <div className="cards-grid">
          {cards.map((card, idx) => (
            <div key={card.card_id} className="ui-card glass-card">
              <div className="card-img-wrapper">
                <img src={card.image_url} alt={card.title} className="card-img" />
                <div style={{ position: 'absolute', top: 5, right: 5, background: 'rgba(0,0,0,0.6)', padding:'2px 6px', borderRadius: 4, fontSize: '0.7rem' }}>
                  Lvl {card.stage}
                </div>
              </div>
              <div className="card-info">
                <div className="card-title">{card.title}</div>
                <div className="card-stats">
                  <span>Profit/h</span>
                  <span className="card-pph"><Zap size={12} /> +{card.next_profit - card.current_profit}</span>
                </div>
                
                <button 
                  className={`btn-upgrade ${user.balance >= card.next_cost && card.stage < card.max_stage ? 'affordable' : ''}`}
                  disabled={card.stage >= card.max_stage || user.balance < card.next_cost}
                  onClick={() => handleUpgrade(card.card_id, idx)}
                >
                  <ArrowUpCircle size={16} />
                  {card.stage >= card.max_stage ? 'Max Level' : 
                   <span>{new Intl.NumberFormat('en-US').format(card.next_cost)} VTX</span>}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
