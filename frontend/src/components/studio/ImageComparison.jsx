import React, { useState } from 'react';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { Columns, SplitSquareVertical, ZoomIn } from 'lucide-react';
import { resolveAssetUrl } from '../../services/api';

export function ImageComparison({
  originalImage,
  editedImage,
  prompt,
  targetObject,
}) {
  const [viewMode, setViewMode] = useState('slider'); // 'slider' | 'sideBySide'
  const originalUrl = resolveAssetUrl(originalImage);
  const editedUrl = resolveAssetUrl(editedImage);

  return (
    <div className="flex flex-col gap-3 w-full">
      {/* Top Header & View Toggle */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Space Comparison
          </span>
          {targetObject && (
            <span className="text-[11px] bg-brand-500/20 text-brand-300 border border-brand-500/30 px-2 py-0.5 rounded-full font-medium">
              Target: {targetObject}
            </span>
          )}
        </div>

        {/* View Mode Toggle (Accessibility & Preference) */}
        <div className="flex items-center bg-slate-900 border border-slate-700/80 rounded-xl p-0.5">
          <button
            type="button"
            onClick={() => setViewMode('slider')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'slider'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Draggable Split Slider"
          >
            <SplitSquareVertical className="w-3.5 h-3.5" />
            <span>Slider</span>
          </button>

          <button
            type="button"
            onClick={() => setViewMode('sideBySide')}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'sideBySide'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
            title="Side by Side Grid View"
          >
            <Columns className="w-3.5 h-3.5" />
            <span>Side-by-Side</span>
          </button>
        </div>
      </div>

      {/* Comparison Display */}
      <div className="relative w-full rounded-2xl overflow-hidden border border-slate-700/80 bg-slate-950 shadow-2xl">
        {viewMode === 'slider' ? (
          <div className="relative w-full aspect-video">
            <ReactCompareSlider
              itemOne={
                <ReactCompareSliderImage
                  src={originalUrl}
                  alt="Original room"
                  className="w-full h-full object-cover"
                />
              }
              itemTwo={
                <ReactCompareSliderImage
                  src={editedUrl}
                  alt="AI redesigned room"
                  className="w-full h-full object-cover"
                />
              }
              className="w-full h-full"
            />
            {/* Overlay Labels */}
            <div className="absolute top-3 left-3 bg-dark-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-300 border border-slate-700/60 pointer-events-none">
              Original
            </div>
            <div className="absolute top-3 right-3 bg-brand-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[11px] font-semibold text-brand-300 border border-brand-500/40 pointer-events-none">
              AI Redesign
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-slate-800">
            {/* Original */}
            <div className="relative aspect-video bg-slate-950 group">
              <img
                src={originalUrl}
                alt="Original space"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3 bg-dark-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-300 border border-slate-700/60">
                Original Space
              </div>
            </div>

            {/* Edited */}
            <div className="relative aspect-video bg-slate-950 group">
              <img
                src={editedUrl}
                alt="AI edited space"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3 bg-brand-900/80 backdrop-blur-md px-2.5 py-1 rounded-lg text-[11px] font-semibold text-brand-300 border border-brand-500/40">
                AI Customized Space
              </div>
            </div>
          </div>
        )}

        {/* Prompt Caption Bar */}
        {prompt && (
          <div className="p-3 bg-dark-900/90 border-t border-slate-800/80 text-xs text-slate-300 flex items-center justify-between">
            <p className="truncate mr-4">
              <span className="text-slate-400">Prompt:</span>{' '}
              <span className="text-white italic">"{prompt}"</span>
            </p>
            <a
              href={editedUrl}
              target="_blank"
              rel="noreferrer"
              className="text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium text-[11px] flex-shrink-0"
            >
              <ZoomIn className="w-3.5 h-3.5" />
              <span>Full View</span>
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default ImageComparison;
