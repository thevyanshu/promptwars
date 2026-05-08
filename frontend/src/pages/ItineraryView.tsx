import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { jsonrepair } from 'jsonrepair';
import { useAuth } from '../contexts/AuthContext';
import DayCard from '../components/itinerary/DayCard';
import ChatModifier from '../components/itinerary/ChatModifier';
import MapComponent from '../components/maps/MapComponent';
import './ItineraryView.css';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const ItineraryView = () => {
  const { id } = useParams<{ id: string }>();
  const { getToken } = useAuth();
  const [streamData, setStreamData] = useState<any>(null);
  const [isStreaming, setIsStreaming] = useState(true);
  const [error, setError] = useState(false);
  const lastVersionRef = useRef<number | null>(null);

  useEffect(() => {
    if (!id) return;

    let eventSource: EventSource | null = null;
    let accumulatedJson = '';

    const connectStream = async () => {
      try {
        const token = await getToken();
        // Appending token to URL since EventSource doesn't support custom headers natively
        eventSource = new EventSource(`${BASE_URL}/planner/${id}/stream?token=${token}`);

        eventSource.onmessage = (event) => {
          try {
            const rawData = event.data.replace(/\\n/g, '\n');
            
            if (rawData.startsWith('{"status":')) {
               const parsed = JSON.parse(rawData);
               if (parsed.status === "error") {
                   setError(true);
                   setIsStreaming(false);
                   eventSource?.close();
                   return;
               }
            }

            accumulatedJson += rawData;
            
            try {
              const repaired = jsonrepair(accumulatedJson);
              setStreamData(JSON.parse(repaired));
            } catch (repairError) {
              // Wait for next chunk
            }

          } catch (err) {
            console.error("Stream parse error", err);
          }
        };

        eventSource.onerror = (err) => {
          setIsStreaming(false);
          eventSource?.close();
        };
      } catch (err) {
        console.error("Failed to get auth token", err);
        setError(true);
      }
    };

    connectStream();

    return () => {
      eventSource?.close();
    };
  }, [id, getToken]);

  useEffect(() => {
    if (!isStreaming && streamData?.version) {
      if (lastVersionRef.current !== null && streamData.version > lastVersionRef.current) {
        toast.success("Itinerary updated!");
      }
      lastVersionRef.current = streamData.version;
    }
  }, [streamData?.version, isStreaming]);

  if (error) {
    return (
      <div className="itinerary-view-container">
        <div className="glass-panel" style={{ padding: '2rem', borderColor: 'var(--accent)' }}>
          <h2>Connection Failed</h2>
          <p>Please ensure you are signed in and try again.</p>
        </div>
      </div>
    );
  }

  if (!streamData && isStreaming) {
    return (
      <div className="itinerary-view-container loading-state">
        <div className="glass-panel text-center" style={{ padding: '4rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <Loader2 className="animate-spin" size={48} color="var(--primary)" />
          <h2>Generating Your Adventure...</h2>
          <p className="text-muted">Gemini is crafting a personalized itinerary.</p>
        </div>
      </div>
    );
  }

  const markers = streamData?.itinerary?.flatMap((day: any) => 
    (day.activities || [])
      .filter((act: any) => act.location && act.lat && act.lng)
      .map((act: any, idx: number) => ({
        id: `${day.day}-${idx}`,
        lat: act.lat,
        lng: act.lng,
        title: act.location
      }))
  ) || [];

  return (
    <div className="itinerary-view-container">
      <div className="itinerary-header">
        <h1>
          Your <span className="text-gradient">Itinerary</span> 
          {isStreaming && <Loader2 className="animate-spin" size={24} style={{ display: 'inline', marginLeft: '1rem', color: 'var(--primary)' }} />}
        </h1>
        
        {streamData?.budget_summary && (
          <div className="ai-summary glass-panel">
            <p><strong>Budget Summary:</strong> {streamData.budget_summary}</p>
            {streamData?.ai_notes && <p><strong>AI Note:</strong> {streamData.ai_notes}</p>}
          </div>
        )}
      </div>

      <div className="itinerary-layout">
        <div className="itinerary-timeline-scroll">
          {streamData?.itinerary?.map((day: any) => (
            <DayCard 
              key={day.day || Math.random()}
              dayNumber={day.day}
              date={day.date || "TBD"}
              theme={day.theme || "Planning..."}
              activities={day.activities || []}
            />
          ))}
        </div>
        
        <div className="itinerary-map-sticky">
          <div className="glass-panel" style={{ height: 'calc(100vh - 120px)' }}>
             <MapComponent markers={markers} />
          </div>
        </div>
      </div>

      {!isStreaming && streamData && id && (
        <ChatModifier
          tripId={id}
          currentItinerary={streamData}
          onItineraryUpdate={(newData) => {
            setStreamData(newData);
          }}
        />
      )}
    </div>
  );
};

export default ItineraryView;
