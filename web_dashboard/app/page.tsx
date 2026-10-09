"use client";

import React, { useState, useMemo } from "react";
import { runSimulationJS, StepRecord } from "@/lib/satelliteSim";
import { TutorialModal } from "@/components/TutorialModal";
import { CentralOrbitDiagram } from "@/components/CentralOrbitDiagram";
import { StateBinsHud } from "@/components/StateBinsHud";
import { ScenarioPresets } from "@/components/ScenarioPresets";
import { TelemetryCharts } from "@/components/TelemetryCharts";
import { RuleInspector } from "@/components/RuleInspector";
import { InputControls } from "@/components/InputControls";
import {
  Rocket,
  Compass,
  Battery,
  Zap,
  Gauge,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  HelpCircle,
  Github,
  Sun,
  Moon,
  FastForward,
} from "lucide-react";

export default function DashboardPage() {
  // Input parameters state
  const [initialAlt, setInitialAlt] = useState(396.5);
  const [initialSocPct, setInitialSocPct] = useState(75);
  const [initialPropellantKg, setInitialPropellantKg] = useState(1.5);
  const [startTimeSec, setStartTimeSec] = useState(0);
  const [numSteps, setNumSteps] = useState(100);
  const [dragMultiplier, setDragMultiplier] = useState(1.0);

  // Playback & Scrubber state
  const [currentStepIndex, setCurrentStepIndex] = useState<number | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeedMs, setPlaybackSpeedMs] = useState(300);
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);

  // Run client-side simulation engine
  const trajectory = useMemo(() => {
    const customCdA = (2.2 * 0.04) * dragMultiplier;
    return runSimulationJS(
      initialAlt,
      initialSocPct,
      initialPropellantKg,
      numSteps,
      startTimeSec,
      { Cd_A: customCdA }
    );
  }, [initialAlt, initialSocPct, initialPropellantKg, numSteps, startTimeSec, dragMultiplier]);

  // Active step record
  const maxStep = trajectory.length;
  const activeStepIdx = Math.min(
    maxStep,
    Math.max(1, currentStepIndex ?? maxStep)
  );
  const currentRecord = trajectory[activeStepIdx - 1] ?? trajectory[0];
  const telem = currentRecord.telemetry;

  // Auto-play interval handling
  React.useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isPlaying) {
      timer = setInterval(() => {
        setCurrentStepIndex((prev) => {
          const current = prev ?? maxStep;
          if (current >= maxStep) {
            setIsPlaying(false);
            return maxStep;
          }
          return current + 1;
        });
      }, playbackSpeedMs);
    }
    return () => clearInterval(timer);
  }, [isPlaying, maxStep, playbackSpeedMs]);

  const handleApplyScenario = (
    alt: number,
    soc: number,
    fuel: number,
    startTime: number,
    dragMult: number = 1.0
  ) => {
    setInitialAlt(alt);
    setInitialSocPct(soc);
    setInitialPropellantKg(fuel);
    setStartTimeSec(startTime);
    setDragMultiplier(dragMult);
    setCurrentStepIndex(1);
    setIsPlaying(false);
  };

  // Metric deltas
  const altDelta = currentRecord.alt_km - 400.0;
  const socDelta = telem.delta_soc * 100.0;

  const modeNames: Record<number, string> = {
    0: "Safe Mode (2W)",
    1: "Standard (5W)",
    2: "Payload Mode (12W)",
  };

  const burnDur = currentRecord.burn_duration_s;
  let thrusterLabel = "Idle (0s)";
  if (burnDur === 2.0) thrusterLabel = "Short Pulse (2s)";
  if (burnDur === 10.0) thrusterLabel = "Long Burn (10s)";

  return (
    <div className="min-h-screen bg-space-900 text-gray-100 p-4 md:p-8 space-y-6">
      {/* 1. Header Bar */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-space-800 border border-space-border p-5 rounded-2xl shadow-xl">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 rounded-xl shadow-lg shadow-cyan-500/10">
            <Rocket className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-extrabold text-white tracking-tight">
                Autonomous Satellite Power & Propulsion Dashboard
              </h1>
              <span className="px-2.5 py-0.5 bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 text-[10px] font-mono font-bold rounded-full">
                4D MDP DISCRETIZATION
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Interactive Educational Simulator for Satellite Station-Keeping, Eclipse Cycles & Battery Management
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsTutorialOpen(true)}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 text-xs font-bold rounded-xl transition-all shadow-md"
          >
            <HelpCircle className="w-4 h-4" />
            <span>Mission Tutorial</span>
          </button>

          <a
            href="https://github.com/Vedhiga/satellite-power-propulsion-rl-building"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-space-700 hover:bg-space-600 border border-space-border text-gray-200 text-xs font-bold rounded-xl transition-all"
          >
            <Github className="w-4 h-4" />
            <span>GitHub Repository</span>
          </a>
        </div>
      </header>

      {/* Tutorial Onboarding Modal */}
      <TutorialModal
        isOpen={isTutorialOpen}
        onClose={() => setIsTutorialOpen(false)}
      />

      {/* 2. Interactive Scenario Sandbox */}
      <ScenarioPresets onApplyScenario={handleApplyScenario} />

      {/* 3. Explicit 4D Discrete State Space Classification HUD */}
      <StateBinsHud
        bins={currentRecord.bins}
        altitudeKm={currentRecord.alt_km}
        socPct={currentRecord.soc_pct}
        propellantKg={currentRecord.propellant_kg}
        inSun={telem.in_sun}
      />

      {/* 4. Educational Parameter Sliders */}
      <InputControls
        initialAlt={initialAlt}
        setInitialAlt={setInitialAlt}
        initialSocPct={initialSocPct}
        setInitialSocPct={setInitialSocPct}
        initialPropellantKg={initialPropellantKg}
        setInitialPropellantKg={setInitialPropellantKg}
        startTimeSec={startTimeSec}
        setStartTimeSec={setStartTimeSec}
        numSteps={numSteps}
        setNumSteps={setNumSteps}
        onOpenTutorial={() => setIsTutorialOpen(true)}
      />

      {/* 5. Top Metric Status Cards (Row of 5 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
        {/* Card 1: Altitude */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 uppercase tracking-wider font-semibold">
            <span>Orbital Altitude</span>
            <Compass className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-extrabold text-white font-mono">
              {currentRecord.alt_km.toFixed(2)} km
            </div>
            <div
              className={`text-xs font-medium mt-1 ${
                Math.abs(altDelta) <= 2.0 ? "text-emerald-400" : "text-amber-400"
              }`}
            >
              {altDelta >= 0 ? "+" : ""}
              {altDelta.toFixed(2)} km vs Target (400km)
            </div>
          </div>
        </div>

        {/* Card 2: Battery SOC */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 uppercase tracking-wider font-semibold">
            <span>Battery SOC</span>
            <Battery className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-extrabold text-white font-mono">
              {currentRecord.soc_pct.toFixed(1)}%
            </div>
            <div
              className={`text-xs font-medium mt-1 ${
                socDelta >= 0 ? "text-emerald-400" : "text-amber-400"
              }`}
            >
              {socDelta >= 0 ? "+" : ""}
              {socDelta.toFixed(2)}% / step
            </div>
          </div>
        </div>

        {/* Card 3: Propellant */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 uppercase tracking-wider font-semibold">
            <span>Propellant Reserve</span>
            <Gauge className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-extrabold text-white font-mono">
              {(currentRecord.propellant_kg * 1000).toFixed(1)} g
            </div>
            <div className="text-xs text-rose-400 font-medium mt-1">
              -{currentRecord.fuel_burned_g.toFixed(1)} g Total Expended
            </div>
          </div>
        </div>

        {/* Card 4: Electrical Power Mode */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 uppercase tracking-wider font-semibold">
            <span>Power Mode</span>
            <Zap className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-2">
            <div className="text-sm font-bold text-purple-300">
              {modeNames[currentRecord.power_mode]}
            </div>
            <div className="text-xs text-gray-400 font-medium mt-1">
              {telem.P_bus.toFixed(1)} W Bus Load
            </div>
          </div>
        </div>

        {/* Card 5: Thruster Status */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-gray-400 uppercase tracking-wider font-semibold">
            <span>Thruster State</span>
            <Rocket className="w-4 h-4 text-rose-400" />
          </div>
          <div className="mt-2">
            <div
              className={`text-sm font-bold ${
                burnDur > 0 ? "text-rose-400" : "text-gray-300"
              }`}
            >
              {thrusterLabel}
            </div>
            <div className="text-xs text-gray-400 font-medium mt-1">
              {burnDur > 0
                ? `-${telem.m_used_g.toFixed(2)} g Burned in Step`
                : "0.00 g Expended"}
            </div>
          </div>
        </div>
      </div>

      {/* 6. Main Visuals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: 2D Orbit Visualization */}
        <div className="lg:col-span-1">
          <CentralOrbitDiagram currentRecord={currentRecord} />
        </div>

        {/* Right Column: Telemetry Charts */}
        <div className="lg:col-span-2">
          <TelemetryCharts trajectory={trajectory} currentStep={activeStepIdx} />
        </div>
      </div>

      {/* 7. Playback Timeline Scrubber */}
      <div className="bg-space-800 border border-space-border rounded-2xl p-4 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setIsPlaying(false);
              setCurrentStepIndex(1);
            }}
            className="p-2 bg-space-700 hover:bg-space-600 rounded-lg transition-colors"
            title="Reset to Start (Step 1)"
          >
            <SkipBack className="w-4 h-4 text-gray-300" />
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center space-x-1.5 px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-space-900 text-xs font-bold rounded-lg transition-colors shadow-lg shadow-cyan-500/20"
          >
            {isPlaying ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Auto-Play</span>
              </>
            )}
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              setCurrentStepIndex(maxStep);
            }}
            className="p-2 bg-space-700 hover:bg-space-600 rounded-lg transition-colors"
            title="Jump to End"
          >
            <SkipForward className="w-4 h-4 text-gray-300" />
          </button>

          {/* Speed selector */}
          <button
            onClick={() => {
              setPlaybackSpeedMs((prev) => (prev === 300 ? 150 : prev === 150 ? 50 : 300));
            }}
            className="px-2.5 py-1.5 bg-space-700 hover:bg-space-600 rounded-lg text-[11px] font-mono font-bold text-gray-300 flex items-center space-x-1"
            title="Toggle Playback Speed"
          >
            <FastForward className="w-3.5 h-3.5" />
            <span>{playbackSpeedMs === 300 ? "1x" : playbackSpeedMs === 150 ? "2x" : "5x"}</span>
          </button>
        </div>

        <div className="flex-1 w-full flex items-center space-x-3">
          <span className="text-xs text-gray-400 font-mono whitespace-nowrap">
            Step {activeStepIdx} / {maxStep}
          </span>
          <input
            type="range"
            min="1"
            max={maxStep}
            value={activeStepIdx}
            onChange={(e) => {
              setIsPlaying(false);
              setCurrentStepIndex(parseInt(e.target.value));
            }}
            className="w-full h-2 bg-space-700 accent-cyan-400 rounded-lg cursor-pointer"
          />
          <span className="text-xs font-mono font-bold text-cyan-400 whitespace-nowrap">
            {currentRecord.time_min.toFixed(1)} mins
          </span>
        </div>
      </div>

      {/* 8. Explainable Operational Rule Inspector */}
      <RuleInspector currentRecord={currentRecord} />
    </div>
  );
}
