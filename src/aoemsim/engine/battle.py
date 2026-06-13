"""Deterministic battle engine for AOEM Battle Simulator."""


from pydantic import BaseModel

from aoemsim.engine.rng import RngRollEvent, RngService
from aoemsim.engine.state import TroopState
from aoemsim.engine.synergy import apply_synergy_to_stats
from aoemsim.models.enums import StatKind
from aoemsim.models.hero import Hero
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
        attacker_heroes: list[Hero] | None = None,
        defender_heroes: list[Hero] | None = None,
        max_duration_sec: float = 90.0,
        tick_sec: float = 0.1,
    ):
        self.attacker_lineup = attacker_lineup
        self.defender_lineup = defender_lineup
        self.attacker_heroes = attacker_heroes or []
        self.defender_heroes = defender_heroes or []
        self.max_duration_sec = max_duration_sec
        self.tick_sec = tick_sec

    def run(self, seed: int) -> BattleResult:
        """Run the battle simulation from start to finish using the given seed."""
        rng = RngService(seed)

        # Calculate initial synergy bonuses
        attacker_synergy = apply_synergy_to_stats(
            self.attacker_heroes, self.attacker_lineup.troop.unit_type
        )
        defender_synergy = apply_synergy_to_stats(
            self.defender_heroes, self.defender_lineup.troop.unit_type
        )

        # Initialize runtime state
        attacker_state = TroopState(
            lineup=self.attacker_lineup,
            hp=self.attacker_lineup.troop.total_hp,
            max_hp=self.attacker_lineup.troop.total_hp,
            unit_type=self.attacker_lineup.troop.unit_type,
            synergy_bonus=attacker_synergy,
            stats_cache=self._prepare_stats_cache(self.attacker_heroes, attacker_synergy),
        )
        defender_state = TroopState(
            lineup=self.defender_lineup,
            hp=self.defender_lineup.troop.total_hp,
            max_hp=self.defender_lineup.troop.total_hp,
            unit_type=self.defender_lineup.troop.unit_type,
            synergy_bonus=defender_synergy,
            stats_cache=self._prepare_stats_cache(self.defender_heroes, defender_synergy),
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

    def _prepare_stats_cache(
        self, heroes: list[Hero], synergy_bonus: float
    ) -> dict[StatKind, float]:
        """Aggregate stats from all heroes and apply synergy bonus."""
        stats: dict[StatKind, float] = {}

        # Initialize base stats that must exist
        for kind in StatKind:
            total_val = 0.0
            for hero in heroes:
                if kind in hero.attributes:
                    total_val += hero.stat(kind)
            stats[kind] = total_val * (1 + synergy_bonus)

        return stats
