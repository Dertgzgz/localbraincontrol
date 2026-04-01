import React, { useState } from 'react';
import { 
  Shield, 
  Key, 
  Save, 
  ExternalLink, 
  Lock,
  Globe,
  Database,
  Cloud
} from 'lucide-react';
import { motion } from 'framer-motion';
import api from '../lib/api';

const PROVIDERS = [
  { id: 'google', name: 'Google AI / Gemini', icon: Globe, url: 'https://aistudio.google.com/app/apikey' },
  { id: 'huggingface', name: 'Hugging Face', icon: Cloud, url: 'https://huggingface.co/settings/tokens' },
  { id: 'openai', name: 'OpenAI', icon: Globe, url: 'https://platform.openai.com/api-keys' },
  { id: 'anthropic', name: 'Anthropic', icon: Shield, url: 'https://console.anthropic.com/settings/keys' },
];

const Settings = ({ t, lang }) => {
  const [keys, setKeys] = useState({});
  const [saving, setSaving] = useState(null);

  const handleSave = async (provider) => {
    const key = keys[provider];
    if (!key) return;
    setSaving(provider);
    try {
      await api.post('/config/credentials', { provider, key });
      alert('Key saved successfully!');
    } catch (e) {
      alert('Error saving key');
    } finally {
      setSaving(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <header>
        <h2 className="text-3xl font-bold tracking-tight">System Settings</h2>
        <p className="text-gray-400">Configure credentials and cloud provider integrations.</p>
      </header>

      <section className="bg-[#111] border border-gray-800 rounded-3xl overflow-hidden">
        <div className="p-6 border-b border-gray-800 flex items-center gap-3">
          <Key className="h-5 w-5 text-primary" />
          <h3 className="font-bold">Credential Vault</h3>
        </div>
        
        <div className="divide-y divide-gray-800">
          {PROVIDERS.map((p) => (
            <div key={p.id} className="p-6 flex items-center justify-between hover:bg-white/[0.01] transition-colors">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-xl bg-gray-900 flex items-center justify-center border border-gray-800">
                  <p.icon className="h-5 w-5 text-gray-400" />
                </div>
                <div>
                  <h4 className="font-bold text-gray-200">{p.name}</h4>
                  <a href={p.url} target="_blank" rel="noreferrer" className="text-[10px] text-primary flex items-center gap-1 hover:underline">
                    Get API Key <ExternalLink className="h-2 w-2" />
                  </a>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="relative">
                  <input 
                    type="password" 
                    placeholder="••••••••••••••••"
                    value={keys[p.id] || ''}
                    onChange={(e) => setKeys({ ...keys, [p.id]: e.target.value })}
                    className="bg-black border border-gray-800 rounded-xl px-4 py-2 text-xs w-64 focus:outline-none focus:border-primary transition-all"
                  />
                  <Lock className="h-3 w-3 text-gray-700 absolute right-3 top-2.5" />
                </div>
                <button 
                  onClick={() => handleSave(p.id)}
                  disabled={saving === p.id}
                  className="p-2 bg-primary rounded-xl text-white hover:bg-primary-dark transition-all disabled:opacity-50"
                >
                  {saving === p.id ? <Database className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-6 flex gap-4">
        <Shield className="h-6 w-6 text-amber-500 shrink-0" />
        <div className="space-y-1">
          <h4 className="font-bold text-amber-500 text-sm">Security Advisory</h4>
          <p className="text-[11px] text-amber-500/70 leading-relaxed">
            Keys are stored locally in the server configuration. Ensure your local environment is secured. 
            Remote search and downloads from Hugging Face will use these credentials when required.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Settings;
