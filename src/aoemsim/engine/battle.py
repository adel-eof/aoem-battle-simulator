"""Deterministic battle engine for AOEM Battle Simulator."""


from pydantic import BaseModel

from aoemsim.engine.rng import RngRollEvent, RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.lineup import Lineup


class BattleResult(BaseModel):
    """Result of a single battle simulation."""

    winner: str | None = None
    duration_ticks: int
    duration_sec: float
    finish_reason: str
    attacker_final_hp: float
    defender_final_hp: float
    rng_history: list[RngRollEvent]


class BattleEngine:
    """Core engine responsible for running a deterministic tick-based battle."""

    def __init__(
        self,
        attacker_lineup: Lineup,
        defender_lineup: Lineup,
        max_duration_sec: float = 90.0,
        tick_sec: float = 0.1,
    ):
        self.attacker_lineup = attacker_lineup
        self.defender_lineup = defender_lineup
        self.max_duration_sec = max_duration_sec
        self.tick_sec = tick_sec

    def run(self, seed: int) -> BattleResult:
        """Run the battle simulation from start to finish using the given seed."""
        rng = RngService(seed)

        # Initialize runtime state
        attacker_state = TroopState(
            hp=self.attacker_lineup.troop.total_hp,
            max_hp=self.attacker_lineup.troop.total_hp,
        )
        defender_state = TroopState(
            hp=self.defender_lineup.troop.total_hp,
            max_hp=self.defender_lineup.troop.total_hp,
        )

        tick = 0
        max_ticks = int(self.max_duration_sec / self.tick_sec)
        finish_reason = "timeout"
        winner = None

        while tick < max_ticks:
            # 1. Termination checks
            if attacker_state.hp <= 0 and defender_state.hp <= 0:
                finish_reason = "draw"
                break
            if defender_state.hp <= 0:
                finish_reason = "victory"
                winner = self.attacker_lineup.name
                break
            if attacker_state.hp <= 0:
                finish_reason = "defeat"
                winner = self.defender_lineup.name
                break

            # 2. Tick Logic (Placeholder for M2-001)
            self._process_tick(tick, attacker_state, defender_state, rng)

            tick += 1

        # Check winner on final tick if not already caught (due to loop limit)
        if finish_reason == "timeout":
            if attacker_state.hp <= 0 and defender_state.hp <= 0:
                finish_reason = "draw"
            elif defender_state.hp <= 0:
                finish_reason = "victory"
                winner = self.attacker_lineup.name
            elif attacker_state.hp <= 0:
                finish_reason = "defeat"
                winner = self.defender_lineup.name

        return BattleResult(
            winner=winner,
            duration_ticks=tick,
            duration_sec=round(tick * self.tick_sec, 2),
            finish_reason=finish_reason,
            attacker_final_hp=max(0.0, attacker_state.hp),
            defender_final_hp=max(0.0, defender_state.hp),
            rng_history=rng.history,
        )

    def _process_tick(
        self, tick: int, attacker: TroopState, defender: TroopState, rng: RngService
    ) -> None:
        """Process a single tick of battle. Can be overridden for testing or specific logic."""
        # Record a dummy RNG roll to verify determinism in tests
        rng.random(source="tick_start")
