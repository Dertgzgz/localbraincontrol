import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Terminal, 
  ShieldCheck, 
  XCircle, 
  Play,
  RotateCcw,
  History,
  Plus,
  Link,
  FileCode,
  ChevronLeft,
  ChevronRight,
  Trash2,
  Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { streamAgentChat, getSessions, getSession, saveSession, resolveContext } from '../lib/api';
import ContextChip from './ContextChip';
import ModelSelector from './ModelSelector';

import { useChat } from '../context/ChatContext';

const ChatTerminal = ({ t, lang }) => {
  const {
    messages, setMessages,
    currentSessionId, setCurrentSessionId,
    sessions, setSessions,
    contextItems, setContextItems,
    isStreaming, setIsStreaming,
    isResolving, setIsResolving,
    availableModels, selectedModel, setSelectedModel,
    modelProvider, setModelProvider,
    fetchSessions,
    clearChat
  } = useChat();

  const [input, setInput] = useState('');
  const [pendingTool, setPendingTool] = useState(null);
  const [showContext, setShowContext] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [contextInput, setContextInput] = useState('');
  
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleLoadSession = async (id) => {
    try {
      const data = await getSession(id);
      setMessages(data.messages || []);
      setCurrentSessionId(id);
      setContextItems(data.context || []);
    } catch (e) { console.error("Error loading session", e); }
  };

  const handleAddContext = () => {
    if (!contextInput.trim()) return;
    const type = contextInput.startsWith('http') ? 'url' : 'file';
    setContextItems(prev => [...prev, { type, value: contextInput.trim() }]);
    setContextInput('');
  };

  const handleRemoveContext = (idx) => {
    setContextItems(prev => prev.filter((_, i) => i !== idx));
  };

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    setIsStreaming(true);
    let currentInput = input;
    
    // Resolve context if any
    let resolvedContextText = "";
    if (contextItems.length > 0) {
      setIsResolving(true);
      try {
        const { resolved } = await resolveContext(contextItems);
        resolvedContextText = resolved.map(r => `[CONTEXT: ${r.type.toUpperCase()} - ${r.value}]\n${r.content}\n[END CONTEXT]`).join('\n\n');
        currentInput = `${resolvedContextText}\n\nUSER REQUEST: ${input}`;
      } catch (e) {
        console.error("Context resolution error", e);
      } finally {
        setIsResolving(false);
      }
    }

    const userMsg = { role: 'user', content: input }; // Keep original for display
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    let assistantContent = "";
    const assistantMsg = { role: 'assistant', content: '', id: Date.now() };
    setMessages(prev => [...prev, assistantMsg]);

    streamAgentChat(
      currentInput, // Send resolved prompt
      messages.map(m => ({ role: m.role, content: m.content })),
      (data) => {
        if (data.type === 'text') {
          assistantContent += data.content;
          setMessages(prev => {
            const last = [...prev];
            last[last.length - 1] = { ...last[last.length - 1], content: assistantContent };
            return last;
          });
        } else if (data.type === 'require_approval') {
          setPendingTool(data.tool_call);
          setMessages(prev => {
            const last = [...prev];
            last[last.length - 1] = { ...last[last.length - 1], content: data.message };
            return last;
          });
        }
      },
      async () => {
        setIsStreaming(false);
        // Auto-save session
        try {
          const res = await saveSession({
            id: currentSessionId,
            title: messages[0]?.content?.substring(0, 30) || "Nueva Conversación",
            messages: [...messages, userMsg, { role: 'assistant', content: assistantContent }],
            context: contextItems
          });
          if (!currentSessionId) setCurrentSessionId(res.id);
          fetchSessions();
        } catch (e) { console.error("Save error", e); }
      },
      (err) => {
        console.error('Chat error:', err);
        setIsStreaming(false);
      }
    );
  };

  const handleToolDecision = (approved) => {
    setPendingTool(null);
    if (approved) {
      setMessages(prev => [...prev, { role: 'assistant', content: t('action_ok') }]);
    }
  };

  return (
    <div className="flex h-[calc(100vh-160px)] bg-[#1a1a1a]/40 border border-gray-800 rounded-2xl overflow-hidden backdrop-blur-xl">
      {/* Sidebar: Historial */}
      <motion.aside 
        animate={{ width: sidebarOpen ? 280 : 0 }}
        className="bg-black/40 border-r border-gray-800 flex flex-col overflow-hidden relative"
      >
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">{t('chat_history')}</h3>
          <button onClick={clearChat} className="p-1.5 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-all">
            <Plus className="h-4 w-4" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {sessions.length > 0 ? sessions.map(s => (
            <button
              key={s.id}
              onClick={() => handleLoadSession(s.id)}
              className={`w-full text-left p-3 rounded-xl transition-all group relative ${currentSessionId === s.id ? 'bg-primary/10 border border-primary/20' : 'hover:bg-white/5 border border-transparent'}`}
            >
              <p className={`text-xs font-bold truncate ${currentSessionId === s.id ? 'text-primary' : 'text-gray-400'}`}>
                {s.title}
              </p>
              <p className="text-[9px] text-gray-600 mt-1 uppercase font-bold tracking-tighter">
                {new Date(parseFloat(s.last_update) * 1000).toLocaleDateString()}
              </p>
            </button>
          )) : (
            <div className="p-8 text-center opacity-30">
              <History className="h-8 w-8 mx-auto mb-2 text-gray-600" />
              <p className="text-[10px] uppercase font-bold">{t('no_history')}</p>
            </div>
          )}
        </div>
      </motion.aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col items-center relative min-w-0">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-50 h-10 w-10 bg-gray-900 border border-gray-800 rounded-full flex items-center justify-center text-gray-500 hover:text-white transition-all shadow-2xl"
        >
          {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </button>

        {/* Header */}
        <div className="w-full px-6 py-4 border-b border-gray-800 bg-[#1a1a1a]/60 backdrop-blur-md flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
              <Terminal className="h-4 w-4 text-primary" />
            </div>
            <div>
              <h3 className="font-premium text-base font-bold tracking-tight text-white">{t('chat_title')}</h3>
              <div className="flex items-center gap-1.5 opacity-80">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                <span className="text-[10px] text-gray-400 font-bold tracking-widest uppercase">Core v2.5 Online</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ModelSelector
              availableModels={availableModels}
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              modelProvider={modelProvider}
              onProviderChange={setModelProvider}
              t={t}
              compact={true}
            />
            <button 
              onClick={() => setShowContext(!showContext)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all border ${showContext ? 'bg-primary/20 text-primary border-primary/30' : 'bg-white/5 text-gray-500 border-white/10 hover:text-white'}`}
            >
              <ShieldCheck className="h-3 w-3" /> {t('neural_context').toUpperCase()}
            </button>
          </div>
        </div>

        {/* System Context Info Panel */}
        <AnimatePresence>
          {showContext && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
              className="w-full bg-primary/5 border-b border-primary/10 overflow-hidden"
            >
              <div className="p-6 flex gap-6 items-start max-w-4xl mx-auto">
                <div className="h-12 w-12 rounded-2xl bg-primary/20 flex items-center justify-center shrink-0 border border-primary/30 shadow-lg">
                  <Bot className="h-6 w-6 text-primary" />
                </div>
                <div className="space-y-2">
                  <h4 className="text-[10px] font-black text-primary uppercase tracking-[0.2em] flex items-center gap-2">
                    <History className="h-3 w-3" /> Neural Directive context
                  </h4>
                  <p className="text-xs text-primary/70 leading-relaxed italic font-medium">
                    "Act as a Senior AI Assistant integrated into the Antigravity local ecosystem. You have access to local tools, secure file processing and hardware control. Maintain maximum analytical precision."
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages area */}
        <div 
          ref={scrollRef}
          className="flex-1 w-full overflow-y-auto px-6 py-8 space-y-6 scroll-smooth scrollbar-hide flex flex-col items-center"
        >
          <div className="w-full max-w-4xl space-y-6">
            <AnimatePresence initial={false}>
              {messages.map((msg, idx) => (
                <motion.div 
                  key={idx}
                  initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                  className={`flex gap-5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="h-10 w-10 rounded-2xl bg-gray-900 flex-shrink-0 flex items-center justify-center border border-gray-800 shadow-xl self-start mt-1">
                      <Bot className="h-5 w-5 text-gray-400" />
                    </div>
                  )}
                  
                  <div className={`max-w-[85%] rounded-[1.8rem] p-6 shadow-3xl backdrop-blur-md relative group transition-all duration-500 hover:ring-2 hover:ring-primary/20 ${
                    msg.role === 'user' 
                      ? 'bg-primary/95 text-white rounded-tr-none border border-white/20' 
                      : 'bg-[#1a1a1a]/95 border border-white/5 text-gray-100 rounded-tl-none'
                  }`}>
                    <div className="text-[14px] leading-relaxed whitespace-pre-wrap font-medium antialiased selection:bg-white/20 select-text outline-none">{msg.content}</div>
                  </div>

                  {msg.role === 'user' && (
                    <div className="h-10 w-10 rounded-2xl bg-primary/20 flex-shrink-0 flex items-center justify-center border border-primary/30 shadow-xl self-start mt-1">
                      <User className="h-5 w-5 text-primary" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {(isStreaming || isResolving) && (
              <div className="flex gap-5">
                <div className="h-10 w-10 rounded-2xl bg-gray-900 flex items-center justify-center animate-pulse border border-gray-800">
                  <Bot className="h-5 w-5 text-gray-600" />
                </div>
                <div className="bg-[#1a1a1a]/40 border border-gray-800 rounded-2xl px-6 py-4 flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">
                    {isResolving ? "Resolving Context..." : "Synchronizing..."}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Context Management Area (Chips) */}
        <div className="w-full max-w-4xl px-6">
          <AnimatePresence>
            {contextItems.length > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
                className="flex flex-wrap gap-2 pb-4 border-b border-white/5"
              >
                {contextItems.map((item, i) => (
                  <ContextChip key={i} item={item} onRemove={() => handleRemoveContext(i)} />
                ))}
                <button 
                  onClick={() => setContextItems([])}
                  className="px-3 py-1.5 rounded-full bg-red-500/10 text-red-500 border border-red-500/20 text-[9px] font-black uppercase hover:bg-red-500/20 transition-all"
                >
                  {t('clear_context')}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Input area */}
        <div className="w-full p-6 bg-gradient-to-t from-black/40 to-transparent flex flex-col items-center shrink-0">
          <div className="w-full max-w-4xl relative group">
            <div className="absolute inset-0 bg-primary/10 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity" />
            
            <div className="relative flex flex-col bg-[#0c0c0c] border border-gray-800 rounded-3xl overflow-hidden shadow-2xl focus-within:border-primary/50 transition-all">
              {/* Context Input Row */}
              <div className="flex items-center px-4 py-2 border-b border-white/5 bg-white/3">
                <Link className="h-3.5 w-3.5 text-gray-600 mr-2" />
                <input 
                  type="text" 
                  value={contextInput}
                  onChange={(e) => setContextInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddContext()}
                  placeholder={t('add_context')}
                  className="flex-1 bg-transparent border-none outline-none text-[10px] text-gray-400 placeholder:text-gray-700 font-bold"
                />
                <button 
                  onClick={handleAddContext}
                  className="p-1.5 hover:bg-white/5 rounded-lg text-gray-500 hover:text-white transition-all"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="flex items-center px-2 py-2">
                <input 
                  type="text" 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isStreaming && handleSend()}
                  disabled={isStreaming || !!pendingTool || isResolving}
                  placeholder={t('chat_placeholder')}
                  className="flex-1 bg-transparent border-none outline-none py-3 px-4 text-sm text-gray-200 placeholder:text-gray-600 disabled:opacity-50"
                />
                <button 
                  onClick={handleSend}
                  disabled={!input.trim() || isStreaming || !!pendingTool || isResolving}
                  className="p-3 bg-primary text-white rounded-2xl shadow-xl shadow-primary/20 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 transition-all mr-1"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
          <p className="text-[9px] text-gray-600 mt-4 font-black uppercase tracking-[0.2em] opacity-40">
            AG-CORE Local Node : GPU-Accelerated Analytics
          </p>
        </div>
      </div>

      {/* Pending Tool Modal Overlay */}
      <AnimatePresence>
        {pendingTool && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-6"
          >
            <div className="bg-[#111] border border-white/10 rounded-[2.5rem] w-full max-w-sm p-8 shadow-4xl ring-1 ring-white/10">
              <div className="flex items-center gap-4 text-amber-500 mb-6">
                <div className="h-12 w-12 rounded-2xl bg-amber-500/10 flex items-center justify-center border border-amber-500/20">
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="font-black text-lg text-white">{t('confirm_req').replace('⚠️ ', '')}</h4>
                  <p className="text-[10px] text-amber-500 font-bold uppercase tracking-widest">Action requires authorization</p>
                </div>
              </div>
              <div className="bg-black border border-white/5 rounded-2xl p-5 mb-8 font-mono text-[10px] shadow-inner max-h-48 overflow-auto">
                <div className="text-primary mb-2 flex items-center gap-2">
                  <FileCode className="h-3 w-3" /> Tool: <span className="text-white font-bold">{pendingTool.name}</span>
                </div>
                <pre className="text-gray-500 leading-relaxed">{JSON.stringify(pendingTool.args, null, 2)}</pre>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <button 
                  onClick={() => handleToolDecision(false)}
                  className="py-4 rounded-2xl border border-white/10 hover:bg-white/5 transition-all text-xs font-black text-gray-400"
                >
                  {t('btn_cancel').replace('❌ ', '').toUpperCase()}
                </button>
                <button 
                  onClick={() => handleToolDecision(true)}
                  className="py-4 rounded-2xl bg-primary text-white hover:bg-primary-dark transition-all text-xs font-black shadow-2xl shadow-primary/30"
                >
                  {t('btn_exec').replace('✅ ', '').toUpperCase()}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ChatTerminal;
