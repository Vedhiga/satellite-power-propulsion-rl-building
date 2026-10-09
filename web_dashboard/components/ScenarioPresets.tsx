"use client";

import React, { useState } from "react";
import { Zap, AlertTriangle, ShieldAlert, Sun, Battery, Compass, Sparkles } from "lucide-react";

interface ScenarioPresetsProps {
  onApplyScenario: (
    alt: number,
    soc: number,
    fuel: number,
    startTimeSec: number,
    dragMultiplier?: number,
    description?: string
  ) => void;
}

export const ScenarioPresets: React.FC<ScenarioPresetsProps> = ({ onApplyScenario }) => {
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [observationCallout, setObservationCallout] = useState<string>(
    "Select a scenario trigger below to inject critical boundary conditions into the live TypeScript engine."
  );

  const handleScenarioA = () => {
    setActivePreset("A");
    const desc =
      "SCENARIO A: Satellite dropped to 394.0 km in deep Earth shadow with only 22% battery. Observe cross-coupling: firing thruster valves (+4W load) risks immediate brownout (<15% SOC), so the controller inhibits burns until reaching daylight.";
    setObservationCallout(desc);
    onApplyScenario(394.0, 22, 1.5, 600, 1.0, desc);
  };

  const handleScenarioB = () => {
    setActivePreset("B");
    const desc =
      "SCENARIO B: Solar Maximum storm expands upper thermosphere, increasing atmospheric drag by 300% (3x Cd*A) while in eclipse. Observe accelerated altitude decay and test whether emergency orbit recovery burns trigger in darkness.";
    setObservationCallout(desc);
    onApplyScenario(393.5, 65, 1.5, 900, 3.0, desc);
  };

  const handleScenarioC = () => {
    setActivePreset("C");
    const desc =
      "SCENARIO C: Propellant reserve exhausted to 0.002 kg with altitude low (393.0 km). Observe physical thruster lock-out: burn duration is clamped to 0.0 s without negative fuel numbers or physics crashes.";
    setObservationCallout(desc);
    onApplyScenario(393.0, 75, 0.002, 0, 1.0, desc);
  };

  const handleScenarioD = () => {
    setActivePreset("D");
    const desc =
      "SCENARIO D: Satellite placed in direct sunlight (2700s orbit clock) at 397.0 km with healthy 85% battery. Observe simultaneous +8.0 W solar battery recharge, High-Duty Payload enablement, and safe orbital station-keeping boost.";
    setObservationCallout(desc);
    onApplyScenario(397.0, 85, 1.5, 2700, 1.0, desc);
  };

  return (
    <div className="bg-space-800 border border-space-border p-5 rounded-2xl shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-950/80 border border-amber-500/40 text-amber-400 rounded-xl">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              Interactive Scenario Sandbox ("What Happens If...?")
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              One-click boundary condition injections to observe physical cross-subsystem interlocks
            </p>
          </div>
        </div>

        <span className="px-3 py-1 bg-space-900 border border-space-border text-gray-400 text-xs font-mono rounded-full font-semibold">
          4 PRESET STRESS PROFILES
        </span>
      </div>

      {/* Preset Buttons Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Button A */}
        <button
          onClick={handleScenarioA}
          className={`p-3.5 border rounded-xl text-left transition-all flex flex-col justify-between space-y-2 group ${
            activePreset === "A"
              ? "bg-rose-950/90 border-rose-500 text-rose-200 ring-2 ring-rose-500/30 shadow-lg shadow-rose-500/10"
              : "bg-space-900 hover:bg-space-700/80 border-space-border text-gray-300"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-rose-400 group-hover:text-rose-300">
              SCENARIO A
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-xs font-bold text-white">Altitude Drop in Deep Shadow</div>
          <div className="text-[11px] text-gray-400 font-mono">
            h=394km | SOC=22% | Shadow
          </div>
        </button>

        {/* Button B */}
        <button
          onClick={handleScenarioB}
          className={`p-3.5 border rounded-xl text-left transition-all flex flex-col justify-between space-y-2 group ${
            activePreset === "B"
              ? "bg-amber-950/90 border-amber-500 text-amber-200 ring-2 ring-amber-500/30 shadow-lg shadow-amber-500/10"
              : "bg-space-900 hover:bg-space-700/80 border-space-border text-gray-300"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-amber-400 group-hover:text-amber-300">
              SCENARIO B
            </span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xs font-bold text-white">Solar Storm Drag Surge</div>
          <div className="text-[11px] text-gray-400 font-mono">
            3x Drag (3*CdA) | Shadow
          </div>
        </button>

        {/* Button C */}
        <button
          onClick={handleScenarioC}
          className={`p-3.5 border rounded-xl text-left transition-all flex flex-col justify-between space-y-2 group ${
            activePreset === "C"
              ? "bg-purple-950/90 border-purple-500 text-purple-200 ring-2 ring-purple-500/30 shadow-lg shadow-purple-500/10"
              : "bg-space-900 hover:bg-space-700/80 border-space-border text-gray-300"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-purple-400 group-hover:text-purple-300">
              SCENARIO C
            </span>
            <Battery className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-xs font-bold text-white">Fuel Starvation Lockout</div>
          <div className="text-[11px] text-gray-400 font-mono">
            m_p=0.002kg | h=393km
          </div>
        </button>

        {/* Button D */}
        <button
          onClick={handleScenarioD}
          className={`p-3.5 border rounded-xl text-left transition-all flex flex-col justify-between space-y-2 group ${
            activePreset === "D"
              ? "bg-emerald-950/90 border-emerald-500 text-emerald-200 ring-2 ring-emerald-500/30 shadow-lg shadow-emerald-500/10"
              : "bg-space-900 hover:bg-space-700/80 border-space-border text-gray-300"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-emerald-400 group-hover:text-emerald-300">
              SCENARIO D
            </span>
            <Sun className="w-4 h-4 text-yellow-400" />
          </div>
          <div className="text-xs font-bold text-white">Daylight Boost & Full Charge</div>
          <div className="text-[11px] text-gray-400 font-mono">
            h=397km | SOC=85% | Sun
          </div>
        </button>
      </div>

      {/* Observation Callout Banner */}
      <div className="bg-space-900 border border-space-border p-4 rounded-xl flex items-start space-x-3 text-xs">
        <Sparkles className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-amber-300 uppercase tracking-wider text-[11px]">
            Educational Observation Focus
          </div>
          <div className="text-gray-300 leading-relaxed font-sans">
            {observationCallout}
          </div>
        </div>
      </div>
    </div>
  );
};
