import React from 'react';
import { HelpCircle, ChevronDown, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';

export function Help() {
  const steps = [
    { num: 1, title: 'Upload Your Photo', desc: 'Select or drag-and-drop a photo of your living room, office, or room into Design Studio.' },
    { num: 2, title: 'AI Space Analysis', desc: 'The system automatically scans the space and detects key furniture, walls, floors, and fixtures.' },
    { num: 3, title: 'Describe Your Change', desc: 'Enter a natural language prompt like "Change the sofa to blue leather" or click one of the suggested prompts.' },
    { num: 4, title: 'Automatic Object Targeting', desc: 'The AI identifies the target object from your prompt without requiring manual lassoing or drawing.' },
    { num: 5, title: 'Generative AI Customization', desc: 'The targeted object is inpainted with your requested textures, colors, and design styling.' },
    { num: 6, title: 'Review Before & After', desc: 'Drag the split comparison slider to compare your original room with the AI customized space.' },
    { num: 7, title: 'Approve Your Design', desc: 'Click "Approve Design" when satisfied with the updated interior appearance.' },
    { num: 8, title: 'Convert into 3D Space', desc: 'Click "MAKE IT 3D" to run depth estimation and 3D mesh reconstruction.' },
    { num: 9, title: 'Interactive 3D Inspection', desc: 'Rotate, pan, zoom, and inspect your 3D room model, or download the GLB file.' },
  ];

  const faqs = [
    {
      q: 'Do I need to manually select or mask the object before editing?',
      a: 'No! DesignVerse AI features natural language object identification. Simply describe what you want to change in words (e.g. "Change the sofa to dark blue leather"), and the AI automatically determines which object you are referring to.',
    },
    {
      q: 'What image formats and file sizes are supported?',
      a: 'You can upload JPG, JPEG, PNG, WEBP, BMP, and TIFF images up to 20 MB in size.',
    },
    {
      q: 'What 3D model formats are generated?',
      a: 'DesignVerse AI exports standard binary glTF (.GLB) 3D files. You can rotate and inspect them directly in our interactive web viewer, or download the file to open in Blender, Unity, or Unreal Engine.',
    },
    {
      q: 'Can I refine my edit or make additional changes to the same space?',
      a: 'Yes! After reviewing your edit, simply click "Edit Again" to modify your prompt, target another detected object, or re-run customization on the space.',
    },
  ];

  return (
    <div className="p-6 sm:p-8 max-w-5xl mx-auto w-full space-y-12">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-950/60 border border-brand-500/30 text-brand-300 text-xs font-semibold">
          <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
          <span>User Guide & FAQs</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          How to Use DesignVerse AI
        </h1>
        <p className="text-sm text-slate-400 leading-relaxed">
          Follow our 9-step workflow to effortlessly customize your room with natural language AI.
        </p>
      </div>

      {/* 9-Step Walkthrough */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <h2 className="text-lg font-bold text-white">The 9-Step Workflow</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {steps.map((step) => (
            <div
              key={step.num}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between"
            >
              <div>
                <div className="w-7 h-7 rounded-lg bg-brand-600/30 text-brand-300 font-bold text-xs flex items-center justify-center mb-3 border border-brand-500/30">
                  {step.num}
                </div>
                <h3 className="text-sm font-bold text-white mb-1">{step.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="pt-4 flex justify-center">
          <Link to="/studio">
            <Button size="md" rightIcon={<ArrowRight className="w-4 h-4" />}>
              Try It in Design Studio
            </Button>
          </Link>
        </div>
      </div>

      {/* FAQs Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 space-y-6">
        <h2 className="text-lg font-bold text-white">Frequently Asked Questions</h2>

        <div className="space-y-4">
          {faqs.map((faq, idx) => (
            <div key={idx} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                {faq.q}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed pl-6">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Help;
