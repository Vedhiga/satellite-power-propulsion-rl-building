"use client";

import React from "react";
import { StepRecord } from "@/lib/satelliteSim";
import {
  ResponsiveContainer,
  ComposedChart,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Area,
  ReferenceArea,
} from "recharts";

interface TelemetryChartsProps {
  trajectory: StepRecord[];
  currentStep: number;
}

export const TelemetryCharts: React.FC<TelemetryChartsProps> = ({
  trajectory,
  currentStep,
}) => {
  const chartData = trajectory.map((rec) => ({
    step: rec.step,
    time_min: Number(rec.time_min.toFixed(1)),
    alt_km: Number(rec.alt_km.toFixed(3)),
    target_alt: 400.0,
    deadband_lower: 398.0,
    deadband_upper: 402.0,
    soc_pct: Number(rec.soc_pct.toFixed(2)),
    P_gen: Number(rec.telemetry.P_gen.toFixed(1)),
    P_bus: Number(rec.telemetry.P_bus.toFixed(2)),
    burn_dur: rec.burn_duration_s,
    is_burn_2s: rec.burn_duration_s === 2.0 ? rec.alt_km : null,
    is_burn_10s: rec.burn_duration_s === 10.0 ? rec.alt_km : null,
  }));

  const currentMin = trajectory[currentStep - 1]?.time_min.toFixed(1) ?? 0;

  return (
    <div className="space-y-6">
      {/* 1. Altitude Tracking Chart */}
      <div className="bg-space-800 border border-space-border rounded-2xl p-5 shadow-xl">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">
              Orbital Altitude Tracking & Station-Keeping Burns
            </h4>
            <p className="text-xs text-gray-400">
              Drag decay vs. Impulsive Thruster Boosts (Target: 400.0 km, Deadband: 398–402 km)
            </p>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              <span className="text-gray-300">Altitude</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span className="text-gray-300">Target (400km)</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span className="text-gray-300">2s Burn</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              <span className="text-gray-300">10s Burn</span>
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="time_min" stroke="#6b7280" fontSize={11} unit=" m" />
              <YAxis domain={[388, 406]} stroke="#6b7280" fontSize={11} unit="km" />
              <Tooltip
                contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "8px" }}
                itemStyle={{ fontSize: "12px" }}
                labelFormatter={(val) => `Time: ${val} mins (Step ${chartData.find((d) => d.time_min === val)?.step})`}
              />

              {/* Station-keeping Deadband (398 - 402 km) */}
              <ReferenceArea
                y1={398.0}
                y2={402.0}
                fill="#10b981"
                fillOpacity={0.08}
                stroke="#10b981"
                strokeOpacity={0.2}
                strokeDasharray="2 2"
              />

              {/* Target Altitude Line */}
              <ReferenceLine y={400.0} stroke="#10b981" strokeDasharray="4 4" strokeWidth={1.5} />

              {/* Active Scrubber Reference Line */}
              <ReferenceLine x={Number(currentMin)} stroke="#ffffff" strokeDasharray="2 2" strokeWidth={1.5} />

              {/* Altitude Trajectory Line */}
              <Line
                type="monotone"
                dataKey="alt_km"
                stroke="#06b6d4"
                strokeWidth={2.5}
                dot={false}
                name="Altitude (km)"
              />

              {/* 2s Burn Markers */}
              <Line
                type="monotone"
                dataKey="is_burn_2s"
                stroke="none"
                dot={{ r: 5, fill: "#f59e0b", stroke: "#ffffff", strokeWidth: 1.5 }}
                name="2.0s Burn"
              />

              {/* 10s Burn Markers */}
              <Line
                type="monotone"
                dataKey="is_burn_10s"
                stroke="none"
                dot={{ r: 7, fill: "#ef4444", stroke: "#ffffff", strokeWidth: 1.5 }}
                name="10.0s Burn"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 2. Power Balance & Battery SOC Chart */}
      <div className="bg-space-800 border border-space-border rounded-2xl p-5 shadow-xl">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">
              Electrical Power Balance & Battery State of Charge (SOC)
            </h4>
            <p className="text-xs text-gray-400">
              Solar Array Harvesting (P_gen) vs. Total Bus Demand (P_bus) and Battery Dynamics
            </p>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span className="text-gray-300">P_gen (8W)</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
              <span className="text-gray-300">P_bus Demand</span>
            </span>
            <span className="flex items-center space-x-1">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              <span className="text-gray-300">Battery SOC %</span>
            </span>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="time_min" stroke="#6b7280" fontSize={11} unit=" m" />
              
              {/* Left Y-Axis: Battery SOC % */}
              <YAxis yAxisId="soc" domain={[0, 100]} stroke="#06b6d4" fontSize={11} unit="%" />

              {/* Right Y-Axis: Power (Watts) */}
              <YAxis yAxisId="power" orientation="right" domain={[0, 15]} stroke="#f59e0b" fontSize={11} unit="W" />

              <Tooltip
                contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "8px" }}
                itemStyle={{ fontSize: "12px" }}
              />

              {/* 20% Critical Battery Safety Threshold */}
              <ReferenceLine
                yAxisId="soc"
                y={20.0}
                stroke="#ef4444"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                label={{ value: "20% Critical SOC Limit", fill: "#ef4444", fontSize: 10, position: "insideBottomLeft" }}
              />

              {/* Active Scrubber Reference Line */}
              <ReferenceLine yAxisId="soc" x={Number(currentMin)} stroke="#ffffff" strokeDasharray="2 2" strokeWidth={1.5} />

              {/* Solar Generation Area */}
              <Area
                yAxisId="power"
                type="stepAfter"
                dataKey="P_gen"
                fill="#10b981"
                fillOpacity={0.25}
                stroke="#10b981"
                strokeWidth={1.5}
                name="Solar Gen (W)"
              />

              {/* Bus Demand Line */}
              <Line
                yAxisId="power"
                type="stepAfter"
                dataKey="P_bus"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="3 3"
                dot={false}
                name="Bus Demand (W)"
              />

              {/* Battery SOC Line */}
              <Line
                yAxisId="soc"
                type="monotone"
                dataKey="soc_pct"
                stroke="#06b6d4"
                strokeWidth={2.5}
                dot={false}
                name="Battery SOC (%)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
