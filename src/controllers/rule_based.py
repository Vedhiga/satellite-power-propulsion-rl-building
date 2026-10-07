class RuleBasedController:
    """
    Deterministic Heuristic Rule-Based Controller for Autonomous Satellite Operations.
    Implements coupled energy and propulsion management heuristics.
    """
    def __init__(self, env=None):
        self.env = env
        # Action Table Mapping: (power_mode, burn_duration_s) -> action_idx
        self.action_map = {
            (0, 0.0): 0, (0, 2.0): 1, (0, 10.0): 2,
            (1, 0.0): 3, (1, 2.0): 4, (1, 10.0): 5,
            (2, 0.0): 6, (2, 2.0): 7, (2, 10.0): 8
        }

    def select_action(self, *args, **kwargs):
        """
        Flexibly accepts either select_action(env) or select_action(altitude, soc, is_sun).
        """
        if len(args) == 1 and hasattr(args[0], 'soc'):
            env = args[0]
            altitude = env.altitude
            soc = env.soc
            orbit_phase = (env.time % env.cfg.orbit_period_s) / env.cfg.orbit_period_s
            is_sun = 0 if orbit_phase < env.cfg.eclipse_fraction else 1
        elif len(args) >= 2:
            altitude = args[0]
            soc = args[1]
            is_sun = args[2] if len(args) > 2 else 1
        elif self.env is not None:
            env = self.env
            altitude = env.altitude
            soc = env.soc
            orbit_phase = (env.time % env.cfg.orbit_period_s) / env.cfg.orbit_period_s
            is_sun = 0 if orbit_phase < env.cfg.eclipse_fraction else 1
        else:
            raise ValueError("Environment or state parameters must be provided to RuleBasedController.")

        # 1. Energy Management Strategy
        if soc < 0.30:
            power_mode = 0  # Safe Mode (2.0 W)
        elif is_sun == 1:
            power_mode = 2  # Payload Mode (12.0 W)
        else:
            power_mode = 1  # Standard Mode (5.0 W)

        # 2. Propulsion Station-keeping Strategy
        if soc <= 0.25:
            burn_duration = 0.0  # Safety interlock
        elif altitude < 392.0:
            burn_duration = 10.0  # Major recovery burn
        elif 392.0 <= altitude < 398.0:
            burn_duration = 2.0   # Proportional thrust correction
        else:
            burn_duration = 0.0   # Idle

        return self.action_map[(power_mode, burn_duration)]
