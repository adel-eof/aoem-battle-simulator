"""Tests for rage accumulation and commander skill interrupt logic."""

import pytest

from aoemsim.engine.battle import BattleEngine
from aoemsim.engine.rage import should_interrupt_cast, update_rage
from aoemsim.engine.state import TroopState
from aoemsim.models.enums import SkillSlot, StatKind, TriggerType, UnitType
from aoemsim.models.hero import Hero
from aoemsim.models.lineup import Lineup
from aoemsim.models.skill import Skill, SkillTrigger
from aoemsim.models.stat import Stat
from aoemsim.models.troop import Troop


@pytest.fixture
def sample_hero():
    return Hero(
        id="test_hero",
        name="Test Hero",
        military="warrior",
        unit_types=[UnitType.SWORDSMAN],
        level=1,
        attributes={
            StatKind.MIGHT: Stat(base=100, growth=0),
            StatKind.RAGE_REGEN: Stat(base=100, growth=0),  # 100 rage per sec
            StatKind.MAX_RAGE: Stat(base=1000, growth=0),
        },
        skills={
            SkillSlot.COMMANDER: Skill(
                id="cmd_skill",
                name="Commander Skill",
                slot=SkillSlot.COMMANDER,
                trigger=SkillTrigger(type=TriggerType.ACTIVE),
                rage_cost=200,
            )
        },
    )


@pytest.fixture
def sample_lineup():
    return Lineup(
        name="Test Lineup",
        commander_id="test_hero",
        heroes=["test_hero"],
        troop=Troop(unit_type=UnitType.SWORDSMAN, size=100),
    )


def test_update_rage_logic(sample_hero, sample_lineup):
    """Test pure rage update logic."""
    state = TroopState(
        lineup=sample_lineup,
        hp=1000,
        max_hp=1000,
        unit_type=UnitType.SWORDSMAN,
        stats_cache={
            StatKind.RAGE_REGEN: 100.0,
            StatKind.MAX_RAGE: 1000.0,
        },
    )

    # 1 tick (0.1s) with 100/s regen = 10 rage
    update_rage(state, 0.1)
    assert state.rage == 10.0

    # Cap at max rage
    state.rage = 995.0
    update_rage(state, 0.1)
    assert state.rage == 1000.0


def test_should_interrupt_cast(sample_hero, sample_lineup):
    """Test interrupt condition detection."""
    skill = sample_hero.skills[SkillSlot.COMMANDER]
    state = TroopState(
        lineup=sample_lineup,
        hp=1000,
        max_hp=1000,
        unit_type=UnitType.SWORDSMAN,
        commander_skill=skill,
    )

    # Rage not enough
    state.rage = 150.0
    assert should_interrupt_cast(state) is None

    # Rage exactly enough
    state.rage = 200.0
    assert should_interrupt_cast(state) == skill

    # Rage more than enough
    state.rage = 250.0
    assert should_interrupt_cast(state) == skill


def test_battle_engine_integration(sample_hero, sample_lineup):
    """Test integration into BattleEngine tick loop."""
    # Rage cost 200, regen 100/s. Should take 2 seconds (20 ticks of 0.1s)
    engine = BattleEngine(
        attacker_lineup=sample_lineup,
        defender_lineup=sample_lineup,
        attacker_heroes=[sample_hero],
        defender_heroes=[sample_hero],
        max_duration_sec=3.0,
        tick_sec=0.1,
    )

    # Run simulation
    result = engine.run(seed=42)

    # The skill should have been cast.
    # In M3-001, we just record it in RNG history for now.
    # Cost is 200. At 2.0s, rage reaches 200.
    # Let's check if the cast event is in RNG history.
    cast_events = [e for e in result.rng_history if e.source == "cast_skill_cmd_skill"]
    assert len(cast_events) >= 1

    # Check that after cast, rage was reset.
    # Since BattleEngine doesn't return final states directly in BattleResult,
    # we might need to test the loop logic more granularly or trust the integration.
    # But wait, we can verify it by checking if it casts AGAIN.
    # 3 seconds total.
    # 0 -> 2.0s: Cast (Rage 200 -> 0)
    # 2.0s -> 3.0s: Rage reaches 100. Not enough for second cast.
    assert len(cast_events) == 2  # Wait, 2 lineages. Attacker and Defender.
    # So 1 cast per side.
    
    # If it was 5 seconds:
    # 0 -> 2.0s: Cast
    # 2.0s -> 4.0s: Cast
    # 4.0s -> 5.0s: Rage 100.
    # So 2 casts per side.
    
    engine_5s = BattleEngine(
        attacker_lineup=sample_lineup,
        defender_lineup=sample_lineup,
        attacker_heroes=[sample_hero],
        defender_heroes=[sample_hero],
        max_duration_sec=5.0,
        tick_sec=0.1,
    )
    result_5s = engine_5s.run(seed=42)
    cast_events_5s = [e for e in result_5s.rng_history if e.source == "cast_skill_cmd_skill"]
    # Total 4 events: 2 for attacker, 2 for defender.
    assert len(cast_events_5s) == 4
