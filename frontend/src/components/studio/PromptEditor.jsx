import React, { useEffect } from 'react';
import { Wand2, Target, HelpCircle, ArrowRight } from 'lucide-react';
import Button from '../common/Button';
import SuggestedPrompts from './SuggestedPrompts';
import aiService from '../../services/aiService';

export function PromptEditor({
  prompt,
  setPrompt,
  targetObject,
  setTargetObject,
  detectedObjects = [],
  onSubmit,
  isGenerating,
  selectedObject,
}) {
  // Update target object dynamically as user types or selects object
  useEffect(() => {
    if (selectedObject) {
      setTargetObject(selectedObject);
    } else {
      const detected = aiService.identifyTargetObject(prompt, detectedObjects);
      setTargetObject(detected);
    }
  }, [prompt, selectedObject, detectedObjects, setTargetObject]);

  const hasPrompt = prompt.trim().length >= 5;
  const isAmbiguous = hasPrompt && !targetObject;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (hasPrompt && onSubmit) {
      onSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Target Object Banner */}
      {targetObject ? (
        <div className="p-3 bg-brand-950/40 border border-brand-500/30 rounded-xl flex items-center justify-between animate-in fade-in duration-200">
          <div className="flex items-center gap-2 text-xs text-brand-300">
            <Target className="w-4 h-4 text-brand-400 flex-shrink-0" />
            <span>
              Target Identified: <strong className="text-white uppercase tracking-wider">{targetObject}</strong>
            </span>
          </div>
          <span className="text-[11px] text-brand-400/80 bg-brand-500/10 px-2 py-0.5 rounded-md border border-brand-500/20">
            Segment & Inpaint
          </span>
        </div>
      ) : isAmbiguous ? (
        <div className="p-3 bg-amber-950/30 border border-amber-600/40 rounded-xl flex items-start gap-2 text-xs text-amber-300 animate-in fade-in duration-200">
          <HelpCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <span>
            We couldn't identify which object you mean — try mentioning it by name (e.g. 'sofa', 'wall', 'table') or select one from the tags above.
          </span>
        </div>
      ) : null}

      {/* Textarea */}
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your design change... e.g. 'Change the sofa to dark blue leather' or 'Paint the walls light grey'"
          rows={3}
          disabled={isGenerating}
          className="w-full bg-slate-900/90 text-slate-100 border border-slate-700/80 rounded-2xl p-4 text-sm resize-none placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all leading-relaxed"
        />

        <div className="flex items-center justify-between mt-2">
          <span className="text-[11px] text-slate-400">
            {prompt.length}/1000 characters
          </span>

          <Button
            type="submit"
            disabled={!hasPrompt || isGenerating}
            isLoading={isGenerating}
            size="md"
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Generate AI Design
          </Button>
        </div>
      </div>

      {/* Suggested prompts */}
      <SuggestedPrompts
        selectedObject={selectedObject || targetObject}
        onSelectPrompt={(selectedText) => setPrompt(selectedText)}
      />
    </form>
  );
}

export default PromptEditor;
