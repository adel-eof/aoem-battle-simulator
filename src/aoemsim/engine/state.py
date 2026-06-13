"""Runtime state for battle simulation."""

from dataclasses import dataclass, field


@dataclass
class TroopState:
    """Runtime state of a troop in battle."""

    hp: float
    max_hp: float
    rage: float = 0.0
    effects: list[str] = field(default_factory=list)
    cooldowns: dict[str, float] = field(default_factory=dict)

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
