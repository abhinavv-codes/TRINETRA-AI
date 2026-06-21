import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Live from './pages/Live';
import Detection from './pages/Detection';
import VideoDetection from './pages/VideoDetection';
import Analytics from './pages/Analytics';
import Heatmap from './pages/Heatmap';
import Trends from './pages/Trends';
import Search from './pages/Search';
import Evidence from './pages/Evidence';
import RiskQueue from './pages/RiskQueue';
import Login from './pages/Login';
import Validation from './pages/Validation';
import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
        {isLoggedIn ? (
          <>
            <Header onLogout={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('role');
              setIsLoggedIn(false);
            }} />
            <div className="main-container">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/detect" element={<Detection />} />
                <Route path="/video-detection" element={<VideoDetection />} />
                <Route path="/live-feed" element={<Live />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/heatmap" element={<Heatmap />} />
                <Route path="/trends" element={<Trends />} />
                <Route path="/search" element={<Search />} />
                <Route path="/evidence/:id" element={<Evidence />} />
                <Route path="/risk-queue" element={<RiskQueue />} />
                <Route path="/validation" element={<Validation />} />
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
    </QueryClientProvider>
  );
}

export default App;
