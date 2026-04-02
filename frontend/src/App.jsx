import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  MessageSquare, 
  FileSearch, 
  Settings as LucideSettings, 
  LayoutDashboard,
  Cpu,
  Database,
  Terminal,
  Languages,
  ChevronRight,
  Package,
  LogOut
} from 'lucide-react';
import { getTranslations } from './lib/api';
import { useAuth } from './context/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ChatTerminal from './components/ChatTerminal';
import LogAnalyzer from './components/LogAnalyzer';
import ModelManager from './components/ModelManager';
import PerformanceTuner from './components/PerformanceTuner';
import Settings from './components/Settings';

function App() {
  const { user, logout, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [lang, setLang] = useState('es');
  const [translations, setTranslations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchI18n = async () => {
      try {
        const data = await getTranslations();
        setTranslations(data);
      } catch (err) {
        console.error('Error loading i18n:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchI18n();
  }, []);

  const t = (key) => {
    if (!translations || !translations[key]) return key;
    return translations[key][lang] || translations[key]['es'];
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: t('nav_dashboard') },
    { id: 'chat', icon: MessageSquare, label: t('nav_terminal') },
    { id: 'perf', icon: LucideSettings, label: t('nav_perf') },
    { id: 'logs', icon: FileSearch, label: t('diag_title') },
    { id: 'models', icon: Package, label: t('nav_models') },
    { id: 'settings', icon: Database, label: t('nav_settings') },
  ];

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-[#0c0c0c]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-gray-400 animate-pulse">Inizializing Antigravity...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full bg-[#0c0c0c] text-white">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-[#0c0c0c] flex flex-col p-6 shadow-2xl relative z-10">
        <div className="flex items-center gap-4 mb-10 px-2 group cursor-pointer">
          <div className="h-10 w-10 rounded-2xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20 group-hover:scale-110 transition-transform duration-300">
            <Cpu className="h-6 w-6 text-white" />
          </div>
          <h1 className="font-premium text-2xl font-black tracking-tighter text-white">Antigravity</h1>
        </div>

        <nav className="flex-1 space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                activeTab === item.id 
                  ? 'bg-primary/10 text-primary border border-primary/20' 
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
              {activeTab === item.id && <ChevronRight className="ml-auto h-4 w-4" />}
            </button>
          ))}
        </nav>

        <div className="mt-auto pt-4 border-t border-gray-800">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-white/5 hover:text-white transition-all mb-4"
          >
            <LogOut className="h-5 w-5" />
            <span className="font-medium">Cerrar Sesión</span>
          </button>
          <div className="flex items-center gap-3 px-2 mb-4">
            <Languages className="h-4 w-4 text-gray-500" />
            <select 
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="bg-transparent text-sm text-gray-300 focus:outline-none border-none cursor-pointer hover:text-white"
            >
              <option value="es" className="bg-[#1a1a1a]">Español</option>
              <option value="en" className="bg-[#1a1a1a]">English</option>
              <option value="eu" className="bg-[#1a1a1a]">Euskara</option>
            </select>
          </div>
          <div className="text-[10px] text-gray-600 px-2 uppercase tracking-widest font-bold opacity-50">
            Local Agent v2.0
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-8">
        <div className="max-w-6xl mx-auto">
          {activeTab === 'dashboard' && <Dashboard t={t} lang={lang} />}
          {activeTab === 'chat' && <ChatTerminal t={t} lang={lang} />}
          {activeTab === 'perf' && <PerformanceTuner t={t} lang={lang} />}
          {activeTab === 'logs' && <LogAnalyzer t={t} lang={lang} />}
          {activeTab === 'models' && <ModelManager t={t} lang={lang} />}
          {activeTab === 'settings' && <Settings t={t} lang={lang} />}
        </div>
      </main>
    </div>
  );
}

export default App;
