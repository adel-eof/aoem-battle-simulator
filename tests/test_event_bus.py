"""Tests for the Event Bus and battle event integration."""

import pytest

from aoemsim.engine.battle import BattleEngine
from aoemsim.engine.events import EventBus, EventPayload, EventType
from aoemsim.models.lineup import Lineup
from aoemsim.models.troop import Troop


@pytest.fixture
def event_bus():
    return EventBus()


def test_event_bus_subscribe_publish(event_bus):
    # Given a subscriber
    calls = []
    def subscriber(payload: EventPayload):
        calls.append(payload)

    event_bus.subscribe(EventType.BATTLE_START, subscriber)

    # When publishing an event
    payload = EventPayload(tick=0)
    event_bus.publish(EventType.BATTLE_START, payload)

    # Then subscriber is called
    assert len(calls) == 1
    assert calls[0] == payload


def test_event_bus_multiple_subscribers_order(event_bus):
    # Given multiple subscribers
    order = []
    event_bus.subscribe(EventType.TICK, lambda _: order.append(1))
    event_bus.subscribe(EventType.TICK, lambda _: order.append(2))

    # When publishing
    event_bus.publish(EventType.TICK, EventPayload(tick=1))

    # Then order is preserved
    assert order == [1, 2]


def test_battle_engine_events_integration():
    # Setup minimal battle
    attacker_lineup = Lineup(
        name="Attacker",
        commander_id="hero1",
        heroes=["hero1"],
        troop=Troop(unit_type="swordsman", size=100, unit_base_hp=10),
    )

    defender_lineup = Lineup(
        name="Defender",
        commander_id="hero2",
        heroes=["hero2"],
        troop=Troop(unit_type="swordsman", size=100, unit_base_hp=10),
    )

    engine = BattleEngine(
        attacker_lineup, defender_lineup, max_duration_sec=0.2, tick_sec=0.1
    )

    events_captured = []
    def capture(payload: EventPayload):
        events_captured.append(payload)

    engine.event_bus.subscribe(EventType.BATTLE_START, capture)
    engine.event_bus.subscribe(EventType.BATTLE_END, capture)
    engine.event_bus.subscribe(EventType.TICK, capture)

    # Run battle
    engine.run(seed=1)

    # Let's adjust capture to include type
    events_with_type = []
    def capture_with_type(etype):
        return lambda p: events_with_type.append((etype, p))

    engine.event_bus = EventBus() # Reset
    engine.event_bus.subscribe(EventType.BATTLE_START, capture_with_type(EventType.BATTLE_START))
    engine.event_bus.subscribe(EventType.BATTLE_END, capture_with_type(EventType.BATTLE_END))
    engine.event_bus.subscribe(EventType.TICK, capture_with_type(EventType.TICK))

    engine.run(seed=1)

    # Types should be in order
    event_types = [et for et, p in events_with_type]
    assert EventType.BATTLE_START in event_types
    assert EventType.TICK in event_types
    assert EventType.BATTLE_END in event_types
    assert event_types[0] == EventType.BATTLE_START
    assert event_types[-1] == EventType.BATTLE_END


def test_event_determinism():
    # Two identical runs should produce identical event sequences
    def get_event_sequence(seed):
        attacker_lineup = Lineup(
            name="Attacker",
            commander_id="h1",
            heroes=["h1"],
            troop=Troop(unit_type="swordsman", size=10, unit_base_hp=100),
        )

        defender_lineup = Lineup(
            name="Defender",
            commander_id="h2",
            heroes=["h2"],
            troop=Troop(unit_type="swordsman", size=10, unit_base_hp=100),
        )

        engine = BattleEngine(attacker_lineup, defender_lineup, max_duration_sec=0.3)
        sequence = []
        for etype in EventType:
            # Maintain a closure for etype
            def make_handler(et):
                return lambda p: sequence.append((et, p.tick, p.data))
            engine.event_bus.subscribe(etype, make_handler(etype))
        
        engine.run(seed)
        return sequence

    seq1 = get_event_sequence(42)
    seq2 = get_event_sequence(42)

    assert seq1 == seq2
