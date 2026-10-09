"use client";

import React from "react";
import { StepRecord } from "@/lib/satelliteSim";
import { Sun, Moon, Zap, Flame, ShieldAlert } from "lucide-react";

interface CentralOrbitDiagramProps {
  currentRecord: StepRecord;
}

export const CentralOrbitDiagram: React.FC<CentralOrbitDiagramProps> = ({
  currentRecord,
}) => {
  const telem = currentRecord.telemetry;
  const inSun = telem.in_sun === 1;
  const burnDur = currentRecord.burn_duration_s;
  const powerMode = currentRecord.power_mode;

  // Geometry calculations
  const cx = 250;
  const cy = 230;
  const earthRadius = 90;
  const orbitRadius = 160;

  // Convert orbital phase angle to radians (0 deg = right +X side, direct sun)
  // 35% eclipse zone is centered on the left (-X side, 180 deg)
  // Eclipse range: [180 - 63, 180 + 63] = [117 deg, 243 deg]
  const angleDeg = currentRecord.orbitPhaseAngleDeg % 360;
  const angleRad = (angleDeg * Math.PI) / 180;

  const satX = cx + orbitRadius * Math.cos(angleRad);
  const satY = cy + orbitRadius * Math.sin(angleRad);

  // Thruster vector angle (tangential to orbit direction)
  const thrustAngleRad = angleRad + Math.PI / 2;
  const flameLength = burnDur === 10.0 ? 30 : burnDur === 2.0 ? 18 : 0;
  const flameX = satX - flameLength * Math.cos(angleRad);
  const flameY = satY - flameLength * Math.sin(angleRad);

  // Narrative generation
  let narrativeText = "";
  const altKmStr = currentRecord.alt_km.toFixed(1);
  const socPctStr = currentRecord.soc_pct.toFixed(1);

  if (!inSun) {
    if (burnDur > 0) {
      narrativeText = `Satellite is in Earth's Shadow (Eclipse). Solar generation is 0.0 W. Battery is discharging. Thruster fired for ${burnDur}s (+4.0 W valve load), drawing bus power to ${telem.P_bus.toFixed(1)} W at ${altKmStr} km altitude.`;
    } else if (currentRecord.soc_pct < 25) {
      narrativeText = `Satellite is in Earth's Shadow (Eclipse). Battery is critically low (${socPctStr}%). Controller locks out thruster burns to prevent brownout until sunlight is reached.`;
    } else {
      narrativeText = `Satellite is in Earth's Shadow (Eclipse). Solar generation is 0.0 W. Bus power load is ${telem.P_bus.toFixed(1)} W. Altitude is ${altKmStr} km (${currentRecord.bins.altBin.label.split("-")[1]?.trim() || ""}). Thruster is idle.`;
    }
  } else {
    if (burnDur > 0) {
      narrativeText = `Satellite is in Direct Sunlight. Solar arrays generate +8.0 W. Thruster burn executed for ${burnDur}s (${telem.boost_km.toFixed(3)} km boost). Net power is ${telem.P_net >= 0 ? "+" : ""}${telem.P_net.toFixed(1)} W.`;
    } else if (powerMode === 2) {
      narrativeText = `Satellite is in Direct Sunlight. Solar arrays generate +8.0 W. High-Duty Payload (12 W) enabled. Battery SOC is ${socPctStr}%. Altitude is ${altKmStr} km.`;
    } else {
      narrativeText = `Satellite is in Direct Sunlight. Solar arrays generate +8.0 W. Battery charging at ${telem.P_net >= 0 ? "+" : ""}${telem.P_net.toFixed(1)} W. Altitude is ${altKmStr} km.`;
    }
  }

  return (
    <div className="bg-space-800 border border-space-border rounded-2xl p-5 shadow-xl flex flex-col justify-between space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 rounded-xl">
            {inSun ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-indigo-400" />}
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">
              2D LEO Orbital Vector Diagram
            </h3>
            <p className="text-[11px] text-gray-400">
              Real-time Earth shadow cone, solar radiation inflow & thruster exhaust
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <span
            className={`px-2.5 py-1 rounded-full font-bold border ${
              inSun
                ? "bg-yellow-950/80 border-yellow-500/50 text-yellow-300"
                : "bg-indigo-950/90 border-indigo-500/50 text-indigo-300"
            }`}
          >
            {inSun ? "☀️ SUNLIGHT (8.0W)" : "🌑 ECLIPSE (0.0W)"}
          </span>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="relative w-full aspect-[5/4] bg-space-900 border border-space-border rounded-xl overflow-hidden flex items-center justify-center">
        <svg viewBox="0 0 500 460" className="w-full h-full">
          <defs>
            {/* Earth Gradient */}
            <radialGradient id="earthGrad" cx="40%" cy="40%" r="60%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="50%" stopColor="#0284c7" />
              <stop offset="85%" stopColor="#0369a1" />
              <stop offset="100%" stopColor="#082f49" />
            </radialGradient>

            {/* Atmosphere Glow */}
            <radialGradient id="atmoGlow" cx="50%" cy="50%" r="50%">
              <stop offset="70%" stopColor="#38bdf8" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </radialGradient>

            {/* Shadow Cone Gradient */}
            <linearGradient id="shadowGrad" x1="1" y1="0" x2="0" y2="0">
              <stop offset="0%" stopColor="#020617" stopOpacity="0.9" />
              <stop offset="70%" stopColor="#090d16" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#0b0f19" stopOpacity="0.2" />
            </linearGradient>

            {/* Sun Vector Rays Gradient */}
            <linearGradient id="sunRaysGrad" x1="1" y1="0" x2="0" y2="0">
              <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#fbbf24" stopOpacity="0" />
            </linearGradient>

            {/* Thruster Flame Gradient */}
            <radialGradient id="flameGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#ef4444" />
              <stop offset="50%" stopColor="#f97316" />
              <stop offset="100%" stopColor="#fbbf24" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Grid lines & Space Stars Background */}
          <circle cx={cx} cy={cy} r={orbitRadius + 40} stroke="#1e293b" strokeWidth="1" strokeDasharray="3 6" fill="none" />
          
          {/* Sun Radiation Vector Inflow (from right +X side) */}
          <rect x="360" y="50" width="130" height="360" fill="url(#sunRaysGrad)" />
          {[80, 140, 200, 260, 320, 380].map((y, idx) => (
            <g key={idx}>
              <line x1="480" y1={y} x2="380" y2={y} stroke="#fbbf24" strokeWidth="1.5" strokeDasharray="4 4" opacity="0.6" />
              <polygon points={`380,${y} 388,${y-3} 388,${y+3}`} fill="#fbbf24" opacity="0.8" />
            </g>
          ))}

          {/* Earth Shadow Cone (Umbra - Left side, 35% eclipse wedge) */}
          <polygon
            points={`${cx},${cy - earthRadius * 0.95} 0,60 0,400 ${cx},${cy + earthRadius * 0.95}`}
            fill="url(#shadowGrad)"
          />

          {/* Atmosphere Glow Ring */}
          <circle cx={cx} cy={cy} r={earthRadius + 14} fill="url(#atmoGlow)" />

          {/* Earth Body */}
          <circle cx={cx} cy={cy} r={earthRadius} fill="url(#earthGrad)" stroke="#0284c7" strokeWidth="2" />
          
          {/* Continental Shading Overlay */}
          <path
            d={`M ${cx - 40} ${cy - 30} Q ${cx - 10} ${cy - 60} ${cx + 30} ${cy - 40} Q ${cx + 50} ${cy} ${cx + 10} ${cy + 40} Q ${cx - 30} ${cy + 50} ${cx - 50} ${cy + 10} Z`}
            fill="#15803d"
            opacity="0.35"
          />

          {/* Circular LEO Orbit Track (400 km radius scale) */}
          <circle
            cx={cx}
            cy={cy}
            r={orbitRadius}
            stroke={inSun ? "#0284c7" : "#475569"}
            strokeWidth="2"
            strokeDasharray="6 6"
            fill="none"
          />
          
          {/* Target Deadband Zone (398 - 402 km) ring indicator */}
          <circle
            cx={cx}
            cy={cy}
            r={orbitRadius}
            stroke="#10b981"
            strokeWidth="6"
            strokeOpacity="0.15"
            fill="none"
          />

          {/* Satellite Position Line from Earth Center */}
          <line x1={cx} y1={cy} x2={satX} y2={satY} stroke="#334155" strokeWidth="1" strokeDasharray="2 4" />

          {/* Active Thruster Flame Effect (if firing) */}
          {burnDur > 0 && (
            <g>
              <circle cx={flameX} cy={flameY} r={burnDur === 10.0 ? 14 : 9} fill="url(#flameGrad)" className="animate-pulse" />
              <line x1={satX} y1={satY} x2={flameX} y2={flameY} stroke="#ef4444" strokeWidth="4" strokeLinecap="round" />
            </g>
          )}

          {/* Solar Aura Halo in Sunlight */}
          {inSun && (
            <circle cx={satX} cy={satY} r="18" fill="#fbbf24" opacity="0.25" className="animate-ping" />
          )}

          {/* Satellite Marker Body */}
          <g transform={`translate(${satX}, ${satY})`}>
            {/* Solar Panel Wings */}
            <rect
              x="-16"
              y="-4"
              width="8"
              height="8"
              fill={inSun ? "#fbbf24" : "#475569"}
              stroke={inSun ? "#d97706" : "#334155"}
              strokeWidth="1"
              rx="1"
            />
            <rect
              x="8"
              y="-4"
              width="8"
              height="8"
              fill={inSun ? "#fbbf24" : "#475569"}
              stroke={inSun ? "#d97706" : "#334155"}
              strokeWidth="1"
              rx="1"
            />
            
            {/* Bus Body */}
            <rect
              x="-7"
              y="-7"
              width="14"
              height="14"
              fill={burnDur > 0 ? "#f43f5e" : "#0284c7"}
              stroke="#ffffff"
              strokeWidth="1.5"
              rx="2"
            />

            {/* Subsystem LED indicator */}
            <circle cx="0" cy="0" r="2.5" fill={inSun ? "#10b981" : "#6366f1"} />
          </g>

          {/* Annotations */}
          <text x="430" y="40" fill="#fbbf24" fontSize="11" fontWeight="bold" textAnchor="middle">
            SUNLIGHT INFLOW (+8W)
          </text>
          <text x="60" y="230" fill="#818cf8" fontSize="11" fontWeight="bold" textAnchor="middle">
            EARTH SHADOW (UMBRA)
          </text>
          <text x={cx} y={cy + 4} fill="#ffffff" fontSize="12" fontWeight="bold" textAnchor="middle" opacity="0.9">
            EARTH (R_E = 6378 km)
          </text>
        </svg>
      </div>

      {/* Dynamic Context Banner below Diagram */}
      <div className="bg-space-900 border border-space-border p-4 rounded-xl shadow-inner flex items-start space-x-3">
        <div className={`p-2 rounded-lg mt-0.5 ${inSun ? "bg-amber-950 border border-amber-500/40 text-amber-300" : "bg-indigo-950 border border-indigo-500/40 text-indigo-300"}`}>
          {burnDur > 0 ? <Flame className="w-5 h-5 text-rose-400 animate-bounce" /> : inSun ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-300">
              Live Operational Narrative Explanation
            </span>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-500/30">
              {inSun ? "SUNLIGHT PHASE" : "ECLIPSE PHASE"}
            </span>
          </div>
          <p className="text-xs text-gray-200 mt-1 leading-relaxed">
            {narrativeText}
          </p>
        </div>
      </div>
    </div>
  );
};
