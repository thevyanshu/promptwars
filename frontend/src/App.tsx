import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Home from './pages/Home';
import TripPlanner from './pages/TripPlanner';
import ItineraryView from './pages/ItineraryView';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/plan" element={<TripPlanner />} />
          <Route path="/itinerary/:id" element={<ItineraryView />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
