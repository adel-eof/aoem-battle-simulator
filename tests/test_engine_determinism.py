"""Tests for battle engine determinism and core loop logic."""

import pytest

from aoemsim.engine.battle import BattleEngine
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import UnitType
from aoemsim.models.lineup import Lineup
from aoemsim.models.troop import Troop


@pytest.fixture
def sample_lineup_a():
    """Create a sample lineup for testing."""
    return Lineup(
        name="Team A",
        commander_id="hero1",
        heroes=["hero1", "hero2", "hero3"],
        troop=Troop(unit_type=UnitType.SWORDSMAN, size=100, unit_base_hp=10.0),
    )


@pytest.fixture
def sample_lineup_b():
    """Create another sample lineup for testing."""
    return Lineup(
        name="Team B",
        commander_id="hero4",
        heroes=["hero4", "hero5", "hero6"],
        troop=Troop(unit_type=UnitType.ARCHER, size=100, unit_base_hp=10.0),
    )


def test_battle_determinism(sample_lineup_a, sample_lineup_b):
    """Test that the battle produces identical results for the same seed."""
    engine = BattleEngine(sample_lineup_a, sample_lineup_b)
    seed = 12345

    result1 = engine.run(seed)
    result2 = engine.run(seed)

    assert result1.winner == result2.winner
    assert result1.duration_ticks == result2.duration_ticks
    assert result1.duration_sec == result2.duration_sec
    assert result1.finish_reason == result2.finish_reason
    assert result1.attacker_final_hp == result2.attacker_final_hp
    assert result1.defender_final_hp == result2.defender_final_hp
    assert result1.rng_history == result2.rng_history


def test_battle_different_seeds(sample_lineup_a, sample_lineup_b):
    """Test that different seeds produce different RNG histories."""
    engine = BattleEngine(sample_lineup_a, sample_lineup_b)

    result1 = engine.run(111)
    result2 = engine.run(222)

    assert result1.rng_history != result2.rng_history


def test_battle_timeout(sample_lineup_a, sample_lineup_b):
    """Test that battle ends with timeout if no one dies."""
    # Max duration 1 second = 10 ticks
    engine = BattleEngine(sample_lineup_a, sample_lineup_b, max_duration_sec=1.0)
    result = engine.run(42)

    assert result.finish_reason == "timeout"
    assert result.duration_ticks == 10
    assert result.duration_sec == 1.0
    assert result.winner is None


class DamagingBattleEngine(BattleEngine):
    """Test engine that applies damage every tick."""

    def _process_tick(
        self, tick: int, attacker: TroopState, defender: TroopState, rng: RngService
    ) -> None:
        super()._process_tick(tick, attacker, defender, rng)
        # Apply 200 damage to defender every tick
        defender.hp -= 200


def test_battle_termination_on_hp_zero(sample_lineup_a, sample_lineup_b):
    """Test that battle stops immediately when a troop reaches HP <= 0."""
    # Team B has 100 * 10 = 1000 HP
    # DamagingBattleEngine deals 200 damage/tick
    # It should take 5 ticks to reach 0 HP.
    engine = DamagingBattleEngine(sample_lineup_a, sample_lineup_b, max_duration_sec=10.0)
    result = engine.run(42)

    assert result.finish_reason == "victory"
    assert result.winner == "Team A"
    assert result.duration_ticks == 5
    assert result.defender_final_hp == 0.0
