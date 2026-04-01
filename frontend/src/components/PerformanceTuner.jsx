import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Cpu, 
  Layers, 
  Thermometer, 
  Wand2, 
  Save, 
  RefreshCcw,
  AlertCircle,
  Lightbulb
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getModelSettings, saveModelSettings, getAIOptimization, getMetrics } from '../lib/api';

const PerformanceTuner = ({ t, lang }) => {
  const [settings, setSettings] = useState({
    num_ctx: 16384,
    num_gpu: 100,
    temperature: 0.7
  });
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hardware, setHardware] = useState(null);
  const [aiSuggestion, setAiSuggestion] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [s, h] = await Promise.all([getModelSettings(), getMetrics()]);
      setSettings(s);
      setHardware(h);
    } catch (e) {
      console.error("Error fetching data", e);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await saveModelSettings(settings);
      setIsSaving(false);
    } catch (e) {
      console.error("Error saving settings", e);
      setIsSaving(false);
    }
  };

  const handleAIOptimize = async () => {
    setIsOptimizing(true);
    try {
      const suggestion = await getAIOptimization();
      if (!suggestion.error) {
        setSettings({
          num_ctx: suggestion.num_ctx,
          num_gpu: suggestion.num_gpu,
          temperature: suggestion.temperature
        });
        setAiSuggestion(suggestion.reasoning);
      }
    } catch (e) {
      console.error("AI Optimization failed", e);
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto py-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
            <Zap className="h-6 w-6 text-primary fill-primary/20" />
            {t('perf_title')}
          </h2>
          <p className="text-gray-500 text-xs font-bold uppercase tracking-[0.2em] mt-1">AI INFRASTRUCTURE OPTIMIZER</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={fetchData}
            className="p-2 bg-white/5 rounded-xl border border-white/10 text-gray-400 hover:text-white transition-all shadow-lg"
          >
            <RefreshCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Sliders */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#1a1a1a]/60 border border-gray-800 rounded-[2.5rem] p-8 backdrop-blur-xl relative overflow-hidden ring-1 ring-white/5">
            <div className="space-y-10 relative">
              
              {/* Context Window */}
              <div className="space-y-4">
                <div className="flex justify-between items-center text-xs font-black uppercase tracking-widest text-gray-500">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-emerald-500" />
                    {t('ctx_window')}
                  </div>
                  <span className="text-emerald-500 font-mono text-base">{settings.num_ctx}</span>
                </div>
                <input 
                  type="range" min="1024" max="32768" step="1024"
                  value={settings.num_ctx}
                  onChange={(e) => setSettings({...settings, num_ctx: parseInt(e.target.value)})}
                  className="w-full h-1.5 bg-black/40 rounded-full appearance-none cursor-pointer accent-emerald-500 border border-white/5"
                />
                <div className="flex justify-between text-[9px] text-gray-700 font-bold uppercase">
                  <span>Lite (1k)</span>
                  <span>Full (32k)</span>
                </div>
              </div>

              {/* GPU Layers */}
              <div className="space-y-4">
                <div className="flex justify-between items-center text-xs font-black uppercase tracking-widest text-gray-500">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-blue-500" />
                    {t('gpu_layers')}
                  </div>
                  <span className="text-blue-500 font-mono text-base">{settings.num_gpu}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" step="10"
                  value={settings.num_gpu}
                  onChange={(e) => setSettings({...settings, num_gpu: parseInt(e.target.value)})}
                  className="w-full h-1.5 bg-black/40 rounded-full appearance-none cursor-pointer accent-blue-500 border border-white/5"
                />
                <div className="flex justify-between text-[9px] text-gray-700 font-bold uppercase">
                  <span>CPU Only</span>
                  <span>Max GPU</span>
                </div>
              </div>

              {/* Temperature */}
              <div className="space-y-4">
                <div className="flex justify-between items-center text-xs font-black uppercase tracking-widest text-gray-500">
                  <div className="flex items-center gap-2">
                    <Thermometer className="h-4 w-4 text-orange-500" />
                    {t('temperature')}
                  </div>
                  <span className="text-orange-500 font-mono text-base">{settings.temperature.toFixed(1)}</span>
                </div>
                <input 
                  type="range" min="0" max="1.5" step="0.1"
                  value={settings.temperature}
                  onChange={(e) => setSettings({...settings, temperature: parseFloat(e.target.value)})}
                  className="w-full h-1.5 bg-black/40 rounded-full appearance-none cursor-pointer accent-orange-500 border border-white/5"
                />
                <div className="flex justify-between text-[9px] text-gray-700 font-bold uppercase">
                  <span>Precise (0.0)</span>
                  <span>Creative (1.5)</span>
                </div>
              </div>

              {/* Actions */}
              <div className="pt-4 flex gap-4">
                <button 
                  onClick={handleSave}
                  disabled={isSaving}
                  className="flex-1 py-4 bg-primary text-white rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-2xl shadow-primary/30 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  <Save className="h-4 w-4" />
                  {isSaving ? "Saving..." : t('apply_changes')}
                </button>
                <button 
                  onClick={handleAIOptimize}
                  disabled={isOptimizing}
                  className={`flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3 border shadow-2xl ${isOptimizing ? 'bg-white/5 border-white/10 text-gray-500' : 'bg-white/10 border-white/20 text-white hover:bg-white/15'}`}
                >
                  <Wand2 className={`h-4 w-4 ${isOptimizing ? 'animate-spin' : ''}`} />
                  {isOptimizing ? t('recommending') : t('btn_ai_optimize')}
                </button>
              </div>

            </div>
          </div>
        </div>

        {/* Right Column: AI Suggestions & Context */}
        <div className="space-y-6">
          {/* AI Suggestion Card */}
          <AnimatePresence mode="wait">
            {aiSuggestion && (
              <motion.div 
                initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                className="bg-primary/10 border border-primary/20 rounded-[2rem] p-6 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-4 opacity-10">
                  <Wand2 className="h-16 w-16 text-primary rotate-12" />
                </div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
                    <Lightbulb className="h-4 w-4 text-primary" />
                  </div>
                  <h4 className="text-[10px] font-black text-primary uppercase tracking-widest">AI Advisor Recommendation</h4>
                </div>
                <p className="text-xs text-primary/80 leading-relaxed font-medium italic">
                  "{aiSuggestion}"
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hardware Context */}
          <div className="bg-[#1a1a1a]/40 border border-gray-800 rounded-[2rem] p-6 space-y-6">
            <h4 className="text-[10px] font-black text-gray-500 uppercase tracking-widest flex items-center gap-2">
              <Activity className="h-3 w-3" /> Hardware Analytics
            </h4>
            
            <div className="space-y-4">
              {hardware ? (
                <>
                  <div className="flex justify-between items-center bg-black/30 p-4 rounded-2xl border border-white/5">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                        <Cpu className="h-4 w-4 text-emerald-500" />
                      </div>
                      <span className="text-[10px] font-bold text-gray-400 uppercase">Threads</span>
                    </div>
                    <span className="text-sm font-black text-white">{hardware.cpu_percent}%</span>
                  </div>

                  <div className="flex justify-between items-center bg-black/30 p-4 rounded-2xl border border-white/5">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                        <Layers className="h-4 w-4 text-blue-500" />
                      </div>
                      <span className="text-[10px] font-bold text-gray-400 uppercase">VRAM (GPU)</span>
                    </div>
                    <span className="text-sm font-black text-white">
                      {hardware.gpu ? (hardware.gpu.util).toFixed(0) : "N/A"} %
                    </span>
                  </div>
                </>
              ) : (
                <div className="p-12 flex items-center justify-center opacity-20">
                  <RefreshCcw className="h-6 w-6 animate-spin" />
                </div>
              )}
            </div>

            <div className="p-4 bg-orange-500/5 rounded-2xl border border-orange-500/10 flex items-start gap-3">
              <AlertCircle className="h-4 w-4 text-orange-500/50 mt-0.5" />
              <p className="text-[10px] text-orange-500/60 font-medium leading-relaxed italic">
                Note: Modifications apply to the next request sent to the local agent.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceTuner;
