"use client";

import React from "react";
import { StepRecord } from "@/lib/satelliteSim";
import { Zap, Rocket, Target, ShieldCheck, AlertTriangle } from "lucide-react";

interface RuleInspectorProps {
  currentRecord: StepRecord;
}

export const RuleInspector: React.FC<RuleInspectorProps> = ({ currentRecord }) => {
  const {
    step,
    time_min,
    alt_before_km,
    soc_before_pct,
    power_mode,
    burn_duration_s,
    reward,
    telemetry,
  } = currentRecord;

  const inSun = telemetry.in_sun === 1.0;
  const m_used_kg = telemetry.m_used_g / 1000.0;

  // Normalized penalty calculation
  const norm_orbit_err = Math.abs(alt_before_km - 400.0) / 2.0;
  const norm_fuel_used = m_used_kg / (0.00045 * 10.0);
  const norm_power_bus = telemetry.P_bus / 12.67;
  const batt_pen = telemetry.batt_penalty;

  const c_orbit = 0.4 * norm_orbit_err;
  const c_fuel = 0.3 * norm_fuel_used;
  const c_power = 0.1 * norm_power_bus;
  const c_batt = 0.2 * batt_pen;
  const total_cost = c_orbit + c_fuel + c_power + c_batt;

  // Power Rationale Text
  let powerRationale = "";
  let powerBadgeClass = "";

  if (soc_before_pct < 30.0) {
    powerRationale = `Battery SOC (${soc_before_pct.toFixed(
      1
    )}%) is below 30.0% critical threshold. Non-essential payloads are shed to Safe Mode (2.0 W) to prioritize battery recovery.`;
    powerBadgeClass = "text-emerald-400 bg-emerald-950/50 border-emerald-800/60";
  } else if (inSun) {
    powerRationale = `Battery SOC (${soc_before_pct.toFixed(
      1
    )}%) is healthy (≥ 30%) and solar arrays are generating +8.0 W in Direct Sunlight. Activated High Payload Mode (12.0 W).`;
    powerBadgeClass = "text-purple-400 bg-purple-950/50 border-purple-800/60";
  } else {
    powerRationale = `Battery SOC (${soc_before_pct.toFixed(
      1
    )}%) is healthy (≥ 30%), but spacecraft is in Earth Shadow / Eclipse (0.0 W solar). Maintained Standard Mode (5.0 W) to avoid excessive battery drain.`;
    powerBadgeClass = "text-cyan-400 bg-cyan-950/50 border-cyan-800/60";
  }

  // Propulsion Rationale Text
  let propRationale = "";
  let propBadgeClass = "";

  if (soc_before_pct <= 25.0) {
    propRationale = `Battery SOC (${soc_before_pct.toFixed(
      1
    )}%) is ≤ 25.0%. Power Safety Interlock active: Thruster burn is strictly inhibited (0.0 s) to prevent battery brownout.`;
    propBadgeClass = "text-rose-400 bg-rose-950/50 border-rose-800/60";
  } else if (alt_before_km < 392.0) {
    propRationale = `Altitude (${alt_before_km.toFixed(
      2
    )} km) is severely degraded (< 392.0 km). Commanded Major Recovery Burn (10.0 s) to restore orbit altitude.`;
    propBadgeClass = "text-rose-400 bg-rose-950/50 border-rose-800/60";
  } else if (alt_before_km >= 392.0 && alt_before_km < 398.0) {
    propRationale = `Altitude (${alt_before_km.toFixed(
      2
    )} km) is below 398.0 km deadband. Commanded Proportional Corrective Burn (2.0 s) to offset drag decay.`;
    propBadgeClass = "text-amber-400 bg-amber-950/50 border-amber-800/60";
  } else {
    propRationale = `Altitude (${alt_before_km.toFixed(
      2
    )} km) is within or above station-keeping deadband (≥ 398.0 km). Thruster Idled (0.0 s).`;
    propBadgeClass = "text-emerald-400 bg-emerald-950/50 border-emerald-800/60";
  }

  return (
    <div className="bg-space-800 border border-space-border rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-space-border pb-4">
        <div>
          <div className="text-xs font-bold uppercase tracking-wider text-cyan-400">
            Decision Inspector (Causal Explainer)
          </div>
          <h3 className="text-lg font-bold text-white">
            Why Did the Satellite Do That at Step #{step}?
          </h3>
        </div>
        <div className="text-xs font-mono text-gray-400">
          Time: <span className="text-white font-bold">{time_min.toFixed(1)} mins</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* 1. Electrical Power Decision Card */}
        <div className="bg-space-900/70 border border-space-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-gray-300">
              <Zap className="w-4 h-4 text-purple-400" />
              <span>Energy Mode Decision</span>
            </div>
            <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-bold ${powerBadgeClass}`}>
              {power_mode === 0 ? "Safe (2W)" : power_mode === 1 ? "Standard (5W)" : "Payload (12W)"}
            </span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed bg-space-800/60 p-3 rounded-lg border border-space-border/50">
            {powerRationale}
          </p>
        </div>

        {/* 2. Propulsion Decision Card */}
        <div className="bg-space-900/70 border border-space-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-gray-300">
              <Rocket className="w-4 h-4 text-amber-400" />
              <span>Propulsion Decision</span>
            </div>
            <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-bold ${propBadgeClass}`}>
              {burn_duration_s === 0.0 ? "Idle (0s)" : burn_duration_s === 2.0 ? "Short Burn (2s)" : "Long Burn (10s)"}
            </span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed bg-space-800/60 p-3 rounded-lg border border-space-border/50">
            {propRationale}
          </p>
        </div>

        {/* 3. Multi-Objective Cost Breakdown */}
        <div className="bg-space-900/70 border border-space-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-gray-300">
              <Target className="w-4 h-4 text-emerald-400" />
              <span>Multi-Objective Cost</span>
            </div>
            <span className="text-xs font-mono font-bold text-rose-400">
              Reward: {reward.toFixed(4)}
            </span>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Orbit Error (40%)</span>
                <span className="font-mono text-gray-200">{c_orbit.toFixed(4)}</span>
              </div>
              <div className="w-full h-1.5 bg-space-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-cyan-400 rounded-full transition-all"
                  style={{ width: `${Math.min(100, (c_orbit / total_cost) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Fuel Mass Expended (30%)</span>
                <span className="font-mono text-gray-200">{c_fuel.toFixed(4)}</span>
              </div>
              <div className="w-full h-1.5 bg-space-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-400 rounded-full transition-all"
                  style={{ width: `${Math.min(100, (c_fuel / total_cost) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Power Bus Demand (10%)</span>
                <span className="font-mono text-gray-200">{c_power.toFixed(4)}</span>
              </div>
              <div className="w-full h-1.5 bg-space-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-400 rounded-full transition-all"
                  style={{ width: `${Math.min(100, (c_power / total_cost) * 100)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-gray-400 mb-1">
                <span>Battery Risk Penalty (20%)</span>
                <span className="font-mono text-gray-200">{c_batt.toFixed(4)}</span>
              </div>
              <div className="w-full h-1.5 bg-space-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-rose-500 rounded-full transition-all"
                  style={{ width: `${Math.min(100, (c_batt / (total_cost || 1)) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
