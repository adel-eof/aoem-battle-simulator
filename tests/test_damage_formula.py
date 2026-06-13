"""Tests for the base damage formula implementation."""

from unittest.mock import MagicMock

import pytest

from aoemsim.engine.damage import (
    compute_attack_stat,
    compute_counter_multiplier,
    compute_defense_multiplier,
    compute_troop_loss,
    resolve_damage,
)
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import StatKind, UnitType
from aoemsim.models.skill import SkillEffect


@pytest.fixture
def mock_rng():
    return RngService(seed=42)


@pytest.fixture
def attacker_state():
    lineup = MagicMock()
    lineup.troop.unit_base_attack = 100.0
    lineup.troop.unit_base_hp = 1000.0

    return TroopState(
        lineup=lineup,
        hp=130000.0,
        max_hp=130000.0,
        unit_type=UnitType.SWORDSMAN,
        stats_cache={
            StatKind.MIGHT: 100.0,
            StatKind.ARMOR: 100.0,
        },
    )


@pytest.fixture
def defender_state():
    lineup = MagicMock()
    lineup.troop.unit_base_attack = 100.0
    lineup.troop.unit_base_hp = 1000.0

    return TroopState(
        lineup=lineup,
        hp=130000.0,
        max_hp=130000.0,
        unit_type=UnitType.PIKEMAN,  # Swordsman counters Pikeman
        stats_cache={
            StatKind.MIGHT: 100.0,
            StatKind.ARMOR: 100.0,
        },
    )


def test_compute_counter_multiplier():
    # Swordsman counters Pikeman (+30%)
    assert compute_counter_multiplier(UnitType.SWORDSMAN, UnitType.PIKEMAN) == 1.30
    # Pikeman counters Cavalry (+30%)
    assert compute_counter_multiplier(UnitType.PIKEMAN, UnitType.CAVALRY) == 1.30
    # Cavalry counters Archer (+30%)
    assert compute_counter_multiplier(UnitType.CAVALRY, UnitType.ARCHER) == 1.30
    # Archer counters Swordsman (+30%)
    assert compute_counter_multiplier(UnitType.ARCHER, UnitType.SWORDSMAN) == 1.30
    # Same type (no bonus)
    assert compute_counter_multiplier(UnitType.SWORDSMAN, UnitType.SWORDSMAN) == 1.00
    # Non-counter type
    assert compute_counter_multiplier(UnitType.SWORDSMAN, UnitType.ARCHER) == 1.00


def test_compute_attack_stat():
    # 100 base * (1 + 0.0015 * 100) = 100 * 1.15 = 115
    assert pytest.approx(compute_attack_stat(100.0, 100.0)) == 115.0
    # 200 base * (1 + 0.0015 * 0) = 200
    assert pytest.approx(compute_attack_stat(200.0, 0.0)) == 200.0


def test_compute_defense_multiplier():
    # 1 / (1 + 0.0015 * 100) = 1 / 1.15 = 0.869565...
    assert pytest.approx(compute_defense_multiplier(100.0)) == 1.0 / 1.15


def test_compute_troop_loss():
    # floor(2500 / 1000) = 2
    assert compute_troop_loss(2500.0, 1000.0) == 2
    # floor(999.9 / 1000) = 0
    assert compute_troop_loss(999.9, 1000.0) == 0
    # floor(1000.0 / 1000) = 1
    assert compute_troop_loss(1000.0, 1000.0) == 1


def test_resolve_damage_numerical_match(attacker_state, defender_state, mock_rng):
    # Setup:
    # Attacker: Might 100, Base Atk 100 -> Eff Atk 115
    # Defender: Armor 100 -> Def Mult 1/1.15
    # Counter: Swordsman vs Pikeman -> 1.30
    # Skill: Rate 1.0, Might bonus 100 -> Skill Rate 1.0 * (1 + 0.0030 * 100) = 1.3
    # Troop Scaling: 1.0 (Full HP)
    # Variance: (Using Seed 42, we know the value or can mock it)

    effect = SkillEffect(
        kind="damage", params={"rate": 1.0, "attack_stat": "might", "bonus": "might"}
    )

    # Let's mock RNG to return 1.0 for variance to make it deterministic for this test
    mock_rng.uniform = MagicMock(return_value=1.0)

    # Expected:
    # atk_stat = 100 * (1 + 0.0015 * 100) = 115
    # skill_rate = 1.0 * (1 + 0.0030 * 100) = 1.3
    # raw_dmg = 115 * 1.3 = 149.5
    # def_mult = 1 / 1.15
    # counter_mult = 1.3
    # scaling = 1.0
    # variance = 1.0
    # final_float = 149.5 * (1/1.15) * 1.3 * 1.0 * 1.0 = 130 * 1.3 = 169.0
    # troop_loss = floor(169.0 / 1000.0) = 0

    loss = resolve_damage(attacker_state, defender_state, effect, mock_rng)
    assert loss == 0

    # Try with higher damage to see actual loss
    effect.params["rate"] = 10.0
    # skill_rate = 10.0 * 1.3 = 13
    # raw = 115 * 13 = 1495
    # final = 1495 * (1/1.15) * 1.3 = 1300 * 1.3 = 1690
    # loss = floor(1690 / 1000) = 1
    loss = resolve_damage(attacker_state, defender_state, effect, mock_rng)
    assert loss == 1


def test_resolve_damage_troop_scaling(attacker_state, defender_state, mock_rng):
    attacker_state.hp = attacker_state.max_hp * 0.5  # 50% HP
    mock_rng.uniform = MagicMock(return_value=1.0)

    effect = SkillEffect(kind="damage", params={"rate": 20.0, "attack_stat": "might"})

    # Scaling 1.0:
    # raw = 20 * 115 = 2300
    # final = 2300 * (1/1.15) * 1.3 = 2000 * 1.3 = 2600 -> loss 2

    # Scaling 0.5:
    # final = 2600 * 0.5 = 1300 -> loss 1

    loss = resolve_damage(attacker_state, defender_state, effect, mock_rng)
    assert loss == 1


def test_resolve_damage_variance_range(attacker_state, defender_state, mock_rng):
    effect = SkillEffect(kind="damage", params={"rate": 100.0, "attack_stat": "might"})

    # Base damage around 13000
    # With variance 0.95: 12350 -> 12 units
    # With variance 1.05: 13650 -> 13 units

    losses = []
    for i in range(50):
        losses.append(resolve_damage(attacker_state, defender_state, effect, RngService(seed=i)))

    assert all(loss >= 12 for loss in losses)
    assert all(loss <= 13 for loss in losses)
