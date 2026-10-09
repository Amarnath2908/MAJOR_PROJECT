import React from 'react';
import { Sparkles, Cpu, Layers, Target, Wand2, Box, ShieldCheck } from 'lucide-react';

export function About() {
  return (
    <div className="p-6 sm:p-8 max-w-5xl mx-auto w-full space-y-10">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-950/60 border border-brand-500/30 text-brand-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>About DesignVerse AI</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Intelligent Space Customization & 3D Spatial Reconstruction
        </h1>
        <p className="text-sm text-slate-400 leading-relaxed">
          DesignVerse AI is an AI-powered interior and exterior design platform developed as a
          B.Tech final year major project in Computer Science & Artificial Intelligence.
        </p>
      </div>

      {/* Target Technologies (Honest Architecture Disclosure) */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Target Deep Learning Architecture</h3>
            <p className="text-xs text-slate-400">
              Modular decoupled AI interfaces ready for zero-redesign model integration
            </p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-brand-950/20 border border-brand-500/20 text-xs text-slate-300 leading-relaxed">
          <strong>Phase Status Note:</strong> In accordance with clean software engineering practices,
          the current system infrastructure is built with verified mock interfaces. Real deep learning
          weights for Grounding DINO, SAM, Stable Diffusion, and InstantMesh can be dropped directly into
          the backend <code className="text-brand-300 bg-slate-900 px-1 py-0.5 rounded font-mono">ai/</code>{' '}
          folder without modifying any frontend component, database table, or API route.
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              name: 'Grounding DINO',
              role: 'Open-Vocabulary Object Detection',
              desc: 'Enables prompt-conditioned bounding box detection of arbitrary space items (furniture, walls, decor) without pre-training on fixed categories.',
              icon: Target,
            },
            {
              name: 'Segment Anything (SAM)',
              role: 'Pixel-Level Object Segmentation',
              desc: 'Extracts exact segmentation masks for the detected target region to isolate the editing area perfectly without bleeding.',
              icon: Layers,
            },
            {
              name: 'Stable Diffusion / FLUX',
              role: 'Targeted Inpainting & Generative Editing',
              desc: 'Synthesizes photo-realistic texture, material, color, and geometric changes strictly within the segmentation mask.',
              icon: Wand2,
            },
            {
              name: 'InstantMesh / Depth Anything',
              role: '3D Spatial Geometry Reconstruction',
              desc: 'Estimates metric depth and predicts multi-view spatial perspectives to reconstruct full .GLB 3D meshes for interactive inspection.',
              icon: Box,
            },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.name} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-brand-400" />
                  <h4 className="text-sm font-bold text-white">{item.name}</h4>
                </div>
                <span className="text-[11px] text-brand-300 font-medium block">{item.role}</span>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default About;
