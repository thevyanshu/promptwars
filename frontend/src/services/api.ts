const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// We use a dummy token for MVP local development as configured in the backend auth middleware
const DUMMY_TOKEN = 'local-dev-token';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${DUMMY_TOKEN}`
};

export const api = {
  async createTrip(tripData: any) {
    const res = await fetch(`${BASE_URL}/trips/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(tripData),
    });
    if (!res.ok) throw new Error('Failed to create trip');
    return res.json();
  },

  async generateItinerary(tripId: string) {
    const res = await fetch(`${BASE_URL}/planner/${tripId}/generate`, {
      method: 'POST',
      headers,
    });
    if (!res.ok) throw new Error('Failed to start generation');
    return res.json();
  },

  async getItinerary(tripId: string) {
    const res = await fetch(`${BASE_URL}/planner/${tripId}/itinerary`, {
      method: 'GET',
      headers,
    });
    if (!res.ok) throw new Error('Failed to fetch itinerary');
    return res.json();
  }
};
