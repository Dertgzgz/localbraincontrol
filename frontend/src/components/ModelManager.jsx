import React, { useState, useEffect, useRef } from 'react';
import { Package, Download, Trash2, Search, Loader2, Globe, Code, Eye, Zap, MessageSquare, HardDrive, Cpu, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getOllamaTags, deleteModel, streamModelPull, searchHfModels, downloadHfModel, searchMsModels, downloadMsModel } from '../lib/api';

const CATEGORIES = [
  { id: 'general', key: 'cat_general', icon: Globe, color: 'blue' },
  { id: 'coding', key: 'cat_coding', icon: Code, color: 'emerald' },
  { id: 'vision', key: 'cat_vision', icon: Eye, color: 'purple' },
  { id: 'small', key: 'cat_small', icon: Zap, color: 'amber' },
];

const PRESET_MODELS = [
  { id: 'llama3.1', name: 'Llama 3.1', category: 'general', desc: 'Meta high-performance model' },
  { id: 'mistral', name: 'Mistral 7B', category: 'general', desc: 'Powerful 7B model' },
  { id: 'qwen2.5-coder:3b', name: 'Qwen 2.5 Coder', category: 'coding', desc: 'Optimized for coding' },
  { id: 'codellama', name: 'CodeLlama', category: 'coding', desc: 'Specialized coding assistant' },
  { id: 'llava', name: 'LLaVA', category: 'vision', desc: 'Multi-modal model' },
  { id: 'moondream', name: 'Moondream 2', category: 'vision', desc: 'Tiny vision model' },
  { id: 'phi3:mini', name: 'Phi-3 Mini', category: 'small', desc: 'Extremely efficient' },
  { id: 'gemma2:2b', name: 'Gemma 2 2B', category: 'small', desc: 'Lightweight model' },
];

const ModelManager = ({ t, lang }) => {
  // Local models state
  const [localModels, setLocalModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pullingModel, setPullingModel] = useState(null);
  const [pullProgress, setPullProgress] = useState(0);
  const [pullStatus, setPullStatus] = useState('');
  const [customPath, setCustomPath] = useState('D:\\Models\\Ollama');
  const [showAdvisor, setShowAdvisor] = useState(false);

  // Advisor state
  const [advisorChat, setAdvisorChat] = useState([]);
  const [advisorInput, setAdvisorInput] = useState('');
  const [advisorLoading, setAdvisorLoading] = useState(false);
  const advisorEndRef = useRef(null);

  // Tab state
  const [activeTab, setActiveTab] = useState('presets');

  // Hugging Face state
  const [hfSearchQuery, setHfSearchQuery] = useState('');
  const [hfSearchResults, setHfSearchResults] = useState([]);
  const [hfSearching, setHfSearching] = useState(false);
  const [downloadingHfModel, setDownloadingHfModel] = useState(null);

  // ModelScope state
  const [msSearchQuery, setMsSearchQuery] = useState('');
  const [msSearchResults, setMsSearchResults] = useState([]);
  const [msSearching, setMsSearching] = useState(false);
  const [downloadingMsModel, setDownloadingMsModel] = useState(null);

  // System resources state
  const [systemResources, setSystemResources] = useState({
    ram: 32, // GB
    gpu: 'NVIDIA RTX 4060',
    gpuVram: 8, // GB
    cpu: 'Intel i7-13700K',
    availableDisk: 500 // GB
  });

  const refreshModels = async () => {
    try {
      const tags = await getOllamaTags();
      setLocalModels(tags || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // Get visible models based on active tab
  const getVisibleModels = () => {
    switch (activeTab) {
      case 'presets':
        return PRESET_MODELS;
      case 'huggingface':
        return hfSearchResults;
      case 'modelscope':
        return msSearchResults;
      default:
        return [];
    }
  };

  // Analyze model compatibility with system resources
  const analyzeModelCompatibility = (model) => {
    const { ram, gpuVram } = systemResources;
    
    // Estimate model requirements based on name and size
    let estimatedRam = 4; // GB minimum
    let estimatedVram = 2; // GB minimum
    
    const name = model.name?.toLowerCase() || model.id?.toLowerCase() || '';
    
    // Large models (70B+ parameters)
    if (name.includes('70b') || name.includes('72b') || name.includes('65b')) {
      estimatedRam = 64;
      estimatedVram = 24;
    }
    // Medium models (13B-30B parameters)  
    else if (name.includes('30b') || name.includes('13b') || name.includes('20b')) {
      estimatedRam = 32;
      estimatedVram = 12;
    }
    // Small models (7B-13B parameters)
    else if (name.includes('7b') || name.includes('8b') || name.includes('9b') || name.includes('10b')) {
      estimatedRam = 16;
      estimatedVram = 8;
    }
    // Tiny models (1B-3B parameters)
    else if (name.includes('1b') || name.includes('2b') || name.includes('3b') || name.includes('mini')) {
      estimatedRam = 8;
      estimatedVram = 4;
    }
    
    // Vision models need more VRAM
    if (name.includes('vision') || name.includes('llava') || name.includes('moondream')) {
      estimatedVram += 2;
    }
    
    return {
      compatible: ram >= estimatedRam && gpuVram >= estimatedVram,
      estimatedRam,
      estimatedVram,
      ramOk: ram >= estimatedRam,
      vramOk: gpuVram >= estimatedVram
    };
  };

  // Generate intelligent recommendations
  const generateRecommendations = (models) => {
    if (!models || models.length === 0) {
      return "No models to analyze. Try searching for models first.";
    }

    const { ram, gpuVram } = systemResources;
    const compatible = [];
    const incompatible = [];
    
    models.forEach(model => {
      const analysis = analyzeModelCompatibility(model);
      if (analysis.compatible) {
        compatible.push({ ...model, analysis });
      } else {
        incompatible.push({ ...model, analysis });
      }
    });

    let recommendations = `📊 **System Analysis:**\n`;
    recommendations += `• RAM: ${ram}GB | GPU VRAM: ${gpuVram}GB\n`;
    recommendations += `• Compatible models: ${compatible.length}/${models.length}\n\n`;

    if (compatible.length > 0) {
      recommendations += `✅ **Recommended for your system:**\n`;
      compatible.slice(0, 3).forEach((model, idx) => {
        const name = model.name || model.id || 'Unknown';
        recommendations += `${idx + 1}. **${name}**\n`;
        recommendations += `   • RAM: ${model.analysis.estimatedRam}GB | VRAM: ${model.analysis.estimatedVram}GB\n`;
      });
      recommendations += `\n`;
    }

    if (incompatible.length > 0) {
      recommendations += `⚠️ **Too demanding for your system:**\n`;
      incompatible.slice(0, 2).forEach(model => {
        const name = model.name || model.id || 'Unknown';
        const issues = [];
        if (!model.analysis.ramOk) issues.push(`RAM: ${model.analysis.estimatedRam}GB needed`);
        if (!model.analysis.vramOk) issues.push(`VRAM: ${model.analysis.estimatedVram}GB needed`);
        recommendations += `• ${name} (${issues.join(', ')})\n`;
      });
    }

    if (compatible.length === 0) {
      recommendations += `💡 **Suggestions:**\n`;
      recommendations += `• Consider smaller models (7B-13B parameters)\n`;
      recommendations += `• Look for quantized versions (Q4, Q8)\n`;
      recommendations += `• Check models optimized for your GPU architecture\n`;
    }

    return recommendations;
  };

  useEffect(() => {
    refreshModels();
  }, []);

  useEffect(() => {
    advisorEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [advisorChat]);

  // Update system resources when advisor opens
  useEffect(() => {
    if (showAdvisor) {
      // In a real app, this would fetch from backend
      // For now, we'll use the static values but could be made dynamic
      setSystemResources(prev => ({ ...prev }));
    }
  }, [showAdvisor]);

  // Auto-suggest analysis when tab changes and advisor is open
  useEffect(() => {
    if (showAdvisor && advisorChat.length === 0) {
      const visibleModels = getVisibleModels();
      if (visibleModels.length > 0) {
        const welcomeMsg = { 
          role: 'assistant', 
          content: `👋 ¡Bienvenido! Veo que tienes ${visibleModels.length} modelos visibles en la pestaña **${activeTab === 'presets' ? 'Modelos Predefinidos' : activeTab === 'huggingface' ? 'Hugging Face' : 'ModelScope'}**.\n\n¿Quieres que analice cuáles son compatibles con tu sistema (${systemResources.ram}GB RAM, ${systemResources.gpuVram}GB VRAM)?` 
        };
        setAdvisorChat([welcomeMsg]);
      }
    }
  }, [activeTab, showAdvisor]);

  const isInstalled = (id) => localModels.some(m => m.name.split(':')[0] === id.split(':')[0]);

  const handlePull = (name) => {
    if (pullingModel) return;
    setPullingModel(name);
    setPullProgress(0);
    setPullStatus(t('pulling') || 'Pulling...');

    streamModelPull(name, (data) => {
      if (data.status === 'downloading' && data.total) {
        const p = (data.completed / data.total) * 100;
        setPullProgress(p);
        setPullStatus(`${t('pulling')} ${Math.round(p)}%`);
      } else {
        setPullStatus(data.status);
      }
    }, () => {
      setPullingModel(null);
      refreshModels();
    }, (err) => {
      console.error(err);
      setPullingModel(null);
    });
  };

  const handleDelete = async (name) => {
    if (!window.confirm(t('confirm_delete') || 'Delete model?')) return;
    try {
      await deleteModel(name);
      refreshModels();
    } catch (e) {
      alert('Error deleting model');
    }
  };

  const handleHfSearch = async () => {
    if (!hfSearchQuery.trim()) return;
    setHfSearching(true);
    try {
      const results = await searchHfModels(hfSearchQuery, 20);
      setHfSearchResults(results || []);
    } catch (e) {
      console.error('Search error:', e);
      setHfSearchResults([]);
    } finally {
      setHfSearching(false);
    }
  };

  const handleHfDownload = async (repoId, filename) => {
    if (downloadingHfModel) return;
    setDownloadingHfModel(`${repoId}/${filename}`);
    try {
      const result = await downloadHfModel(repoId, filename);
      alert(result.status === 'success' ? 'Downloaded!' : `Error: ${result.message}`);
      refreshModels();
    } catch (e) {
      alert('Error downloading model');
    } finally {
      setDownloadingHfModel(null);
    }
  };

  const handleMsSearch = async () => {
    if (!msSearchQuery.trim()) return;
    setMsSearching(true);
    try {
      const results = await searchMsModels(msSearchQuery, 20);
      setMsSearchResults(results || []);
    } catch (e) {
      console.error('Search error:', e);
      setMsSearchResults([]);
    } finally {
      setMsSearching(false);
    }
  };

  const handleMsDownload = async (modelId) => {
    if (downloadingMsModel) return;
    setDownloadingMsModel(modelId);
    try {
      const result = await downloadMsModel(modelId);
      alert(result.status === 'success' ? 'Downloaded!' : `Error: ${result.message}`);
      refreshModels();
    } catch (e) {
      alert('Error downloading model');
    } finally {
      setDownloadingMsModel(null);
    }
  };

  const handleAdvisorSubmit = async (e) => {
    e.preventDefault();
    if (!advisorInput.trim() || advisorLoading) return;

    const userMsg = { role: 'user', content: advisorInput };
    setAdvisorChat(prev => [...prev, userMsg]);
    setAdvisorInput('');
    setAdvisorLoading(true);

    try {
      const visibleModels = getVisibleModels();
      let response = '';

      if (advisorInput.toLowerCase().includes('analyze') || 
          advisorInput.toLowerCase().includes('recommend') || 
          advisorInput.toLowerCase().includes('compatible')) {
        
        response = generateRecommendations(visibleModels);
        
      } else if (advisorInput.toLowerCase().includes('system') || 
                 advisorInput.toLowerCase().includes('specs') || 
                 advisorInput.toLowerCase().includes('resources')) {
        
        response = `🖥️ **Your System Resources:**\n\n`;
        response += `**Hardware:**\n`;
        response += `• CPU: ${systemResources.cpu}\n`;
        response += `• RAM: ${systemResources.ram}GB\n`;
        response += `• GPU: ${systemResources.gpu}\n`;
        response += `• GPU VRAM: ${systemResources.gpuVram}GB\n`;
        response += `• Available Disk: ${systemResources.availableDisk}GB\n\n`;
        
        response += `**Current Tab:** ${activeTab === 'presets' ? 'Preset Models' : activeTab === 'huggingface' ? 'Hugging Face Search' : 'ModelScope Search'}\n`;
        response += `**Models visible:** ${visibleModels.length}\n\n`;
        
        response += `💡 **Tip:** Ask me to "analyze compatible models" to see recommendations based on your hardware!`;
        
      } else {
        // General AI assistant response
        const context = `You are an AI Model Advisor. The user has a system with ${systemResources.ram}GB RAM, ${systemResources.gpuVram}GB GPU VRAM, and is currently viewing ${visibleModels.length} models in the ${activeTab} tab. Provide helpful advice about AI model selection and system compatibility.`;
        
        response = `🤖 Based on your question "${advisorInput}" and your current view of ${visibleModels.length} models:\n\n`;
        
        if (visibleModels.length > 0) {
          response += `I can see you're looking at models in the **${activeTab}** section. `;
          response += `Would you like me to analyze which of these models are compatible with your ${systemResources.ram}GB RAM and ${systemResources.gpuVram}GB GPU VRAM system?\n\n`;
          response += `Try asking: "analyze compatible models" or "recommend best models for my system"`;
        } else {
          response += `You don't have any models visible right now. Try searching for models in Hugging Face or ModelScope tabs, or check the preset models.\n\n`;
          response += `I can help you choose models that work well with your ${systemResources.ram}GB RAM system!`;
        }
      }

      const assistantMsg = { role: 'assistant', content: response };
      setAdvisorChat(prev => [...prev, assistantMsg]);
      
    } catch (e) {
      console.error(e);
      const errorMsg = { role: 'assistant', content: 'Sorry, I encountered an error analyzing your models. Please try again.' };
      setAdvisorChat(prev => [...prev, errorMsg]);
    } finally {
      setAdvisorLoading(false);
    }
  };

  return (
    <div className="flex h-full gap-8 overflow-hidden">
      <div className="flex-1 space-y-8 overflow-y-auto pr-4">
        <header className="sticky top-0 bg-[#0a0a0a] z-10 pb-4 border-b border-gray-800/50 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">{t('nav_models') || 'Model Manager'}</h2>
            <p className="text-gray-400">Manage AI models and repositories</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-[#1a1a1a] border border-gray-800 rounded-xl px-3 py-1.5">
              <HardDrive className="h-4 w-4" />
              <input type="text" value={customPath} onChange={(e) => setCustomPath(e.target.value)} className="bg-transparent text-xs text-gray-400 focus:outline-none w-40" />
            </div>
            <button onClick={() => setShowAdvisor(!showAdvisor)} className={`p-2 rounded-xl border ${showAdvisor ? 'bg-primary/20 border-primary' : 'bg-[#1a1a1a] border-gray-800'}`}>
              <MessageSquare className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Tabs */}
        <div className="flex gap-1 bg-[#1a1a1a]/40 p-1 rounded-xl">
          <button onClick={() => setActiveTab('presets')} className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium ${activeTab === 'presets' ? 'bg-primary text-white' : 'text-gray-400'}`}>Presets</button>
          <button onClick={() => setActiveTab('huggingface')} className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium ${activeTab === 'huggingface' ? 'bg-primary text-white' : 'text-gray-400'}`}>Hugging Face</button>
          <button onClick={() => setActiveTab('modelscope')} className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium ${activeTab === 'modelscope' ? 'bg-primary text-white' : 'text-gray-400'}`}>ModelScope</button>
        </div>

        {/* Presets Tab */}
        {activeTab === 'presets' && (
          <>
            {CATEGORIES.map(cat => (
              <section key={cat.id} className="space-y-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <cat.icon className="h-5 w-5" />
                  {t(cat.key) || cat.id}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                  {PRESET_MODELS.filter(m => m.category === cat.id).map(model => (
                    <div key={model.id} className="bg-[#1a1a1a] border border-gray-800 rounded-2xl p-5">
                      <h4 className="font-bold text-gray-200 mb-2">{model.name}</h4>
                      <p className="text-xs text-gray-500 mb-4">{model.desc}</p>
                      <button onClick={() => handlePull(model.id)} disabled={isInstalled(model.id) || pullingModel === model.id} className={`w-full py-2 rounded-xl text-xs font-bold ${isInstalled(model.id) ? 'bg-gray-700 text-gray-400' : 'bg-primary text-white hover:bg-primary/80'}`}>
                        {pullingModel === model.id ? <Loader2 className="h-3 w-3 inline animate-spin mr-1" /> : <Download className="h-3 w-3 inline mr-1" />}
                        {isInstalled(model.id) ? 'INSTALLED' : 'PULL'}
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            ))}

            {/* Installed Models */}
            <section className="pt-12 border-t border-gray-800">
              <h3 className="text-xl font-bold mb-4">Installed Models ({localModels.length})</h3>
              {localModels.length > 0 ? (
                <div className="bg-[#111] border border-gray-800 rounded-2xl overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="text-xs bg-[#1a1a1a] border-b border-gray-800">
                      <tr>
                        <th className="px-6 py-4 text-left">Model</th>
                        <th className="px-6 py-4 text-left">Size</th>
                        <th className="px-6 py-4 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                      {localModels.map((m, idx) => (
                        <tr key={idx} className="hover:bg-white/5">
                          <td className="px-6 py-4 text-gray-300">{m.name}</td>
                          <td className="px-6 py-4 text-gray-400">{(m.size / 1024**3).toFixed(2)} GB</td>
                          <td className="px-6 py-4 text-center"><button onClick={() => handleDelete(m.name)} className="text-red-500 hover:text-red-600"><Trash2 className="h-4 w-4" /></button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="bg-[#1a1a1a] border border-gray-800 rounded-2xl p-8 text-center text-gray-500">No models installed</div>
              )}
            </section>
          </>
        )}

        {/* Hugging Face Tab */}
        {activeTab === 'huggingface' && (
          <div className="space-y-6">
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-2xl p-4 flex gap-4">
              <input type="text" value={hfSearchQuery} onChange={(e) => setHfSearchQuery(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleHfSearch()} placeholder="Search GGUF models..." className="flex-1 bg-black/30 border border-gray-700 rounded-xl px-4 py-2 text-white focus:outline-none" />
              <button onClick={handleHfSearch} disabled={hfSearching} className="px-6 py-2 bg-primary text-white rounded-xl hover:bg-primary/80 disabled:opacity-50">{hfSearching ? 'Searching...' : 'Search'}</button>
            </div>
            {hfSearchResults.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {hfSearchResults.map((model, idx) => (
                  <div key={idx} className="bg-[#1a1a1a] border border-gray-800 rounded-xl p-4">
                    <h4 className="font-bold text-gray-200 text-sm mb-2">{model.name}</h4>
                    <p className="text-xs text-gray-500 mb-4">{model.id}</p>
                    <button onClick={() => handleHfDownload(model.id, `${model.name}.gguf`)} className="w-full py-2 text-xs bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30">{downloadingHfModel === `${model.id}/${model.name}.gguf` ? 'Downloading...' : 'Download'}</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ModelScope Tab */}
        {activeTab === 'modelscope' && (
          <div className="space-y-6">
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-2xl p-4 flex gap-4">
              <input type="text" value={msSearchQuery} onChange={(e) => setMsSearchQuery(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleMsSearch()} placeholder="Search ModelScope..." className="flex-1 bg-black/30 border border-gray-700 rounded-xl px-4 py-2 text-white focus:outline-none" />
              <button onClick={handleMsSearch} disabled={msSearching} className="px-6 py-2 bg-green-600 text-white rounded-xl hover:bg-green-500 disabled:opacity-50">{msSearching ? 'Searching...' : 'Search'}</button>
            </div>
            {msSearchResults.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {msSearchResults.map((model, idx) => (
                  <div key={idx} className="bg-[#1a1a1a] border border-gray-800 rounded-xl p-4">
                    <h4 className="font-bold text-gray-200 text-sm mb-2">{model.name}</h4>
                    <p className="text-xs text-gray-500 mb-4">{model.id}</p>
                    <button onClick={() => handleMsDownload(model.id)} className="w-full py-2 text-xs bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30">{downloadingMsModel === model.id ? 'Downloading...' : 'Download'}</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Advisor Sidebar */}
      <AnimatePresence>
        {showAdvisor && (
          <motion.aside initial={{ x: 400 }} animate={{ x: 0 }} exit={{ x: 400 }} className="w-96 bg-[#111] border-l border-gray-800 flex flex-col">
            <div className="p-6 border-b border-gray-800">
              <h3 className="font-bold text-lg mb-1">AI Model Advisor</h3>
              <p className="text-xs text-gray-500">Intelligent analysis of visible models & resource-based recommendations</p>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div className="bg-primary/5 border border-primary/10 rounded-2xl p-4 text-xs text-gray-400 italic">
                "¡Hola! Soy tu asesor inteligente de modelos AI. Analizo los modelos que tienes visibles en pantalla y te doy recomendaciones basadas en tus recursos del sistema ({systemResources.ram}GB RAM, {systemResources.gpuVram}GB VRAM)."
              </div>
              
              {/* Quick action buttons */}
              <div className="flex flex-wrap gap-2">
                <button 
                  onClick={() => setAdvisorInput('analyze compatible models')}
                  className="px-3 py-1 bg-primary/20 text-primary text-xs rounded-lg hover:bg-primary/30 transition-colors"
                >
                  📊 Analyze Models
                </button>
                <button 
                  onClick={() => setAdvisorInput('show system specs')}
                  className="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-lg hover:bg-blue-500/30 transition-colors"
                >
                  🖥️ System Info
                </button>
                <button 
                  onClick={() => setAdvisorInput('recommend best models')}
                  className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-lg hover:bg-green-500/30 transition-colors"
                >
                  🎯 Best Picks
                </button>
              </div>
              
              {advisorChat.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl p-4 text-xs ${
                    msg.role === 'user' 
                      ? 'bg-primary text-white rounded-tr-none' 
                      : 'bg-[#1a1a1a] text-gray-300 border border-gray-800 rounded-tl-none'
                  }`}>
                    <div className="whitespace-pre-line">{msg.content}</div>
                  </div>
                </div>
              ))}
              {advisorLoading && <div className="text-center"><Loader2 className="h-4 w-4 animate-spin text-primary mx-auto" /></div>}
              <div ref={advisorEndRef} />
            </div>
            <form onSubmit={handleAdvisorSubmit} className="p-6 border-t border-gray-800">
              <input type="text" value={advisorInput} onChange={(e) => setAdvisorInput(e.target.value)} placeholder="Ask..." className="w-full bg-[#1a1a1a] border border-gray-800 rounded-xl py-2 px-3 text-xs focus:outline-none focus:border-primary" />
            </form>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ModelManager;
