import React, { useState } from 'react';
import { Zap, TrendingUp, Cpu, AlertCircle, CheckCircle } from 'lucide-react';

const PerformanceTuner = ({ t, lang }) => {
  const [optimizationLevel, setOptimizationLevel] = useState('balanced');
  const [metrics, setMetrics] = useState(null);

  const handleOptimize = async () => {
    try {
      // En el futuro: llamar a API de optimización
      setMetrics({ cpu: '45%', memory: '62%', gpu: '78%', latency: '125ms' });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex h-full overflow-hidden animate-in slide-in-from-right-4 duration-500">
      <div className="flex-1 space-y-8 overflow-y-auto pr-4 custom-scrollbar">
        <header className="sticky top-0 bg-[#0a0a0a] z-10 pb-4 border-b border-gray-800/50">
          <h2 className="text-3xl font-bold tracking-tight">{t('nav_performance') || 'Performance Tuner'}</h2>
          <p className="text-gray-400">Optimize your AI agent for maximum efficiency.</p>
        </header>

        <section className="space-y-4">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            Optimization Levels
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {['lightweight', 'balanced', 'maximum'].map(level => (
              <button
                key={level}
                onClick={() => setOptimizationLevel(level)}
                className={`p-4 rounded-xl border transition-all text-left ${
                  optimizationLevel === level
                    ? 'bg-primary/20 border-primary'
                    : 'bg-[#1a1a1a] border-gray-800 hover:border-primary/50'
                }`}
              >
                <h4 className="font-bold capitalize">{level}</h4>
                <p className="text-xs text-gray-400 mt-2">
                  {level === 'lightweight' && 'Lower resource usage'}
                  {level === 'balanced' && 'Best for most cases'}
                  {level === 'maximum' && 'Maximum performance'}
                </p>
              </button>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Cpu className="h-5 w-5 text-blue-500" />
            System Metrics
          </h3>
          {metrics ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(metrics).map(([key, value]) => (
                <div key={key} className="bg-[#1a1a1a] border border-gray-800 rounded-xl p-4">
                  <p className="text-xs text-gray-400 capitalize mb-2">{key}</p>
                  <p className="text-2xl font-bold text-primary">{value}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-[#1a1a1a] border border-gray-800 rounded-xl p-6 text-center text-gray-500">
              <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No metrics available. Click optimize to start.</p>
            </div>
          )}
        </section>

        <button
          onClick={handleOptimize}
          className="px-6 py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/80 transition-all flex items-center gap-2"
        >
          <CheckCircle className="h-5 w-5" />
          Start Optimization
        </button>
      </div>
    </div>
  );
};

export default PerformanceTuner;
