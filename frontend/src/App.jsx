import React, { useState } from 'react';
import Toaster from 'react-hot-toast/headless/toaster';
import './index.css';
import Landing from './pages/Landing';

function App() {
  return (
    <>
      <Toaster />
      <Landing />
    </>
  );
}

export default App;
