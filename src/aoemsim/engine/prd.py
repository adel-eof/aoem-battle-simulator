"""Pseudo-Random Distribution (PRD) engine for skill triggers."""

from dataclasses import dataclass


@dataclass
class PrdState:
    """State for tracking PRD roll progress for a specific skill."""

    skill_id: str
    fail_count: int = 0
    # [TBD: formula PRD resmi]
    # Current implementation uses C constant approximate logic.
    # C = f(P) where P is base chance.
    # For now, we will use a simplified lookup for common AoE-like PRD constants
    # or a linear increment as a placeholder.


class PrdEngine:
    """Engine for deterministic PRD evaluations."""

    def __init__(self) -> None:
        self._states: dict[str, PrdState] = {}

    def get_state(self, skill_id: str) -> PrdState:
        """Get or create PRD state for a skill."""
        if skill_id not in self._states:
            self._states[skill_id] = PrdState(skill_id=skill_id)
        return self._states[skill_id]

    def evaluate_trigger(self, skill_id: str, base_chance: float, roll: float) -> bool:
        """
        Evaluate if a skill triggers based on PRD.
        
        Args:
            skill_id: Unique identifier for the skill.
            base_chance: Base probability (0.0 to 1.0).
            roll: Random value from RNG service (0.0 to 1.0).
            
        Returns:
            True if the skill triggers, False otherwise.
        """
        state = self.get_state(skill_id)
        
        # [TBD: formula PRD resmi]
        # Using a simple cumulative probability increment as a placeholder
        # Actual PRD often uses P_current = C * (fail_count + 1)
        # For base_chance 0.2 (20%), C is approximately 0.0557
        # Since we don't have the table, we'll use a linear approximation for now.
        
        # Linear approximation of C-constant if not provided
        c_constant = self._calculate_c_constant(base_chance)
        current_chance = c_constant * (state.fail_count + 1)
        
        success = roll < current_chance
        
        if success:
            state.fail_count = 0
        else:
            state.fail_count += 1
            
        return success

    def _calculate_c_constant(self, p: float) -> float:
        """
        Placeholder linear approximation for PRD C-constant.
        [TBD: formula PRD resmi]
        """
        # This is a very rough approximation. Proper PRD uses precomputed tables.
        # For p=0.20, C=0.0557
        # For p=0.10, C=0.0147
        # For p=0.30, C=0.119
        if p <= 0:
            return 0.0
        if p >= 1:
            return 1.0
            
        # Linear ramp as placeholder
        return p * p # Just a placeholder approximation
