import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { ChatProvider } from './context/ChatContext.jsx'
import { AuthProvider } from './context/AuthContext.jsx'
import api from './lib/api.js'

// Función para enviar errores al backend
const logErrorToBackend = async (error, component = 'frontend') => {
  try {
    const errorData = {
      message: error.message || 'Unknown error',
      stack: error.stack || '',
      url: window.location.href,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      component: component
    };

    await api.post('/errors/log', { error: errorData, component });
  } catch (e) {
    console.error('Failed to log error to backend:', e);
  }
};

// Capturar errores no manejados
window.addEventListener('error', (event) => {
  logErrorToBackend({
    message: event.message,
    stack: event.error?.stack || '',
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno
  });
});

// Capturar promesas rechazadas no manejadas
window.addEventListener('unhandledrejection', (event) => {
  logErrorToBackend({
    message: `Unhandled promise rejection: ${event.reason}`,
    stack: event.reason?.stack || ''
  });
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <ChatProvider>
        <App />
      </ChatProvider>
    </AuthProvider>
  </StrictMode>,
)
