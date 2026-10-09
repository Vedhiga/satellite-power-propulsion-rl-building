"use client";

import React from "react";
import { Sliders, Compass, Battery, Gauge, Clock, HelpCircle } from "lucide-react";

interface InputControlsProps {
  initialAlt: number;
  setInitialAlt: (val: number) => void;
  initialSocPct: number;
  setInitialSocPct: (val: number) => void;
  initialPropellantKg: number;
  setInitialPropellantKg: (val: number) => void;
  startTimeSec: number;
  setStartTimeSec: (val: number) => void;
  numSteps: number;
  setNumSteps: (val: number) => void;
  onOpenTutorial: () => void;
}

export const InputControls: React.FC<InputControlsProps> = ({
  initialAlt,
  setInitialAlt,
  initialSocPct,
  setInitialSocPct,
  initialPropellantKg,
  setInitialPropellantKg,
  startTimeSec,
  setStartTimeSec,
  numSteps,
  setNumSteps,
  onOpenTutorial,
}) => {
  const startTimeMin = startTimeSec / 60.0;
  const inShadow = startTimeMin < 32.375; // 35% of 92.5 min = 32.375 min

  return (
    <div className="bg-space-800 border border-space-border p-5 rounded-2xl shadow-xl space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-space-border pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 rounded-xl">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              Educational Parameter Sliders & Initial Conditions
            </h3>
            <p className="text-xs text-gray-400">
              Adjust initial altitude, battery SOC, propellant reserve, and orbit clock position
            </p>
          </div>
        </div>

        <button
          onClick={onOpenTutorial}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-space-700 hover:bg-space-600 border border-space-border text-cyan-300 text-xs font-bold rounded-xl transition-all self-start sm:self-auto"
        >
          <HelpCircle className="w-4 h-4" />
          <span>Interactive Guide</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-5 text-xs">
        {/* Slider 1: Altitude */}
        <div className="space-y-2 bg-space-900 border border-space-border p-3.5 rounded-xl flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-gray-300 font-semibold">
              <Compass className="w-4 h-4 text-cyan-400" />
              <span>Initial Altitude</span>
            </div>
            <span className="font-mono font-bold text-cyan-400 text-sm">
              {initialAlt.toFixed(1)} km
            </span>
          </div>

          <input
            type="range"
            min="385.0"
            max="415.0"
            step="0.5"
            value={initialAlt}
            onChange={(e) => setInitialAlt(parseFloat(e.target.value))}
            className="w-full h-2 bg-space-700 accent-cyan-400 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-gray-400 font-mono">
            <span>385km</span>
            <span className="text-rose-400 font-bold">390</span>
            <span className="text-emerald-400 font-bold">400</span>
            <span className="text-purple-400 font-bold">410</span>
            <span>415km</span>
          </div>
        </div>

        {/* Slider 2: Battery SOC */}
        <div className="space-y-2 bg-space-900 border border-space-border p-3.5 rounded-xl flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-gray-300 font-semibold">
              <Battery className="w-4 h-4 text-emerald-400" />
              <span>Initial Battery</span>
            </div>
            <span
              className={`font-mono font-bold text-sm ${
                initialSocPct < 20
                  ? "text-rose-400"
                  : initialSocPct < 40
                  ? "text-amber-400"
                  : "text-emerald-400"
              }`}
            >
              {initialSocPct.toFixed(0)}%
            </span>
          </div>

          <input
            type="range"
            min="15"
            max="100"
            step="1"
            value={initialSocPct}
            onChange={(e) => setInitialSocPct(parseInt(e.target.value))}
            className="w-full h-2 bg-space-700 accent-emerald-400 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-gray-400 font-mono">
            <span className="text-rose-400 font-bold">15% Crit</span>
            <span className="text-amber-400 font-bold">40% Low</span>
            <span className="text-emerald-400 font-bold">80% Full</span>
          </div>
        </div>

        {/* Slider 3: Propellant Reserve */}
        <div className="space-y-2 bg-space-900 border border-space-border p-3.5 rounded-xl flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-gray-300 font-semibold">
              <Gauge className="w-4 h-4 text-amber-400" />
              <span>Propellant Mass</span>
            </div>
            <span className="font-mono font-bold text-amber-400 text-sm">
              {(initialPropellantKg * 1000).toFixed(0)} g
            </span>
          </div>

          <input
            type="range"
            min="0.00"
            max="1.50"
            step="0.05"
            value={initialPropellantKg}
            onChange={(e) => setInitialPropellantKg(parseFloat(e.target.value))}
            className="w-full h-2 bg-space-700 accent-amber-400 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-gray-400 font-mono">
            <span className="text-rose-400 font-bold">0.0 kg (Dry)</span>
            <span>0.75 kg</span>
            <span className="text-emerald-400 font-bold">1.50 kg</span>
          </div>
        </div>

        {/* Slider 4: Orbit Position / Clock */}
        <div className="space-y-2 bg-space-900 border border-space-border p-3.5 rounded-xl flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-gray-300 font-semibold">
              <Clock className="w-4 h-4 text-yellow-400" />
              <span>Orbit Clock Position</span>
            </div>
            <span className={`font-mono font-bold text-xs ${inShadow ? "text-indigo-400" : "text-yellow-400"}`}>
              {startTimeMin.toFixed(1)}m ({inShadow ? "Shadow" : "Sun"})
            </span>
          </div>

          <input
            type="range"
            min="0"
            max="5550"
            step="60"
            value={startTimeSec}
            onChange={(e) => setStartTimeSec(parseInt(e.target.value))}
            className="w-full h-2 bg-space-700 accent-yellow-400 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-gray-400 font-mono">
            <span className="text-indigo-400 font-bold">0m (Shadow)</span>
            <span className="text-indigo-400 font-bold">32m</span>
            <span className="text-yellow-400 font-bold">92.5m (Sun)</span>
          </div>
        </div>

        {/* Slider 5: Duration */}
        <div className="space-y-2 bg-space-900 border border-space-border p-3.5 rounded-xl flex flex-col justify-between">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-1.5 text-gray-300 font-semibold">
              <Sliders className="w-4 h-4 text-purple-400" />
              <span>Sim Duration</span>
            </div>
            <span className="font-mono font-bold text-purple-400 text-sm">
              {numSteps} steps
            </span>
          </div>

          <input
            type="range"
            min="30"
            max="200"
            step="10"
            value={numSteps}
            onChange={(e) => setNumSteps(parseInt(e.target.value))}
            className="w-full h-2 bg-space-700 accent-purple-400 rounded-lg cursor-pointer"
          />

          <div className="flex justify-between text-[10px] text-gray-400 font-mono">
            <span>30 steps (30m)</span>
            <span className="text-purple-400 font-bold">100 (~1.6 orbits)</span>
            <span>200 steps</span>
          </div>
        </div>
      </div>
    </div>
  );
};
