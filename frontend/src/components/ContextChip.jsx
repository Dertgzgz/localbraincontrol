import React from 'react';
import { FileText, Globe, X } from 'lucide-react';

const ContextChip = ({ item, onRemove }) => {
  const isUrl = item.type === 'url';
  const Icon = isUrl ? Globe : FileText;
  
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 hover:border-primary/30 transition-all group max-w-[200px]">
      <div className={`p-1 rounded-full ${isUrl ? 'bg-blue-500/10 text-blue-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
        <Icon className="h-3 w-3" />
      </div>
      <span className="text-[10px] font-bold text-gray-400 truncate flex-1">
        {item.value.split('/').pop() || item.value}
      </span>
      <button 
        onClick={onRemove}
        className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-white/10 rounded-full transition-all text-gray-500 hover:text-white"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
};

export default ContextChip;
