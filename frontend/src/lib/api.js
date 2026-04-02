import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
});

export const getMetrics = async () => {
  const { data } = await api.get('/system/metrics');
  return data;
};

export const getOllamaStatus = async () => {
  const { data } = await api.get('/ollama/ps');
  return data;
};

export const getOllamaTags = async () => {
  const { data } = await api.get('/ollama/tags');
  return data;
};

export const getTranslations = async () => {
  const { data } = await api.get('/config/i18n');
  return data;
};

export const deleteModel = async (name) => {
  const { data } = await api.delete(`/ollama/models/${name}`);
  return data;
};

export const analyzeLogs = async (source, agent, lines = 100) => {
  const { data } = await api.post('/logs/analyze', { source, agent, lines });
  return data;
};

export const getGoogleModels = async () => {
  const { data } = await api.get('/models/google');
  return data;
};

export const getUsageStats = async () => {
  const { data } = await api.get('/system/usage');
  return data;
};

export const peekLogs = async (source) => {
  const { data } = await api.get(`/logs/peek?source=${source}`);
  return data;
};

export const getSessions = async () => (await api.get('/chat/sessions')).data;
export const getSession = async (id) => (await api.get(`/chat/sessions/${id}`)).data;
export const saveSession = async (sessionData) => (await api.post('/chat/sessions/save', sessionData)).data;
export const resolveContext = async (items) => (await api.post('/context/resolve', { items })).data;
export const getModelSettings = async () => (await api.get('/model/settings')).data;
export const saveModelSettings = async (settings) => (await api.post('/model/settings', settings)).data;
export const getAIOptimization = async () => (await api.post('/model/optimize', {})).data;

// Hugging Face API functions
export const searchHfModels = async (query, limit = 10) => {
  const { data } = await api.get(`/huggingface/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  return data;
};

export const downloadHfModel = async (repoId, filename) => {
  const { data } = await api.post('/huggingface/download', { repoId, filename });
  return data;
};

// ModelScope API functions
export const searchMsModels = async (query, limit = 10) => {
  const { data } = await api.get(`/modelscope/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  return data;
};

export const downloadMsModel = async (modelId) => {
  const { data } = await api.post('/modelscope/download', { modelId });
  return data;
};

// Para streaming necesitamos EventSource nativo o Fetch
export const streamAgentChat = (prompt, history, onChunk, onComplete, onError) => {
  const url = `${API_BASE}/agent/chat`;
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt, history }),
  }).then(async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          onChunk(data);
        }
      }
    }
    onComplete();
  }).catch(onError);
};

export const streamModelPull = (name, onProgress, onComplete, onError) => {
  const url = `http://localhost:8000/api/ollama/pull`;
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  }).then(async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onProgress(data);
          } catch(e) {}
        }
      }
    }
    onComplete();
  }).catch(onError);
};

export default api;
