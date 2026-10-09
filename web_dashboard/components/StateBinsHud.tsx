"use client";

import React from "react";
import { DiscreteStateBreakdown } from "@/lib/satelliteSim";
import { Compass, Battery, Flame, Sun, Layers } from "lucide-react";

interface StateBinsHudProps {
  bins: DiscreteStateBreakdown;
  altitudeKm: number;
  socPct: number;
  propellantKg: number;
  inSun: number;
}

export const StateBinsHud: React.FC<StateBinsHudProps> = ({
  bins,
  altitudeKm,
  socPct,
  propellantKg,
  inSun,
}) => {
  const getBadgeStyle = (statusType: string) => {
    switch (statusType) {
      case "danger":
        return "bg-rose-950/80 border-rose-500/50 text-rose-300 ring-rose-500/20";
      case "warning":
        return "bg-amber-950/80 border-amber-500/50 text-amber-300 ring-amber-500/20";
      case "success":
        return "bg-emerald-950/80 border-emerald-500/50 text-emerald-300 ring-emerald-500/20";
      case "info":
        return "bg-cyan-950/80 border-cyan-500/50 text-cyan-300 ring-cyan-500/20";
      case "purple":
        return "bg-purple-950/80 border-purple-500/50 text-purple-300 ring-purple-500/20";
      case "gold":
        return "bg-yellow-950/80 border-yellow-500/50 text-yellow-300 ring-yellow-500/20 shadow-yellow-500/10";
      case "dark":
        return "bg-indigo-950/90 border-indigo-500/50 text-indigo-300 ring-indigo-500/20";
      default:
        return "bg-gray-800 border-gray-600 text-gray-300";
    }
  };

  const getProgressColor = (statusType: string) => {
    switch (statusType) {
      case "danger":
        return "bg-rose-500 shadow-rose-500/50";
      case "warning":
        return "bg-amber-500 shadow-amber-500/50";
      case "success":
        return "bg-emerald-500 shadow-emerald-500/50";
      case "info":
        return "bg-cyan-500 shadow-cyan-500/50";
      case "purple":
        return "bg-purple-500 shadow-purple-500/50";
      case "gold":
        return "bg-yellow-400 shadow-yellow-400/50";
      case "dark":
        return "bg-indigo-600 shadow-indigo-600/50";
      default:
        return "bg-gray-400";
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Banner: Flat Index Explanation */}
      <div className="bg-space-800 border border-space-border p-4 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 rounded-xl">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-white tracking-tight">
                4D Discrete State Classification HUD
              </h3>
              <span className="px-2 py-0.5 bg-cyan-950 border border-cyan-500/40 text-cyan-300 text-[11px] font-mono font-bold rounded-full">
                5 × 4 × 3 × 2 = 120 STATES
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">
              Continuous physical telemetry binned into discrete MDP state vectors for Q-table lookup.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4 bg-space-900 border border-space-border px-4 py-2.5 rounded-xl">
          <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">
            Q-Table Row Index (s):
          </span>
          <div className="flex items-baseline space-x-1 font-mono">
            <span className="text-2xl font-black text-cyan-400">
              {bins.flatStateIndex}
            </span>
            <span className="text-xs text-gray-400 font-medium">/ 119</span>
          </div>
        </div>
      </div>

      {/* 4 Bin Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Bin 1: Altitude */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Compass className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                1. Altitude (s_alt)
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-gray-400">
              {altitudeKm.toFixed(1)} km
            </span>
          </div>

          <div
            className={`px-3 py-2 border rounded-xl font-mono text-xs font-bold ring-1 flex items-center justify-between ${getBadgeStyle(
              bins.altBin.statusType
            )}`}
          >
            <span>{bins.altBin.label}</span>
            <span className="text-[10px] opacity-80 uppercase">Bin {bins.altBin.binIndex}</span>
          </div>

          <div className="w-full bg-space-900 h-2 rounded-full overflow-hidden border border-space-border">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor(
                bins.altBin.statusType
              )}`}
              style={{ width: `${bins.altBin.progressPct}%` }}
            />
          </div>

          <p className="text-[11px] text-gray-400 leading-snug">
            {bins.altBin.description}
          </p>
        </div>

        {/* Bin 2: Battery Charge */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Battery className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                2. Battery (s_soc)
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-gray-400">
              {socPct.toFixed(1)}%
            </span>
          </div>

          <div
            className={`px-3 py-2 border rounded-xl font-mono text-xs font-bold ring-1 flex items-center justify-between ${getBadgeStyle(
              bins.socBin.statusType
            )}`}
          >
            <span>{bins.socBin.label}</span>
            <span className="text-[10px] opacity-80 uppercase">Bin {bins.socBin.binIndex}</span>
          </div>

          <div className="w-full bg-space-900 h-2 rounded-full overflow-hidden border border-space-border">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor(
                bins.socBin.statusType
              )}`}
              style={{ width: `${bins.socBin.progressPct}%` }}
            />
          </div>

          <p className="text-[11px] text-gray-400 leading-snug">
            {bins.socBin.description}
          </p>
        </div>

        {/* Bin 3: Propellant Reserve */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Flame className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                3. Propellant (s_fuel)
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-gray-400">
              {(propellantKg * 1000).toFixed(0)} g
            </span>
          </div>

          <div
            className={`px-3 py-2 border rounded-xl font-mono text-xs font-bold ring-1 flex items-center justify-between ${getBadgeStyle(
              bins.fuelBin.statusType
            )}`}
          >
            <span className="truncate">{bins.fuelBin.label}</span>
            <span className="text-[10px] opacity-80 uppercase ml-1">Bin {bins.fuelBin.binIndex}</span>
          </div>

          <div className="w-full bg-space-900 h-2 rounded-full overflow-hidden border border-space-border">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor(
                bins.fuelBin.statusType
              )}`}
              style={{ width: `${bins.fuelBin.progressPct}%` }}
            />
          </div>

          <p className="text-[11px] text-gray-400 leading-snug">
            {bins.fuelBin.description}
          </p>
        </div>

        {/* Bin 4: Illumination */}
        <div className="bg-space-800 border border-space-border p-4 rounded-xl shadow-lg flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sun className="w-4 h-4 text-yellow-400" />
              <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
                4. Daylight (s_sun)
              </span>
            </div>
            <span className="text-xs font-mono font-bold text-gray-400">
              {inSun === 1 ? "Sunlight (+8W)" : "Shadow (0W)"}
            </span>
          </div>

          <div
            className={`px-3 py-2 border rounded-xl font-mono text-xs font-bold ring-1 flex items-center justify-between ${getBadgeStyle(
              bins.sunBin.statusType
            )}`}
          >
            <span>{bins.sunBin.label}</span>
            <span className="text-[10px] opacity-80 uppercase">Bin {bins.sunBin.binIndex}</span>
          </div>

          <div className="w-full bg-space-900 h-2 rounded-full overflow-hidden border border-space-border">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor(
                bins.sunBin.statusType
              )}`}
              style={{ width: `${bins.sunBin.progressPct}%` }}
            />
          </div>

          <p className="text-[11px] text-gray-400 leading-snug">
            {bins.sunBin.description}
          </p>
        </div>
      </div>
    </div>
  );
};
