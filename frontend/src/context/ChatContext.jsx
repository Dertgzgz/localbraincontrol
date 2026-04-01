import React, { createContext, useContext, useState, useEffect } from 'react';
import { getSessions } from '../lib/api';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [contextItems, setContextItems] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isResolving, setIsResolving] = useState(false);

  // Cargar sesiones al inicio
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (e) {
      console.error("Error fetching sessions in context", e);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    setContextItems([]);
  };

  return (
    <ChatContext.Provider value={{
      messages, setMessages,
      currentSessionId, setCurrentSessionId,
      sessions, setSessions,
      contextItems, setContextItems,
      isStreaming, setIsStreaming,
      isResolving, setIsResolving,
      fetchSessions,
      clearChat
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
