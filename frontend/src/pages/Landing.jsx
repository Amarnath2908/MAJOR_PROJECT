import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Wand2,
  Box,
  Layers,
  ArrowRight,
  Target,
  Cpu,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import Button from '../components/common/Button';
import useAuthStore from '../store/authStore';

export function Landing() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="flex flex-col w-full">
      {/* ── 1. Hero Section ────────────────────────────────────────────── */}
      <section className="relative pt-20 pb-28 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-950/60 border border-brand-500/30 text-brand-300 text-xs font-semibold mb-8 shadow-glow/30">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>AI-Powered Space Customization & 3D Reconstruction</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight">
            Transform Your Space with{' '}
            <span className="bg-gradient-to-r from-brand-400 via-purple-300 to-cyan-400 bg-clip-text text-transparent">
              Natural Language AI
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-xl text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
            Upload an image of your living room, office, or exterior. Describe what you want to change,
            and watch AI identify the object, customize it, and turn the space into an interactive 3D model.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link to={isAuthenticated ? '/studio' : '/auth?tab=register'}>
              <Button size="xl" rightIcon={<ArrowRight className="w-5 h-5" />}>
                Start Designing Now
              </Button>
            </Link>

            <Link to="/help">
              <Button variant="secondary" size="xl" leftIcon={<HelpCircle className="w-5 h-5" />}>
                How It Works
              </Button>
            </Link>
          </div>

          {/* Interactive Preview Mock */}
          <div className="mt-16 max-w-4xl mx-auto rounded-3xl p-2 bg-gradient-to-b from-brand-500/30 via-slate-800/40 to-transparent border border-brand-500/20 shadow-2xl">
            <div className="rounded-2xl overflow-hidden bg-slate-950 border border-slate-800 relative group aspect-video">
              <img
                src="/src/assets/hero_room.jpg"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80';
                }}
                alt="Living room AI transform preview"
                className="w-full h-full object-cover"
              />

              <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-dark-900/30 to-transparent flex flex-col justify-end p-6 sm:p-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-brand-600/80 backdrop-blur-md flex items-center justify-center text-white border border-brand-400/40">
                      <Target className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs text-brand-300 font-semibold uppercase tracking-wider">
                        Natural Language Prompt
                      </p>
                      <p className="text-sm font-medium text-white italic">
                        "Change the sofa to dark blue leather and add warm ambient ceiling lighting"
                      </p>
                    </div>
                  </div>

                  <Link to="/studio">
                    <Button variant="cyan" size="sm">
                      Try This Space
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. The 4-Step Pipeline ──────────────────────────────────────── */}
      <section className="py-20 border-t border-slate-800/80 bg-dark-850/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-brand-400 uppercase tracking-widest mb-2">
              How It Works
            </h2>
            <h3 className="text-3xl font-extrabold text-white">
              Zero Manual Masking. Just Describe Your Vision.
            </h3>
            <p className="mt-3 text-sm text-slate-400">
              Unlike traditional 3D software or complex editors, DesignVerse AI handles detection,
              segmentation, editing, and 3D reconstruction automatically.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              {
                step: '01',
                title: 'Upload Room Photo',
                desc: 'Upload a standard 2D photo of your room, living room, office, or furniture.',
                icon: Layers,
              },
              {
                step: '02',
                title: 'AI Space Analysis',
                desc: 'Open-vocabulary AI detects structural elements: walls, sofas, tables, windows, and floors.',
                icon: Target,
              },
              {
                step: '03',
                title: 'Text Prompt Editing',
                desc: 'Type your change naturally. AI automatically locates and customizes the targeted object.',
                icon: Wand2,
              },
              {
                step: '04',
                title: 'Generate 3D Model',
                desc: 'Depth estimation and mesh reconstruction convert your approved design into an interactive 3D GLB.',
                icon: Box,
              },
            ].map((card) => {
              const Icon = card.icon;
              return (
                <div
                  key={card.step}
                  className="glass-panel p-6 rounded-2xl relative border border-slate-800 hover:border-brand-500/40 transition-all duration-200"
                >
                  <span className="text-3xl font-black text-slate-800 absolute top-4 right-4">
                    {card.step}
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-brand-600/20 text-brand-400 flex items-center justify-center mb-4 border border-brand-500/30">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-base font-bold text-white mb-2">{card.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{card.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── 3. Features & Technology ───────────────────────────────────── */}
      <section className="py-20 border-t border-slate-800/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">
                Under the Hood
              </span>
              <h3 className="text-3xl font-extrabold text-white mt-2 leading-tight">
                Engineered with Modern Deep Learning & Clean Architecture
              </h3>
              <p className="mt-4 text-sm text-slate-400 leading-relaxed">
                DesignVerse AI is designed with modular placeholder interfaces that decouple the
                FastAPI web service from machine learning models. Future integration swaps mock
                endpoints with state-of-the-art vision models without changing the frontend or database.
              </p>

              <div className="mt-6 space-y-3">
                {[
                  { name: 'Grounding DINO', role: 'Open-vocabulary zero-shot object detection' },
                  { name: 'Segment Anything Model (SAM)', role: 'Pixel-accurate mask generation' },
                  { name: 'Stable Diffusion / FLUX', role: 'Context-aware inpainting & text guidance' },
                  { name: 'Depth Anything V2', role: 'Monocular metric depth estimation' },
                  { name: 'InstantMesh / 3D Diffusion', role: 'Fast feedforward single-image 3D generation' },
                ].map((tech) => (
                  <div key={tech.name} className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <CheckCircle2 className="w-4 h-4 text-brand-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="text-xs font-bold text-white block">{tech.name}</span>
                      <span className="text-[11px] text-slate-400">{tech.role}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                <Cpu className="w-4 h-4 text-brand-400" />
                <span>Decoupled Clean Architecture</span>
              </div>

              <div className="p-4 rounded-2xl bg-dark-900 border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
                <p className="text-brand-400">// Client Request</p>
                <p className="text-slate-400">React Client &rarr; Axios &rarr; Bearer JWT Auth</p>
                <p className="text-cyan-400 mt-3">// API Gateway Layer</p>
                <p className="text-slate-400">FastAPI &rarr; Pydantic v2 Validation &rarr; Clean Service</p>
                <p className="text-purple-400 mt-3">// Swappable AI Engine</p>
                <p className="text-slate-400">AnalysisService &rarr; GroundingDINO Interface (Mock/Real)</p>
                <p className="text-slate-400">EditorService &rarr; SAM + SD Inpainting Interface</p>
                <p className="text-slate-400">ViewerService &rarr; InstantMesh 3D GLB Pipeline</p>
              </div>

              <p className="text-[11px] text-slate-500 italic text-center">
                Built as a B.Tech Final Year Major Project &bull; Fully Functional End-to-End
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4. Call to Action Banner ───────────────────────────────────── */}
      <section className="py-20 border-t border-slate-800/80 bg-gradient-to-b from-brand-950/20 to-dark-900">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h3 className="text-3xl sm:text-4xl font-extrabold text-white">
            Ready to Redesign Your Living Space?
          </h3>
          <p className="mt-3 text-sm text-slate-400 max-w-lg mx-auto">
            Experience natural language space customization and instant 3D model generation today.
          </p>

          <div className="mt-8 flex justify-center">
            <Link to={isAuthenticated ? '/studio' : '/auth?tab=register'}>
              <Button size="lg" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Launch Design Studio
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── 5. Footer ──────────────────────────────────────────────────── */}
      <footer className="py-8 border-t border-slate-800/80 text-center text-xs text-slate-500">
        <p>&copy; {new Date().getFullYear()} DesignVerse AI &bull; B.Tech Final Year AI Project &bull; All Rights Reserved.</p>
      </footer>
    </div>
  );
}

export default Landing;
