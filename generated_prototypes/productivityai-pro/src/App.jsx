import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import OnboardingScreen from './components/screens/OnboardingScreen';
import MainScreen from './components/screens/MainScreen';
import DetailScreen from './components/screens/DetailScreen';
import SettingsScreen from './components/screens/SettingsScreen';
import ProfileScreen from './components/screens/ProfileScreen';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/onboarding" element={<OnboardingScreen />} />
          <Route path="/" element={<MainScreen />} />
          <Route path="/detail/:id" element={<DetailScreen />} />
          <Route path="/settings" element={<SettingsScreen />} />
          <Route path="/profile" element={<ProfileScreen />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;