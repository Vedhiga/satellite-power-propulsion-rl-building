class RuleBasedController:
    """
    Deterministic Heuristic Rule-Based Controller for Autonomous Satellite Operations.
    Implements coupled energy and propulsion management heuristics:
    - Energy Management:
        * Safe Mode (2.0 W) if SOC < 0.30 (Battery Recovery)
        * Payload Mode (12.0 W) if SOC >= 0.30 and in direct sunlight
        * Standard Mode (5.0 W) if SOC >= 0.30 and in eclipse
    - Propulsion Management:
        * Inhibit Thruster Burn (0.0 s) if SOC <= 0.25 (Power Safety Interlock)
        * Command 10.0 s Burn if Altitude < 392.0 km (Urgent Orbit Recovery)
        * Command 2.0 s Burn if 392.0 km <= Altitude < 398.0 km (Proportional Station-keeping)
        * Command 0.0 s Burn if Altitude >= 398.0 km (Idle Orbit Maintenance)
    """
    def __init__(self):
        # Action Table Mapping: (power_mode, burn_duration_s) -> action_idx
        self.action_map = {
            (0, 0.0): 0, (0, 2.0): 1, (0, 10.0): 2,
            (1, 0.0): 3, (1, 2.0): 4, (1, 10.0): 5,
            (2, 0.0): 6, (2, 2.0): 7, (2, 10.0): 8
        }

    def select_action(self, env):
        """
        Selects discrete action index based on current environment state attributes.
        """
        # Determine eclipse / sunlight state
        orbit_phase = (env.time % env.cfg.orbit_period_s) / env.cfg.orbit_period_s
        is_sun = 0 if orbit_phase < env.cfg.eclipse_fraction else 1

        # 1. Energy Management Strategy
        if env.soc < 0.30:
            power_mode = 0  # Safe Mode (2.0 W)
        elif is_sun == 1:
            power_mode = 2  # Payload Mode (12.0 W)
        else:
            power_mode = 1  # Standard Mode (5.0 W)

        # 2. Propulsion Station-keeping Strategy
        if env.soc <= 0.25:
            burn_duration = 0.0  # Safety interlock: inhibit propulsion when battery is low
        elif env.altitude < 392.0:
            burn_duration = 10.0  # Major recovery burn
        elif 392.0 <= env.altitude < 398.0:
            burn_duration = 2.0   # Proportional thrust correction
        else:
            burn_duration = 0.0   # Idle (no burn needed near target 400.0 km)

        return self.action_map[(power_mode, burn_duration)]
