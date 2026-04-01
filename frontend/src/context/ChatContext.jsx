import React, { createContext, useContext, useState, useEffect } from 'react';
import { getSessions, getOllamaTags } from '../lib/api';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [contextItems, setContextItems] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  
  // Estado para modelos
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('qwen2.5-coder:3b');
  const [modelProvider, setModelProvider] = useState('ollama'); // 'ollama' or 'google'

  // Cargar sesiones y modelos al inicio
  useEffect(() => {
    fetchSessions();
    fetchModels();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (e) {
      console.error("Error fetching sessions in context", e);
    }
  };

  const fetchModels = async () => {
    try {
      const models = await getOllamaTags();
      if (models && models.models) {
        setAvailableModels(models.models.map(m => ({ id: m.name, name: m.name, size: m.size })));
      }
    } catch (e) {
      console.error("Error fetching models", e);
      // Fallback a modelo por defecto
      setAvailableModels([{ id: 'qwen2.5-coder:3b', name: 'qwen2.5-coder:3b' }]);
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
      availableModels, setAvailableModels,
      selectedModel, setSelectedModel,
      modelProvider, setModelProvider,
      fetchSessions,
      fetchModels,
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
