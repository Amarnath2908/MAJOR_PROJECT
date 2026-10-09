import React from 'react';
import { Sparkles } from 'lucide-react';

const DEFAULT_SUGGESTIONS = [
  'Change the sofa to a dark navy blue modern leather sofa',
  'Paint the walls modern warm light grey',
  'Replace the floor with dark oak hardwood flooring',
  'Change the coffee table to a minimalist glass and walnut table',
  'Add modern recessed warm ceiling lights',
  'Replace the curtains with sheer cream linen drapes',
];

export function SuggestedPrompts({ onSelectPrompt, selectedObject }) {
  // If an object is selected, filter or adapt suggestions
  const suggestions = selectedObject
    ? [
        `Change the ${selectedObject.toLowerCase()} to dark navy modern style`,
        `Replace the ${selectedObject.toLowerCase()} with a luxury minimalist design`,
        `Change the colour of the ${selectedObject.toLowerCase()} to warm beige`,
        `Update the ${selectedObject.toLowerCase()} to modern Scandinavian style`,
      ]
    : DEFAULT_SUGGESTIONS;

  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
        <Sparkles className="w-3.5 h-3.5 text-brand-400" />
        Suggested Prompts
      </span>

      <div className="flex flex-wrap gap-1.5">
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectPrompt(item)}
            className="text-left text-xs bg-slate-800/60 hover:bg-slate-750 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg border border-slate-700/50 transition-colors cursor-pointer"
          >
            "{item}"
          </button>
        ))}
      </div>
    </div>
  );
}

export default SuggestedPrompts;
