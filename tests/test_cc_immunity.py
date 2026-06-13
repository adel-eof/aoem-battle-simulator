"""Tests for Crowd Control and Immunity mechanics."""

from unittest.mock import MagicMock

import pytest

from aoemsim.engine.cc import (
    apply_cc,
    is_disarmed,
    is_incapacitated,
    is_silenced,
    update_cc_timers,
)
from aoemsim.engine.damage import resolve_damage
from aoemsim.engine.rage import should_interrupt_cast
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import CcType, SkillSlot, StatKind, TriggerType, UnitType
from aoemsim.models.skill import Skill, SkillEffect, SkillTrigger


@pytest.fixture
def troop():
    lineup = MagicMock()
    lineup.troop.unit_base_attack = 100.0
    lineup.troop.unit_base_hp = 100.0
    
    return TroopState(
        lineup=lineup,
        hp=1000.0,
        max_hp=1000.0,
        unit_type=UnitType.SWORDSMAN,
        stats_cache={
            StatKind.MIGHT: 100.0,
            StatKind.ARMOR: 100.0,
            StatKind.RAGE_REGEN: 10.0,
            StatKind.MAX_RAGE: 1000.0,
        },
    )


def test_silence_blocks_active_skill(troop):
    # Given troop is silenced
    apply_cc(troop, CcType.SILENCE, 10)
    assert is_silenced(troop)

    # When evaluating active skill
    trigger = SkillTrigger(type=TriggerType.ACTIVE)
    troop.commander_skill = Skill(
        id="test_skill",
        name="Test",
        rage_cost=100,
        slot=SkillSlot.COMMANDER,
        trigger=trigger,
    )
    troop.rage = 200
    
    # Then should_interrupt_cast returns None
    assert should_interrupt_cast(troop) is None


def test_disarm_guard_evaluates_true(troop):
    # Given troop is disarmed
    apply_cc(troop, CcType.DISARM, 10)
    # Then is_disarmed should be true
    assert is_disarmed(troop)


def test_incapacitation_makes_damage_zero(troop):
    # Given troop is incapacitated
    apply_cc(troop, CcType.INCAPACITATION, 10)
    assert is_incapacitated(troop)

    # When resolving damage
    defender = MagicMock(spec=TroopState)
    defender.hp = 1000.0
    effect = SkillEffect(kind="damage", params={"rate": 1.0, "attack_stat": "might"})
    rng = MagicMock()
    
    damage = resolve_damage(troop, defender, effect, rng)
    
    # Then damage should be 0
    assert damage == 0


def test_cc_immunity_flow(troop):
    # 1. Apply CC
    duration = 10
    immunity_duration = 30 # 3 seconds if tick is 0.1
    apply_cc(troop, CcType.SILENCE, duration)
    assert is_silenced(troop)
    
    # 2. Progress ticks until CC ends
    for _ in range(duration):
        update_cc_timers(troop, immunity_duration)
    
    # 3. CC should be gone, and immunity should be active
    assert not is_silenced(troop)
    assert troop.cc_immunity_timers[CcType.SILENCE] == immunity_duration
    
    # 4. Try to re-apply same CC during immunity
    applied = apply_cc(troop, CcType.SILENCE, 10)
    assert not applied
    assert not is_silenced(troop)
    
    # 5. Progress ticks until immunity ends
    for _ in range(immunity_duration):
        update_cc_timers(troop, immunity_duration)
        
    assert CcType.SILENCE not in troop.cc_immunity_timers
    
    # 6. Apply again - should work now
    applied = apply_cc(troop, CcType.SILENCE, 10)
    assert applied
    assert is_silenced(troop)


def test_different_cc_types_timers_independent(troop):
    # Apply Silence
    apply_cc(troop, CcType.SILENCE, 10)
    # Apply Disarm
    apply_cc(troop, CcType.DISARM, 5)
    
    assert is_silenced(troop)
    assert is_disarmed(troop)
    
    # Pass 6 ticks
    for _ in range(6):
        update_cc_timers(troop, 30)
        
    assert is_silenced(troop)
    assert not is_disarmed(troop)
    assert troop.cc_immunity_timers[CcType.DISARM] == 30 - 1 # One tick of immunity already passed
