import React from 'react';
import { APIProvider, Map, Marker } from '@vis.gl/react-google-maps';

interface MapComponentProps {
  apiKey?: string;
  center?: { lat: number; lng: number };
  markers?: Array<{ id: string; lat: number; lng: number; title: string }>;
}

const MapComponent: React.FC<MapComponentProps> = ({ 
  apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "dummy-key",
  center,
  markers = []
}) => {
  // If center is provided, use it. Otherwise, use the first marker. Otherwise fallback to Tokyo.
  const dynamicCenter = center || (markers.length > 0 ? { lat: markers[0].lat, lng: markers[0].lng } : { lat: 35.6762, lng: 139.6503 });

  return (
    <div style={{ height: '100%', width: '100%', minHeight: '400px', borderRadius: '16px', overflow: 'hidden' }}>
      <APIProvider apiKey={apiKey}>
        <Map defaultCenter={dynamicCenter} defaultZoom={12} gestureHandling={'greedy'} disableDefaultUI={true}>
          {markers.map(marker => (
            <Marker key={marker.id} position={{ lat: marker.lat, lng: marker.lng }} title={marker.title} />
          ))}
        </Map>
      </APIProvider>
    </div>
  );
};

export default MapComponent;
