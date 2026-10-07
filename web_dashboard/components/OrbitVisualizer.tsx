"use client";

import React from "react";
import { StepRecord } from "@/lib/satelliteSim";
import { Sun, Moon, Flame } from "lucide-react";

interface OrbitVisualizerProps {
  currentRecord: StepRecord;
}

export const OrbitVisualizer: React.FC<OrbitVisualizerProps> = ({ currentRecord }) => {
  const { telemetry, time_s, time_min, burn_duration_s } = currentRecord;
  const inSun = telemetry.in_sun === 1.0;

  // 92.5 minute LEO orbital period
  const orbitPeriodS = 92.5 * 60.0;
  const orbitPhase = (time_s % orbitPeriodS) / orbitPeriodS;
  const theta = orbitPhase * 2 * Math.PI;

  // 2D Canvas SVG coordinates (center 200, 200)
  const cx = 200;
  const cy = 200;
  const rEarth = 65;
  const rOrbit = 130;

  // Satellite position
  const satX = cx + rOrbit * Math.cos(theta);
  const satY = cy + rOrbit * Math.sin(theta);

  // Thruster plume direction (opposite velocity vector)
  // Velocity direction angle = theta + pi/2
  // Plume direction angle = theta - pi/2
  const plumeAngle = theta - Math.PI / 2;
  const plumeX = satX + 18 * Math.cos(plumeAngle);
  const plumeY = satY + 18 * Math.sin(plumeAngle);

  // Shadow Sector Arc (0.0 to 0.35 phase = 0 to 126 degrees)
  const shadowStartAngle = 0;
  const shadowEndAngle = 0.35 * 2 * Math.PI;
  
  const shadowStartX = cx + (rOrbit + 30) * Math.cos(shadowStartAngle);
  const shadowStartY = cy + (rOrbit + 30) * Math.sin(shadowStartAngle);
  const shadowEndX = cx + (rOrbit + 30) * Math.cos(shadowEndAngle);
  const shadowEndY = cy + (rOrbit + 30) * Math.sin(shadowEndAngle);

  const shadowPath = `M ${cx} ${cy} L ${shadowStartX} ${shadowStartY} A ${rOrbit + 30} ${rOrbit + 30} 0 0 1 ${shadowEndX} ${shadowEndY} Z`;

  return (
    <div className="bg-space-800 border border-space-border rounded-2xl p-5 shadow-xl flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">
            2D Orbital Geometry & Lighting
          </span>
        </div>

        {/* Dynamic Illumination Tag */}
        <div
          className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold transition-all ${
            inSun
              ? "bg-amber-950/60 border border-amber-500/50 text-amber-300 shadow-md shadow-amber-500/10"
              : "bg-indigo-950/60 border border-indigo-500/50 text-indigo-300 shadow-md shadow-indigo-500/10"
          }`}
        >
          {inSun ? (
            <>
              <Sun className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
              <span>Direct Sunlight (+8.0 W)</span>
            </>
          ) : (
            <>
              <Moon className="w-3.5 h-3.5 text-indigo-400" />
              <span>Earth Shadow / Eclipse (0.0 W)</span>
            </>
          )}
        </div>
      </div>

      {/* SVG Canvas schematic */}
      <div className="relative flex items-center justify-center py-2">
        <svg viewBox="0 0 400 400" className="w-full max-w-[340px] h-auto overflow-visible">
          <defs>
            {/* Earth Blue Gradient */}
            <radialGradient id="earthGrad" cx="40%" cy="40%" r="60%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="70%" stopColor="#0284c7" />
              <stop offset="100%" stopColor="#0369a1" />
            </radialGradient>

            {/* Earth Night Side Shading */}
            <linearGradient id="nightGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(0,0,0,0.8)" />
              <stop offset="50%" stopColor="rgba(0,0,0,0.4)" />
              <stop offset="100%" stopColor="rgba(0,0,0,0)" />
            </linearGradient>

            {/* Sun Rays Arrow */}
            <marker
              id="sunArrow"
              viewBox="0 0 10 10"
              refX="5"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#fbbf24" />
            </marker>
          </defs>

          {/* 1. Earth Shadow Cone (35% Eclipse Arc) */}
          <path d={shadowPath} fill="rgba(17, 24, 39, 0.75)" stroke="rgba(75, 85, 99, 0.4)" strokeDasharray="3 3" />

          {/* 2. Circular Orbit Track */}
          <circle
            cx={cx}
            cy={cy}
            r={rOrbit}
            fill="none"
            stroke="#374151"
            strokeWidth="2"
            strokeDasharray="4 4"
          />

          {/* 3. Earth Sphere */}
          <circle cx={cx} cy={cy} r={rEarth} fill="url(#earthGrad)" />
          {/* Earth Night Hemisphere (Left half) */}
          <path
            d={`M ${cx} ${cy - rEarth} A ${rEarth} ${rEarth} 0 0 0 ${cx} ${cy + rEarth} Z`}
            fill="rgba(5, 10, 20, 0.65)"
          />

          <text x={cx} y={cy + 4} textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="bold">
            Earth (LEO)
          </text>

          {/* 4. Sun Flux Vector Arrows (Right Side) */}
          {[120, 160, 200, 240, 280].map((yVal, i) => (
            <line
              key={i}
              x1="380"
              y1={yVal}
              x2="340"
              y2={yVal}
              stroke="#fbbf24"
              strokeWidth="2"
              markerEnd="url(#sunArrow)"
              opacity="0.85"
            />
          ))}

          <text x="360" y="95" textAnchor="middle" fill="#fbbf24" fontSize="10" fontWeight="bold">
            SUNLIGHT ☀️
          </text>

          {/* 5. Satellite Thruster Burn Plume Flash */}
          {burn_duration_s > 0 && (
            <g>
              <circle
                cx={plumeX}
                cy={plumeY}
                r={burn_duration_s === 10.0 ? "10" : "6"}
                fill="#ef4444"
                opacity="0.8"
                className="animate-ping"
              />
              <circle
                cx={plumeX}
                cy={plumeY}
                r={burn_duration_s === 10.0 ? "7" : "4"}
                fill="#f97316"
              />
            </g>
          )}

          {/* 6. Satellite Body Marker */}
          <circle
            cx={satX}
            cy={satY}
            r="8"
            fill={inSun ? "#10b981" : "#ef4444"}
            stroke="#ffffff"
            strokeWidth="2"
          />

          <text
            x={satX}
            y={satY - 14}
            textAnchor="middle"
            fill="#ffffff"
            fontSize="10"
            fontWeight="bold"
            className="drop-shadow-md"
          >
            SAT
          </text>

          {/* Thruster Flame Icon if active */}
          {burn_duration_s > 0 && (
            <text x={satX + 14} y={satY + 4} fontSize="12">
              🔥
            </text>
          )}
        </svg>
      </div>

      {/* Real-time Subsystem Status Footer */}
      <div className="grid grid-cols-2 gap-2 mt-2 pt-3 border-t border-space-border text-xs">
        <div className="bg-space-900/60 p-2 rounded-lg border border-space-border/50">
          <span className="text-gray-400 block text-[10px] uppercase">Orbital Phase</span>
          <span className="font-mono font-bold text-white">{(orbitPhase * 100).toFixed(1)}% Orbit</span>
        </div>
        <div className="bg-space-900/60 p-2 rounded-lg border border-space-border/50">
          <span className="text-gray-400 block text-[10px] uppercase">Mission Time</span>
          <span className="font-mono font-bold text-white">{time_min.toFixed(1)} mins</span>
        </div>
      </div>
    </div>
  );
};
