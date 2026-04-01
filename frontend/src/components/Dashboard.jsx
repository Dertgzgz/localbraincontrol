import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  Database, 
  Activity, 
  Box, 
  Layers,
  HardDrive
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { getMetrics, getOllamaStatus, getUsageStats } from '../lib/api';

const Dashboard = ({ t, lang }) => {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [ollamaModels, setOllamaModels] = useState([]);
  const [usage, setUsage] = useState({ tokens_consumed: 0, requests_count: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const m = await getMetrics();
        const models = await getOllamaStatus();
        const stats = await getUsageStats();
        setMetrics(m);
        setOllamaModels(models);
        setUsage(stats);
        
        // Mantener historial de los últimos 20 puntos
        setHistory(prev => {
          const newPoint = {
            time: new Date().toLocaleTimeString(),
            cpu: m.cpu_percent,
            ram: m.ram_percent
          };
          const next = [...prev, newPoint];
          if (next.length > 20) return next.slice(1);
          return next;
        });
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const MetricsCard = ({ icon: Icon, title, value, subValue, progress, color = "primary" }) => (
    <div className="bg-gradient-to-br from-[#1a1a1a]/60 to-[#0c0c0c]/60 border border-gray-800/50 rounded-[2rem] p-7 backdrop-blur-xl shadow-2xl relative overflow-hidden group hover:border-primary/20 transition-all duration-500">
      <div className="absolute -top-12 -right-12 h-32 w-32 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all duration-700" />
      <div className="flex items-center justify-between mb-6">
        <div className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center shadow-inner">
          <Icon className={`h-6 w-6 text-${color}`} />
        </div>
        <span className="font-premium text-4xl font-black tracking-tighter text-white leading-none">{value}</span>
      </div>
      <h3 className="font-premium text-[11px] font-black text-zinc-500 uppercase tracking-[0.25em] mb-4">{title}</h3>
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 bg-black/40 rounded-full overflow-hidden border border-white/5 p-[1px]">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              className={`h-full bg-${color} rounded-full shadow-[0_0_15px_rgba(var(--primary-rgb),0.5)]`} 
            />
          </div>
          <span className="text-[11px] font-mono font-bold text-zinc-400">{progress.toFixed(0)}%</span>
        </div>
        {subValue && <div className="text-[10px] font-bold text-zinc-600 tracking-widest uppercase">{subValue}</div>}
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <header className="flex items-center justify-between">
        <div>
          {/* Título eliminado por solicitud */}
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
          <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[10px] text-green-500 font-bold uppercase tracking-widest">System Operational</span>
        </div>
      </header>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricsCard 
          icon={Cpu} 
          title={t('cpu_total')} 
          value={`${metrics?.cpu_percent.toFixed(1) || 0}%`} 
          progress={metrics?.cpu_percent || 0}
          color="blue-500"
        />
        <MetricsCard 
          icon={HardDrive} 
          title={t('ram_sys')} 
          value={`${metrics?.ram_percent.toFixed(1) || 0}%`} 
          subValue={`${metrics?.ram_used_gb.toFixed(1) || 0} GB / ${metrics?.ram_total_gb.toFixed(1) || 0} GB`}
          progress={metrics?.ram_percent || 0}
          color="accent"
        />
        {metrics?.gpu && (
          <MetricsCard 
            icon={Activity} 
            title={t('gpu_nv')} 
            value={`${metrics.gpu.util}%`}
            subValue={`${(metrics.gpu.mem_used/1024).toFixed(1)}GB / ${(metrics.gpu.mem_total/1024).toFixed(1)}GB`} 
            progress={metrics.gpu.util}
            color="green-500"
          />
        )}
      </div>

      {/* Usage & Quota Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-2xl p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-primary/20 flex items-center justify-center">
              <Database className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest">{t('usage_tokens')}</h4>
              <p className="text-2xl font-black text-white">{(usage.tokens_consumed / 1000).toFixed(1)}k <span className="text-xs text-gray-600 font-medium">/ sessions</span></p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-1 rounded uppercase">Live Tracking</span>
          </div>
        </div>
        <div className="bg-gradient-to-br from-accent/10 to-transparent border border-accent/20 rounded-2xl p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-xl bg-accent/20 flex items-center justify-center">
              <Activity className="h-6 w-6 text-accent" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest">{t('usage_requests')}</h4>
              <p className="text-2xl font-black text-white">{usage.requests_count} <span className="text-xs text-gray-600 font-medium">calls</span></p>
            </div>
          </div>
          <div className="text-right">
             <span className="text-[10px] font-bold text-accent bg-accent/10 px-2 py-1 rounded uppercase">Quota Sync</span>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-[#1a1a1a]/40 border border-gray-800 rounded-2xl p-6">
        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 px-2">Real-time Utilization</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history}>
              <defs>
                <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" vertical={false} />
              <XAxis dataKey="time" hide />
              <YAxis domain={[0, 100]} stroke="#444" fontSize={10} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '12px' }}
                itemStyle={{ fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" strokeWidth={2} />
              <Area type="monotone" dataKey="ram" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorRam)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ollama Models Group */}
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Layers className="h-5 w-5 text-primary" />
          <h3 className="text-xl font-bold tracking-tight">{t('running_models')}</h3>
        </div>
        
        {ollamaModels.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ollamaModels.map((m, idx) => (
              <div key={idx} className="bg-[#1a1a1a]/40 border border-gray-800 rounded-xl p-5 group hover:border-primary/30 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="h-3 w-3 bg-green-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                    <span className="font-bold text-lg">{m.name}</span>
                  </div>
                  <span className="text-[10px] bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-bold">{m.details.parameter_size}</span>
                </div>
                <div className="grid grid-cols-2 gap-y-3 gap-x-6 text-sm">
                  <div>
                    <span className="text-gray-500 text-xs block uppercase font-bold tracking-tighter">{t('family')}</span>
                    <span className="text-gray-300">{m.details.family}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-xs block uppercase font-bold tracking-tighter">{t('quant')}</span>
                    <span className="text-gray-300">{m.details.quantization_level}</span>
                  </div>
                  <div className="col-span-2 mt-2">
                    <span className="text-gray-500 text-xs block uppercase font-bold tracking-tighter mb-1">{t('vram_use')}</span>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1 bg-gray-800 rounded-full">
                        <div 
                          className="h-full bg-green-500" 
                          style={{ width: `${(m.size_vram/(1024**3*12))*100}%` }} 
                        />
                      </div>
                      <span className="text-[10px] text-gray-400">{(m.size_vram/1024**3).toFixed(1)} GB</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-900/50 border border-dashed border-gray-800 rounded-xl p-12 text-center">
            <Box className="h-12 w-12 text-gray-700 mx-auto mb-4" />
            <p className="text-gray-500">{t('no_models')}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
