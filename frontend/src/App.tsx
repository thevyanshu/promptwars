import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { setTokenGetter } from './services/api';
import Navbar from './components/layout/Navbar';
import Home from './pages/Home';
import TripPlanner from './pages/TripPlanner';
import ItineraryView from './pages/ItineraryView';
import Explore from './pages/Explore';

// Helper component to initialize API with auth token getter
const AuthInitializer = ({ children }: { children: React.ReactNode }) => {
  const { getToken } = useAuth();
  
  useEffect(() => {
    setTokenGetter(getToken);
  }, [getToken]);

  return <>{children}</>;
};

function App() {
  return (
    <AuthProvider>
      <AuthInitializer>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Toaster position="top-right" />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/explore" element={<Explore />} />
              <Route path="/plan" element={<TripPlanner />} />
              <Route path="/itinerary/:id" element={<ItineraryView />} />
            </Routes>
          </main>
        </div>
      </AuthInitializer>
    </AuthProvider>
  );
}

export default App;
