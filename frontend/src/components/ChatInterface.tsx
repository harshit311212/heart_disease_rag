import React, { useState, useRef, useEffect } from 'react';
import type { Message } from '../App';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (msg: string) => void;
  isLoading: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <>
      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ margin: 'auto', textAlign: 'center', opacity: 0.5 }}>
            <h2 className="signage-text" style={{ fontSize: '24px', letterSpacing: '2px', color: '#00E5FF' }}>
              HITECH MEDICAL TERMINAL
            </h2>
            <p style={{ marginTop: '10px' }}>Enter query to query the semantic database.</p>
          </div>
        )}
        
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai typing-indicator">
            Processing Data...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-container" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Type your query..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
      </form>
    </>
  );
};

export default ChatInterface;
