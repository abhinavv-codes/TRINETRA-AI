import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Live from './pages/Live';
import Heatmap from './pages/Heatmap';
import Trends from './pages/Trends';
import Search from './pages/Search';
import Evidence from './pages/Evidence';
import RiskQueue from './pages/RiskQueue';
import Login from './pages/Login';
import Toaster from 'react-hot-toast/headless/toaster';
import './index.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  return (
    <Router>
      <Toaster />
      {isLoggedIn ? (
        <>
          <Header onLogout={() => {
            localStorage.removeItem('token');
            localStorage.removeItem('role');
            setIsLoggedIn(false);
          }} />
          <div className="main-container">
            <Routes>
              <Route path="/" element={<Live />} />
              <Route path="/heatmap" element={<Heatmap />} />
              <Route path="/trends" element={<Trends />} />
              <Route path="/search" element={<Search />} />
              <Route path="/evidence/:id" element={<Evidence />} />
              <Route path="/risk-queue" element={<RiskQueue />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
        </>
      ) : (
        <Routes>
          <Route path="/login" element={<Login onLogin={() => setIsLoggedIn(true)} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </Router>
  );
}

export default App;
