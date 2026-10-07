"use client";

import React from "react";
import { Sliders, RotateCcw, Info, Sparkles, HelpCircle } from "lucide-react";

interface InputControlsProps {
  initialAlt: number;
  setInitialAlt: (val: number) => void;
  initialSocPct: number;
  setInitialSocPct: (val: number) => void;
  initialPropellantKg: number;
  setInitialPropellantKg: (val: number) => void;
  numSteps: number;
  setNumSteps: (val: number) => void;
  onOpenTutorial: () => void;
  onApplyPreset: (alt: number, soc: number, fuel: number) => void;
}

export const InputControls: React.FC<InputControlsProps> = ({
  initialAlt,
  setInitialAlt,
  initialSocPct,
  setInitialSocPct,
  initialPropellantKg,
  setInitialPropellantKg,
  numSteps,
  setNumSteps,
  onOpenTutorial,
  onApplyPreset,
}) => {
  return (
    <div className="bg-space-800 border border-space-border rounded-2xl p-5 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-space-border pb-3">
        <div className="flex items-center space-x-2">
          <Sliders className="w-5 h-5 text-cyan-400" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">
            Mission Controls & Presets
          </h3>
        </div>
        <button
          onClick={onOpenTutorial}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-300 text-xs font-bold rounded-lg transition-colors shadow-sm"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Tutorial</span>
        </button>
      </div>

      {/* Quick-Load Presets */}
      <div>
        <div className="flex items-center space-x-1.5 text-xs font-bold text-gray-300 mb-2 uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5 text-gold" />
          <span>Quick-Load Mission Presets</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <button
            onClick={() => onApplyPreset(396.5, 75, 1.5)}
            className="flex flex-col text-left p-2.5 bg-space-900/80 hover:bg-space-700/80 border border-space-border hover:border-emerald-500/50 rounded-xl transition-all group"
          >
            <span className="text-xs font-bold text-emerald-400 group-hover:text-emerald-300">
              Nominal Orbit Baseline
            </span>
            <span className="text-[11px] text-gray-400">396.5 km | 75% SOC | 1.5 kg</span>
          </button>

          <button
            onClick={() => onApplyPreset(394.0, 24, 1.5)}
            className="flex flex-col text-left p-2.5 bg-space-900/80 hover:bg-space-700/80 border border-space-border hover:border-amber-500/50 rounded-xl transition-all group"
          >
            <span className="text-xs font-bold text-amber-400 group-hover:text-amber-300">
              Eclipse Stress / Low Battery
            </span>
            <span className="text-[11px] text-gray-400">394.0 km | 24% SOC | 1.5 kg</span>
          </button>

          <button
            onClick={() => onApplyPreset(395.0, 80, 0.005)}
            className="flex flex-col text-left p-2.5 bg-space-900/80 hover:bg-space-700/80 border border-space-border hover:border-rose-500/50 rounded-xl transition-all group"
          >
            <span className="text-xs font-bold text-rose-400 group-hover:text-rose-300">
              Fuel Starvation Edge Case
            </span>
            <span className="text-[11px] text-gray-400">395.0 km | 80% SOC | 0.005 kg</span>
          </button>
        </div>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* 1. Initial Altitude */}
        <div className="bg-space-900/50 border border-space-border/60 p-3.5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-gray-200">Initial Altitude (km)</span>
            <span className="font-mono font-bold text-cyan-400">{initialAlt.toFixed(1)} km</span>
          </div>
          <input
            type="range"
            min="390.0"
            max="410.0"
            step="0.1"
            value={initialAlt}
            onChange={(e) => setInitialAlt(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-space-700 accent-cyan-400 rounded-lg cursor-pointer"
          />
          <p className="text-[11px] text-gray-400 leading-snug flex items-start space-x-1">
            <Info className="w-3 h-3 text-gray-500 mt-0.5 shrink-0" />
            <span>Target is 400.0 km. Starting &lt;398 km triggers burns; &gt;402 km allows natural drag.</span>
          </p>
        </div>

        {/* 2. Initial Battery SOC */}
        <div className="bg-space-900/50 border border-space-border/60 p-3.5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-gray-200">Initial Battery SOC (%)</span>
            <span className="font-mono font-bold text-emerald-400">{initialSocPct}%</span>
          </div>
          <input
            type="range"
            min="20"
            max="100"
            step="1"
            value={initialSocPct}
            onChange={(e) => setInitialSocPct(parseInt(e.target.value))}
            className="w-full h-1.5 bg-space-700 accent-emerald-400 rounded-lg cursor-pointer"
          />
          <p className="text-[11px] text-gray-400 leading-snug flex items-start space-x-1">
            <Info className="w-3 h-3 text-gray-500 mt-0.5 shrink-0" />
            <span>&lt;30% enforces Safe Mode (2W). &le;25% inhibits thruster burns to avoid brownouts.</span>
          </p>
        </div>

        {/* 3. Initial Usable Propellant */}
        <div className="bg-space-900/50 border border-space-border/60 p-3.5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-gray-200">Initial Usable Propellant (kg)</span>
            <span className="font-mono font-bold text-amber-400">{initialPropellantKg.toFixed(3)} kg</span>
          </div>
          <input
            type="range"
            min="0.005"
            max="1.50"
            step="0.005"
            value={initialPropellantKg}
            onChange={(e) => setInitialPropellantKg(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-space-700 accent-amber-400 rounded-lg cursor-pointer"
          />
          <p className="text-[11px] text-gray-400 leading-snug flex items-start space-x-1">
            <Info className="w-3 h-3 text-gray-500 mt-0.5 shrink-0" />
            <span>Total fuel mass. Each 10s burn consumes 4.5 g (0.0045 kg). Low values test dry-tank lockout.</span>
          </p>
        </div>

        {/* 4. Simulation Duration */}
        <div className="bg-space-900/50 border border-space-border/60 p-3.5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-gray-200">Simulation Horizon (Steps / Min)</span>
            <span className="font-mono font-bold text-purple-400">{numSteps} steps</span>
          </div>
          <input
            type="range"
            min="30"
            max="200"
            step="5"
            value={numSteps}
            onChange={(e) => setNumSteps(parseInt(e.target.value))}
            className="w-full h-1.5 bg-space-700 accent-purple-400 rounded-lg cursor-pointer"
          />
          <p className="text-[11px] text-gray-400 leading-snug flex items-start space-x-1">
            <Info className="w-3 h-3 text-gray-500 mt-0.5 shrink-0" />
            <span>1 step = 60 seconds. 92.5 steps equals one full LEO orbit (~1.6 orbits for 100 steps).</span>
          </p>
        </div>
      </div>
    </div>
  );
};
