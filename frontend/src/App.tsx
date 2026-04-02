import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import DataGallery from './components/DataGallery';
import './index.css';

export interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
}

export interface PatientData {
  row_id: string;
  Age: string;
  Sex: string;
  Cholesterol: string;
  MaxHR: string;
  HeartDisease: string | number;
  [key: string]: any;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [retrievedData, setRetrievedData] = useState<PatientData[]>([]);
  const [isErrorState, setIsErrorState] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (query: string) => {
    const newUserMsg: Message = { id: Date.now().toString(), sender: 'user', text: query };
    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);
    setIsErrorState(false);
    setRetrievedData([]);

    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      const newAiMsg: Message = { id: (Date.now() + 1).toString(), sender: 'ai', text: data.answer };
      setMessages(prev => [...prev, newAiMsg]);

      if (data.answer.includes("Sorry I can't find anything relevant")) {
        setIsErrorState(true);
      } else if (data.metadata && data.metadata.length > 0) {
        setRetrievedData(data.metadata);
      }
    } catch (error: any) {
      console.error("Backend Connection Failure:", error);
      const errorMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        sender: 'ai', 
        text: `Backend Connection Error: ${error.message}. Please ensure the server is running on port 8000.`
      };
      setMessages(prev => [...prev, errorMsg]);
      setIsErrorState(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="main-layout">
      <div className="chat-panel">
        <ChatInterface 
          messages={messages} 
          onSendMessage={handleSendMessage} 
          isLoading={isLoading} 
        />
      </div>
      <div className="data-panel">
        <DataGallery data={retrievedData} isError={isErrorState} />
      </div>
    </div>
  );
}

export default App;
