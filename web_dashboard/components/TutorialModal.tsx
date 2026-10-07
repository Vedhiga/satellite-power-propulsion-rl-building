"use client";

import React, { useState } from "react";
import {
  Rocket,
  Sun,
  Zap,
  Cpu,
  ChevronRight,
  ChevronLeft,
  X,
  CheckCircle2,
  ShieldAlert,
  Compass,
} from "lucide-react";

interface TutorialModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TutorialModal: React.FC<TutorialModalProps> = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);

  if (!isOpen) return null;

  const steps = [
    {
      title: "Step 1: The LEO Orbit & Atmospheric Drag",
      icon: <Compass className="w-8 h-8 text-cyan-400" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            Our satellite operates in a circular <strong className="text-cyan-400">Low Earth Orbit (LEO)</strong> at a target altitude of <strong className="text-white">400.0 km</strong>.
          </p>
          <div className="bg-space-900/80 border border-space-border p-4 rounded-xl space-y-2">
            <div className="flex items-center space-x-2 text-gold font-semibold text-xs uppercase tracking-wider">
              <ShieldAlert className="w-4 h-4" /> Thermospheric Drag Decay
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              At 400 km, tenuous atmospheric density (ρ₀ = 2.7 × 10⁻¹² kg/m³) continuously drains orbital energy, causing the satellite to decay by ~0.06 meters every minute. Periodic thruster boosts are required to maintain the altitude within the <strong className="text-emerald-400">398.0 km – 402.0 km deadband</strong>.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Step 2: Sun vs. Shadow (92.5-Min Eclipse Cycles)",
      icon: <Sun className="w-8 h-8 text-gold" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            The satellite completes one full orbit every <strong className="text-white">92.5 minutes</strong> (~92.5 control steps).
          </p>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-emerald-950/40 border border-emerald-800/50 p-3 rounded-lg">
              <div className="text-emerald-400 text-xs font-bold uppercase mb-1">Direct Sunlight (~65%)</div>
              <p className="text-xs text-gray-300">
                Triple-junction solar arrays generate up to <strong className="text-emerald-300">8.0 W</strong>, powering bus loads and recharging the 2.6 Ah Li-ion battery.
              </p>
            </div>
            <div className="bg-rose-950/40 border border-rose-800/50 p-3 rounded-lg">
              <div className="text-rose-400 text-xs font-bold uppercase mb-1">Earth Shadow (~35%)</div>
              <p className="text-xs text-gray-300">
                Solar generation drops to <strong className="text-rose-300">0.0 W</strong>. The battery exclusively powers all internal electronics and payloads.
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: "Step 3: Thruster Power Coupling (P_valve)",
      icon: <Zap className="w-8 h-8 text-purple-400" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            Firing the reaction control thruster does not only consume propellant—it also draws electrical power!
          </p>
          <div className="bg-space-900/80 border border-purple-900/40 p-4 rounded-xl space-y-2">
            <div className="flex items-center space-x-2 text-purple-400 font-semibold text-xs uppercase tracking-wider">
              <Zap className="w-4 h-4" /> 4.0 W Solenoid Valve Draw
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              While open, thruster solenoid valves draw <strong className="text-white">4.0 W</strong> of power. Firing a 10s burn while running Payload Mode (12 W) in shadow draws <strong className="text-purple-300">12.67 W total</strong>. Doing this when battery SOC is low risks a terminal <strong className="text-rose-400">brownout (&lt; 15% SOC)</strong>.
            </p>
          </div>
        </div>
      ),
    },
    {
      title: "Step 4: Deterministic Rule-Based Controller Logic",
      icon: <Cpu className="w-8 h-8 text-emerald-400" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            The autonomous rule-based controller prioritizes <strong className="text-emerald-400">energy safety over orbital station-keeping</strong>.
          </p>
          <ul className="space-y-2 text-xs text-gray-300">
            <li className="flex items-start space-x-2 bg-space-900/60 p-2.5 rounded-lg border border-space-border">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <span><strong className="text-emerald-300">Safety Interlock:</strong> If SOC ≤ 25%, thruster burns are strictly inhibited even if altitude is decaying.</span>
            </li>
            <li className="flex items-start space-x-2 bg-space-900/60 p-2.5 rounded-lg border border-space-border">
              <CheckCircle2 className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
              <span><strong className="text-cyan-300">Safe Recovery Mode:</strong> If SOC &lt; 30%, non-essential payloads are shed to 2.0 W Safe Mode.</span>
            </li>
            <li className="flex items-start space-x-2 bg-space-900/60 p-2.5 rounded-lg border border-space-border">
              <CheckCircle2 className="w-4 h-4 text-gold mt-0.5 shrink-0" />
              <span><strong className="text-gold">High Payload Mode:</strong> Activated (12.0 W) only when SOC ≥ 30% AND spacecraft is in direct sunlight.</span>
            </li>
          </ul>
        </div>
      ),
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-xl bg-space-800 border border-space-border rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-space-border bg-space-900/50">
          <div className="flex items-center space-x-3">
            {steps[currentStep].icon}
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                Mission Briefing Guide ({currentStep + 1} / {steps.length})
              </div>
              <h3 className="text-base font-bold text-white">
                {steps[currentStep].title}
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-space-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-6 min-h-[220px]">
          {steps[currentStep].content}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-space-border bg-space-900/50">
          {/* Step indicators */}
          <div className="flex items-center space-x-1.5">
            {steps.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentStep(i)}
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  i === currentStep ? "w-7 bg-cyan-400" : "bg-space-600 hover:bg-space-500"
                }`}
              />
            ))}
          </div>

          <div className="flex items-center space-x-3">
            {currentStep > 0 && (
              <button
                onClick={handlePrev}
                className="flex items-center space-x-1 px-3.5 py-2 text-xs font-semibold text-gray-300 hover:text-white bg-space-700 hover:bg-space-600 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Back</span>
              </button>
            )}
            <button
              onClick={handleNext}
              className="flex items-center space-x-1 px-4 py-2 text-xs font-bold text-space-900 bg-cyan-400 hover:bg-cyan-300 rounded-lg shadow-lg shadow-cyan-500/20 transition-all"
            >
              <span>{currentStep === steps.length - 1 ? "Start Mission" : "Next Step"}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
