import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TripPlanner from '../pages/TripPlanner';

const queryClient = new QueryClient();

const renderWithProviders = (component: React.ReactNode) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('TripPlanner Component', () => {
  it('renders the header and NLP section', () => {
    renderWithProviders(<TripPlanner />);
    
    expect(screen.getByText(/Design Your/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/I want a cheap family trip/i)).toBeInTheDocument();
  });

  it('renders structured inputs', () => {
    renderWithProviders(<TripPlanner />);
    
    expect(screen.getByPlaceholderText(/Where to\?/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Select dates/i)).toBeInTheDocument();
  });

  it('allows typing in the NLP prompt box', () => {
    renderWithProviders(<TripPlanner />);
    
    const input = screen.getByPlaceholderText(/I want a cheap family trip/i);
    fireEvent.change(input, { target: { value: 'A quick weekend getaway' } });
    
    expect(input).toHaveValue('A quick weekend getaway');
  });

  it('renders the generate button', () => {
    renderWithProviders(<TripPlanner />);
    
    const button = screen.getByRole('button', { name: /Generate Itinerary/i });
    expect(button).toBeInTheDocument();
  });
});
