import React from 'react';
import { NavLink } from 'react-router-dom';
import { Pickaxe, Store, Award, Trophy, Wallet } from 'lucide-react';

export const BottomNav: React.FC = () => {
  const defaultClass = "nav-item";
  const activeClass = "nav-item active";

  return (
    <div className="bottom-nav">
      <NavLink 
        to="/" 
        className={({ isActive }) => isActive ? activeClass : defaultClass}
      >
        <Pickaxe className="nav-icon" />
        <span>Arena</span>
      </NavLink>

      <NavLink 
        to="/market" 
        className={({ isActive }) => isActive ? activeClass : defaultClass}
      >
        <Store className="nav-icon" />
        <span>Market</span>
      </NavLink>

      <NavLink 
        to="/earn" 
        className={({ isActive }) => isActive ? activeClass : defaultClass}
      >
        <Award className="nav-icon" />
        <span>Earn</span>
      </NavLink>

      <NavLink 
        to="/leaderboard" 
        className={({ isActive }) => isActive ? activeClass : defaultClass}
      >
        <Trophy className="nav-icon" />
        <span>Top</span>
      </NavLink>

      <NavLink 
        to="/airdrop" 
        className={({ isActive }) => isActive ? activeClass : defaultClass}
      >
        <Wallet className="nav-icon" />
        <span>Airdrop</span>
      </NavLink>
    </div>
  );
};
