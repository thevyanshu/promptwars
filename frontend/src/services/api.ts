const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Token getter is set by the AuthProvider at runtime
let tokenGetter: (() => Promise<string>) | null = null;

export function setTokenGetter(getter: () => Promise<string>) {
  tokenGetter = getter;
}

async function getHeaders(): Promise<Record<string, string>> {
  const token = tokenGetter ? await tokenGetter() : 'local-dev-token';
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
}

export function getStreamUrl(tripId: string): string {
  // We'll append the token as a query param since EventSource can't send headers
  return `${BASE_URL}/planner/${tripId}/stream`;
}

export async function getStreamToken(): Promise<string> {
  return tokenGetter ? tokenGetter() : 'local-dev-token';
}

export const api = {
  async createTrip(tripData: any) {
    const headers = await getHeaders();
    const res = await fetch(`${BASE_URL}/trips/`, {
      method: 'POST',
      headers,
      body: JSON.stringify(tripData),
    });
    if (!res.ok) throw new Error('Failed to create trip');
    return res.json();
  },

  async generateItinerary(tripId: string) {
    const headers = await getHeaders();
    const res = await fetch(`${BASE_URL}/planner/${tripId}/generate`, {
      method: 'POST',
      headers,
    });
    if (!res.ok) throw new Error('Failed to start generation');
    return res.json();
  },

  async getItinerary(tripId: string) {
    const headers = await getHeaders();
    const res = await fetch(`${BASE_URL}/planner/${tripId}/itinerary`, {
      method: 'GET',
      headers,
    });
    if (!res.ok) throw new Error('Failed to fetch itinerary');
    return res.json();
  },

  async chatModify(tripId: string, message: string, currentItinerary: any) {
    const headers = await getHeaders();
    const res = await fetch(`${BASE_URL}/planner/${tripId}/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ message, current_itinerary: currentItinerary }),
    });
    if (!res.ok) throw new Error('Chat request failed');
    return res.json();
  }
};
