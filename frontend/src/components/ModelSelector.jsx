import React from 'react';
import { ChevronDown, Bot, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ModelSelector = ({
  availableModels,
  selectedModel,
  onModelChange,
  modelProvider,
  onProviderChange,
  t,
  compact = false
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const currentModel = availableModels.find(m => m.id === selectedModel) ||
                       availableModels[0] ||
                       { id: 'qwen2.5-coder:3b', name: 'qwen2.5-coder:3b' };

  const formatModelSize = (size) => {
    if (!size) return '';
    const gb = (size / (1024 * 1024 * 1024)).toFixed(1);
    return `${gb}GB`;
  };

  if (compact) {
    return (
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white hover:bg-white/10 transition-all"
        >
          <Bot className="h-3 w-3" />
          <span className="truncate max-w-24">{currentModel.name}</span>
          <ChevronDown className={`h-3 w-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full mt-1 w-64 bg-[#1a1a1a] border border-gray-700 rounded-lg shadow-xl z-50 max-h-60 overflow-y-auto"
            >
              {availableModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    onModelChange(model.id);
                    setIsOpen(false);
                  }}
                  className={`w-full px-3 py-2 text-left hover:bg-white/10 transition-colors flex items-center justify-between ${
                    selectedModel === model.id ? 'bg-primary/20 text-primary' : 'text-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Bot className="h-4 w-4" />
                    <span className="truncate">{model.name}</span>
                  </div>
                  {model.size && (
                    <span className="text-xs text-gray-500">{formatModelSize(model.size)}</span>
                  )}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium text-gray-300">{t('model_selector_title') || 'Modelo IA'}</span>
        </div>
      </div>

      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between p-3 bg-[#1a1a1a] border border-gray-700 rounded-xl hover:border-gray-600 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="text-left">
              <div className="text-sm font-medium text-white">{currentModel.name}</div>
              {currentModel.size && (
                <div className="text-xs text-gray-500">{formatModelSize(currentModel.size)}</div>
              )}
            </div>
          </div>
          <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full mt-2 w-full bg-[#1a1a1a] border border-gray-700 rounded-xl shadow-xl z-50 max-h-60 overflow-y-auto"
            >
              {availableModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => {
                    onModelChange(model.id);
                    setIsOpen(false);
                  }}
                  className={`w-full px-4 py-3 text-left hover:bg-white/10 transition-colors flex items-center justify-between ${
                    selectedModel === model.id ? 'bg-primary/20' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Bot className="h-4 w-4 text-gray-400" />
                    <div>
                      <div className={`text-sm font-medium ${selectedModel === model.id ? 'text-primary' : 'text-white'}`}>
                        {model.name}
                      </div>
                      {model.size && (
                        <div className="text-xs text-gray-500">{formatModelSize(model.size)}</div>
                      )}
                    </div>
                  </div>
                  {selectedModel === model.id && (
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                  )}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ModelSelector;