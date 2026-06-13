"""Tests for the Skill DSL and Effect Handler Registry."""

from unittest.mock import MagicMock

import pytest

from aoemsim.effects import register_default_handlers
from aoemsim.effects.registry import registry
from aoemsim.engine.rng import RngService
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import StatKind, UnitType
from aoemsim.models.lineup import Lineup
from aoemsim.models.skill import SkillEffect
from aoemsim.models.troop import Troop


@pytest.fixture(autouse=True)
def init_registry():
    register_default_handlers()


@pytest.fixture
def troop_attacker():
    lineup = Lineup(
        name="A",
        commander_id="h1",
        heroes=["h1"],
        troop=Troop(unit_type=UnitType.SWORDSMAN, size=100, unit_base_hp=10, unit_base_attack=10),
    )
    return TroopState(
        lineup=lineup,
        hp=1000.0,
        max_hp=1000.0,
        unit_type=UnitType.SWORDSMAN,
        stats_cache={StatKind.MIGHT: 0, StatKind.MAX_RAGE: 1000.0},
    )


@pytest.fixture
def troop_defender():
    lineup = Lineup(
        name="D",
        commander_id="h2",
        heroes=["h2"],
        troop=Troop(unit_type=UnitType.SWORDSMAN, size=100, unit_base_hp=10, unit_base_attack=10),
    )
    return TroopState(
        lineup=lineup,
        hp=1000.0,
        max_hp=1000.0,
        unit_type=UnitType.SWORDSMAN,
        stats_cache={StatKind.ARMOR: 0},
    )


def test_registry_execute_damage(troop_attacker, troop_defender):
    # Given a damage effect
    effect = SkillEffect(kind="damage", params={"rate": 10.0, "attack_stat": "might"})
    rng = RngService(seed=42)

    # When executing
    # 10.0 rate * 10 base atk = 100 damage = 10 troops loss.
    # 10 troops * 10 unit_hp = 100 HP loss.
    registry.execute(troop_attacker, troop_defender, effect, rng)

    # Then defender HP decreases
    assert troop_defender.hp < 1000.0
    assert troop_defender.hp == 900.0


def test_registry_execute_multiple_effects(troop_attacker, troop_defender):
    # Given compound effects
    # 1. Damage (100 HP)
    # 2. Rage Gain (50)
    e1 = SkillEffect(kind="damage", params={"rate": 10.0})
    e2 = SkillEffect(kind="rage_gain", params={"value": 50.0})
    
    rng = RngService(seed=42)
    
    # When executing
    registry.execute(troop_attacker, troop_defender, e1, rng)
    registry.execute(troop_attacker, troop_defender, e2, rng)
    
    # Then both effects applied
    assert troop_defender.hp == 900.0
    assert troop_attacker.rage == 50.0


def test_registry_fail_on_unknown_kind(troop_attacker, troop_defender):
    # Note: SkillEffect kind is validated by Pydantic Literals.
    # To test the registry's own check, we'd need to bypass Pydantic or 
    # use a kind that is in the Literal but not in the registry.
    # However, I registered all Literal kinds in register_default_handlers.
    # So this check in Registry is a safety net.
    
    # We'll mock SkillEffect to bypass Pydantic validation if we want to 
    # test the Registry's internal ValueError.
    mock_effect = MagicMock()
    mock_effect.kind = "unsupported_but_valid_literal_placeholder"
    rng = MagicMock()
    
    with pytest.raises(ValueError, match="Unsupported skill effect kind"):
        registry.execute(troop_attacker, troop_defender, mock_effect, rng)


def test_registry_rage_gain_cap(troop_attacker):
    # Given rage gain with cap
    effect = SkillEffect(kind="rage_gain", params={"value": 1200.0})
    rng = MagicMock()
    
    # When
    registry.execute(troop_attacker, None, effect, rng)
    
    # Then capped at MAX_RAGE (1000)
    assert troop_attacker.rage == 1000.0
