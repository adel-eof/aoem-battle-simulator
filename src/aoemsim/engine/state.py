"""Runtime state for battle simulation."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aoemsim.models.enums import CcType, StatKind, UnitType

if TYPE_CHECKING:
    from aoemsim.engine.effects_lifecycle import ActiveEffect
    from aoemsim.models.lineup import Lineup
    from aoemsim.models.skill import Skill


@dataclass
class TroopState:
    """Runtime state of a troop in battle."""

    lineup: "Lineup"
    hp: float
    max_hp: float
    unit_type: UnitType
    commander_skill: "Skill | None" = None
    stats_cache: dict[StatKind, float] = field(default_factory=dict)
    synergy_bonus: float = 0.0
    rage: float = 0.0
    effects: list[str] = field(default_factory=list)
    active_effects: list["ActiveEffect"] = field(default_factory=list)
    cooldowns: dict[str, float] = field(default_factory=dict)
    cc_timers: dict[CcType, int] = field(default_factory=dict)
    cc_immunity_timers: dict[CcType, int] = field(default_factory=dict)

    @property
    def is_alive(self) -> bool:
        """Check if the troop is still alive."""
        return self.hp > 0


@dataclass
class BattleState:
    """Consolidated state of the entire battle at a given tick."""

    tick: int
    time: float
    attacker_state: TroopState
    defender_state: TroopState
    is_finished: bool = False
    winner: str | None = None
    finish_reason: str | None = None
