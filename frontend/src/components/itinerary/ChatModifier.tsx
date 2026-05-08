import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, MessageCircle, X } from 'lucide-react';
import './ChatModifier.css';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatModifierProps {
  tripId: string;
  currentItinerary: any;
  onItineraryUpdate: (newData: any) => void;
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const DUMMY_TOKEN = 'local-dev-token';

const ChatModifier: React.FC<ChatModifierProps> = ({ tripId, currentItinerary, onItineraryUpdate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your trip assistant. You can ask me to modify your itinerary — for example:\n• \"Make dinner on Day 1 cheaper\"\n• \"Add a museum visit on Day 2\"\n• \"Replace the outdoor hike with an indoor activity\"",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${BASE_URL}/planner/${tripId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DUMMY_TOKEN}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          current_itinerary: currentItinerary
        })
      });

      if (!res.ok) throw new Error('Chat request failed');

      const data = await res.json();

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.reply || "I've updated your itinerary!",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (data.updated_itinerary) {
        onItineraryUpdate(data.updated_itinerary);
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I couldn't process that request. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button 
        className={`chat-fab ${isOpen ? 'chat-fab-active' : ''}`} 
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open chat modifier"
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="chat-panel glass-panel">
          <div className="chat-header">
            <h4>Modify Your Itinerary</h4>
            <span className="chat-badge">AI Assistant</span>
          </div>

          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                <p>{msg.content}</p>
                <span className="chat-time">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
            {isLoading && (
              <div className="chat-bubble assistant">
                <Loader2 className="animate-spin" size={16} />
                <span style={{ marginLeft: '0.5rem' }}>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <textarea
              className="chat-input"
              placeholder="e.g. Make Day 2 more budget-friendly..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
            />
            <button 
              className="chat-send-btn" 
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatModifier;
