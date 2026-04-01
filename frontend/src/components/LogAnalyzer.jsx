import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  BrainCircuit, 
  CheckCircle2, 
  AlertCircle,
  Eye,
  ChevronDown,
  Activity,
  Zap,
  BarChart3,
  Database,
  Server,
  LayoutDashboard
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { analyzeLogs, getGoogleModels, getUsageStats, peekLogs } from '../lib/api';

const LogAnalyzer = ({ t, lang }) => {
  const [source, setSource] = useState('app');
  const [provider, setProvider] = useState('google'); // 'google' or 'local'
  const [selectedModel, setSelectedModel] = useState('gemini-1.5-flash');
  const [googleModels, setGoogleModels] = useState([]);
  const [usage, setUsage] = useState({ tokens_consumed: 0, requests_count: 0 });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [showRaw, setShowRaw] = useState(false);
  const [peekContent, setPeekContent] = useState('');
  const [isLoadingPeek, setIsLoadingPeek] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        const [models, stats] = await Promise.all([getGoogleModels(), getUsageStats()]);
        setGoogleModels(models);
        setUsage(stats);
        if (models.length > 0) setSelectedModel(models[0].id);
      } catch (e) {
        console.error('Error fetching models/stats:', e);
      }
    };
    init();
  }, []);

  useEffect(() => {
    const fetchPeek = async () => {
      setIsLoadingPeek(true);
      try {
        const data = await peekLogs(source);
        setPeekContent(data.content);
      } catch (e) {
        setPeekContent('Failed to fetch peek.');
      } finally {
        setIsLoadingPeek(false);
      }
    };
    fetchPeek();
  }, [source]);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setResult(null);
    try {
      const agentId = provider === 'local' ? 'qwen' : selectedModel;
      const data = await analyzeLogs(source, agentId);
      setResult(data);
      // Refresh usage after analysis
      const stats = await getUsageStats();
      setUsage(stats);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const sources = [
    { id: 'app', label: 'App Local', icon: FileText },
    { id: 'mcp', label: 'Servidor MCP', icon: Search },
    { id: 'backend', label: t('source_backend'), icon: Server },
    { id: 'frontend', label: t('source_frontend'), icon: LayoutDashboard },
    { id: 'ollama', label: 'Ollama', icon: BrainCircuit },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-black tracking-tighter text-white">{t('diag_title')}</h2>
          <p className="text-gray-500 font-medium">Neural Log Intelligence & Diagnostic Engine.</p>
        </div>
        
        {/* Usage Stats Widget */}
        <div className="flex gap-4">
          <div className="bg-[#111] border border-gray-800 rounded-2xl px-5 py-3 flex items-center gap-4">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-widest font-bold text-gray-500">{t('usage_tokens')}</p>
              <p className="text-lg font-mono font-bold text-white leading-none">{(usage.tokens_consumed / 1000).toFixed(1)}k</p>
            </div>
          </div>
          <div className="bg-[#111] border border-gray-800 rounded-2xl px-5 py-3 flex items-center gap-4">
            <div className="h-10 w-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <Activity className="h-5 w-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-widest font-bold text-gray-500">{t('usage_requests')}</p>
              <p className="text-lg font-mono font-bold text-white leading-none">{usage.requests_count}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          <section className="bg-[#0f0f0f] border border-gray-800 rounded-3xl p-6 shadow-xl">
            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-6">{t('select_log')}</h4>
            <div className="space-y-2">
              {sources.map(s => (
                <button
                  key={s.id}
                  onClick={() => setSource(s.id)}
                  className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all border ${
                    source === s.id 
                      ? 'bg-primary border-primary text-white shadow-lg shadow-primary/20' 
                      : 'border-white/5 text-gray-500 hover:bg-white/5 hover:text-gray-300'
                  }`}
                >
                  <s.icon className={`h-5 w-5 ${source === s.id ? 'text-white' : ''}`} />
                  <span className="font-bold text-sm tracking-tight">{s.label}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="bg-[#0f0f0f] border border-gray-800 rounded-3xl p-6 shadow-xl">
            <h4 className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-6">{t('select_agent')}</h4>
            <div className="space-y-4">
              {/* Provider Toggles */}
              <div className="flex p-1 bg-black rounded-xl border border-gray-900 mb-6">
                <button 
                  onClick={() => setProvider('google')}
                  className={`flex-1 py-2 text-[10px] font-bold rounded-lg transition-all ${provider === 'google' ? 'bg-gray-800 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                >
                  GOOGLE CLOUD
                </button>
                <button 
                  onClick={() => setProvider('local')}
                  className={`flex-1 py-2 text-[10px] font-bold rounded-lg transition-all ${provider === 'local' ? 'bg-gray-800 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                >
                  LOCAL QWEN
                </button>
              </div>

              {provider === 'google' ? (
                <div className="space-y-3">
                  <div className="relative group">
                    <select 
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full bg-[#1a1a1a] border border-gray-800 text-gray-200 text-xs rounded-xl py-3 px-4 appearance-none focus:outline-none focus:border-primary transition-all group-hover:border-gray-700 font-bold"
                    >
                      {googleModels.map(m => (
                        <option key={m.id} value={m.id} className="bg-[#111]">{m.name}</option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-4 top-3 h-4 w-4 text-gray-500 pointer-events-none" />
                  </div>
                  <p className="text-[9px] text-gray-600 px-1 italic">Selecting model from your Google AI Studio account.</p>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 text-center">
                  <BrainCircuit className="h-8 w-8 text-primary mx-auto mb-2 opacity-50" />
                  <p className="text-[10px] font-bold text-primary">Qwen 2.5 Coder 3B</p>
                  <p className="text-[9px] text-gray-500">Fast, local, offline.</p>
                </div>
              )}
            </div>
          </section>

          {/* Neural Instruction (Prompt) Always Visible */}
          <section className="bg-gradient-to-b from-[#1a1a1a] to-[#0f0f0f] border border-primary/20 rounded-3xl p-6 shadow-xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-30 transition-opacity">
              <BrainCircuit className="h-12 w-12 text-primary" />
            </div>
            <h4 className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
              <Zap className="h-3 w-3 fill-current" /> {t('sys_instructions')}
            </h4>
            <div className="bg-black/50 rounded-xl p-4 border border-white/5">
              <p className="text-[10px] text-gray-400 leading-relaxed font-medium">
                {t('devops_prompt')}
              </p>
            </div>
          </section>

          <button 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="w-full py-4 rounded-3xl bg-white text-black font-black text-sm shadow-2xl hover:bg-gray-200 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100 flex items-center justify-center gap-3 border-4 border-transparent hover:border-primary/20"
          >
            {isAnalyzing ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent" />
            ) : (
              <Zap className="h-5 w-5 fill-current" />
            )}
            {t('btn_analyze').toUpperCase()}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3">
          <AnimatePresence mode="wait">
            {isAnalyzing ? (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="h-full flex flex-col items-center justify-center bg-[#111]/30 backdrop-blur-xl border border-dashed border-gray-800 rounded-[3rem] p-12 min-h-[500px]"
              >
                <div className="relative mb-8">
                  <motion.div 
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                    className="h-24 w-24 rounded-full bg-primary/20 blur-2xl absolute inset-0"
                  />
                  <div className="h-20 w-20 animate-spin rounded-full border-4 border-primary/10 border-t-primary relative z-10" />
                  <BrainCircuit className="h-8 w-8 text-primary absolute inset-0 m-auto animate-pulse z-20" />
                </div>
                <h3 className="text-2xl font-black mb-3 text-white">GENERATING INSIGHTS</h3>
                <p className="text-gray-500 text-sm font-medium tracking-wide">Processing {source.toUpperCase()} events via {provider.toUpperCase()} neural path...</p>
              </motion.div>
            ) : result ? (
              <motion.div 
                key="result"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="bg-gradient-to-br from-[#111] to-[#0a0a0a] border border-gray-800 rounded-[2.5rem] p-10 shadow-3xl relative overflow-hidden group">
                  <div className="absolute -top-24 -right-24 h-64 w-64 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all duration-1000" />
                  
                  <div className="flex items-center gap-4 mb-8">
                    <div className="h-14 w-14 rounded-2xl bg-white/5 flex items-center justify-center border border-white/10">
                      <BarChart3 className="h-7 w-7 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-3xl font-black text-white tracking-tight">{t('dictamen_title').replace('### ', '')}</h3>
                      <p className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-1">Diagnostic Artifact Generated by {provider.toUpperCase()}</p>
                    </div>
                  </div>

                  <div className="prose prose-invert max-w-none">
                    <div className="text-gray-300 leading-relaxed text-lg font-medium whitespace-pre-wrap selection:bg-primary/30">
                      {result.dictamen}
                    </div>
                  </div>

                  <div className="mt-12 pt-8 border-t border-gray-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-6">
                      <div className="flex items-center gap-2 text-[10px] font-bold text-gray-500 bg-black/40 px-3 py-1.5 rounded-full border border-gray-800">
                        <Activity className="h-3 w-3" /> VERDICT: OPTIMAL
                      </div>
                      <div className="flex items-center gap-2 text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20">
                        <CheckCircle2 className="h-3 w-3" /> NO THREADS DETECTED
                      </div>
                    </div>
                    <button 
                      onClick={() => setShowRaw(!showRaw)}
                      className="group flex items-center gap-2 text-xs font-black text-white hover:text-primary transition-all"
                    >
                      <Eye className="h-4 w-4" /> {t('ver_log').toUpperCase()}
                      <motion.div animate={{ x: showRaw ? 2 : 0 }} className="ml-1"><ChevronDown className={`h-4 w-4 transition-transform ${showRaw ? 'rotate-180' : ''}`} /></motion.div>
                    </button>
                  </div>
                </div>

                {showRaw && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                    className="bg-black/90 rounded-3xl border border-gray-800 p-8 font-mono text-xs overflow-x-auto shadow-inner ring-1 ring-white/5"
                  >
                    <div className="flex items-center gap-2 mb-4 text-gray-600 text-[10px] font-bold uppercase tracking-widest">
                      <FileText className="h-3 w-3" /> Source Stream Header (Trailing 100 lines)
                    </div>
                    <pre className="text-gray-400 leading-relaxed">{result.raw_log}</pre>
                  </motion.div>
                )}
              </motion.div>
            ) : (
              <div className="space-y-8 h-full flex flex-col min-h-[500px]">
                {/* Log Peek (Data Flow Preview) */}
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-[2.5rem] p-8 grow flex flex-col shadow-inner group">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                        <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                          <div className="h-2 w-2 rounded-full bg-emerald-500" />
                        </motion.div>
                      </div>
                      <h3 className="text-xs font-black text-gray-400 uppercase tracking-widest">{t('log_peek')}</h3>
                    </div>
                    <div className="text-[10px] font-mono text-gray-600 bg-black px-3 py-1 rounded-full border border-gray-900 group-hover:text-gray-400 transition-colors">
                      LIVE STREAM: {source.toUpperCase()}
                    </div>
                  </div>

                  <div className="flex-1 bg-black/40 rounded-3xl border border-gray-900 p-6 font-mono text-[11px] overflow-auto relative">
                    <div className="absolute inset-x-0 top-0 h-12 bg-gradient-to-b from-black/20 to-transparent pointer-events-none" />
                    {isLoadingPeek ? (
                      <div className="h-full flex items-center justify-center gap-2 text-gray-600 italic animate-pulse">
                        <Activity className="h-4 w-4 animate-spin" /> Sychronizing buffer...
                      </div>
                    ) : (
                      <pre className="text-gray-500 leading-relaxed whitespace-pre-wrap">
                        {peekContent || 'Waiting for stream events...'}
                      </pre>
                    )}
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center grow border-2 border-dashed border-gray-800/30 rounded-[3rem] p-12 text-center opacity-60 hover:opacity-100 transition-opacity">
                  <div className="h-16 w-16 rounded-2xl bg-gray-900/50 border border-gray-800 flex items-center justify-center mb-6">
                    <BrainCircuit className="h-7 w-7 text-gray-700" />
                  </div>
                  <h3 className="text-xl font-black text-gray-500 mb-2 uppercase tracking-tighter">Diagnostic Engine Ready</h3>
                  <p className="text-gray-600 max-w-xs text-[11px] font-medium leading-relaxed">Neural correlation buffer is ready. Select an agent to initiate diagnostic evaluation.</p>
                </div>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default LogAnalyzer;
