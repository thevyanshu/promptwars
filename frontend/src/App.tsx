import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/layout/Navbar';
import Home from './pages/Home';
import TripPlanner from './pages/TripPlanner';
import ItineraryView from './pages/ItineraryView';
import Explore from './pages/Explore';

function App() {
  return (
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
  );
}

export default App;
