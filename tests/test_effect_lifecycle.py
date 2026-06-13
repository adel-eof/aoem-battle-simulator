import pytest

from aoemsim.engine.effects_lifecycle import (
    apply_effect,
    apply_heal_with_cap,
    prune_expired_effects,
)
from aoemsim.engine.state import TroopState
from aoemsim.models.buff import BuffEffect
from aoemsim.models.enums import BuffStackPolicy, UnitType


@pytest.fixture
def mock_troop():
    from unittest.mock import MagicMock

    lineup = MagicMock()
    return TroopState(
        lineup=lineup,
        hp=1000.0,
        max_hp=1000.0,
        unit_type=UnitType.SWORDSMAN,
    )


def test_apply_heal_with_cap(mock_troop):
    mock_troop.hp = 800.0
    # Heal 300, should be capped at 1000 (actual heal 200)
    healed = apply_heal_with_cap(mock_troop, 300.0)
    assert healed == 200.0
    assert mock_troop.hp == 1000.0


def test_refresh_policy(mock_troop):
    effect = BuffEffect(
        id="test_buff", name="Test", duration_ticks=5, stack_policy=BuffStackPolicy.REFRESH
    )

    apply_effect(mock_troop, effect)
    assert len(mock_troop.active_effects) == 1
    assert mock_troop.active_effects[0].remaining_ticks == 5

    # Tick down
    prune_expired_effects(mock_troop)
    assert mock_troop.active_effects[0].remaining_ticks == 4

    # Re-apply, should refresh
    apply_effect(mock_troop, effect)
    assert len(mock_troop.active_effects) == 1
    assert mock_troop.active_effects[0].remaining_ticks == 5


def test_stack_policy(mock_troop):
    effect = BuffEffect(
        id="stack_buff",
        name="Stack",
        duration_ticks=5,
        stack_policy=BuffStackPolicy.STACK,
        max_stacks=3,
    )

    apply_effect(mock_troop, effect)
    assert mock_troop.active_effects[0].stacks == 1

    apply_effect(mock_troop, effect)
    assert mock_troop.active_effects[0].stacks == 2

    apply_effect(mock_troop, effect)
    assert mock_troop.active_effects[0].stacks == 3

    # Should not exceed max_stacks
    apply_effect(mock_troop, effect)
    assert mock_troop.active_effects[0].stacks == 3


def test_replace_if_stronger_policy(mock_troop):
    weak_effect = BuffEffect(
        id="stronger_buff",
        name="Stronger",
        value=10.0,
        duration_ticks=5,
        stack_policy=BuffStackPolicy.REPLACE_IF_STRONGER,
    )
    strong_effect = BuffEffect(
        id="stronger_buff",
        name="Stronger",
        value=20.0,
        duration_ticks=5,
        stack_policy=BuffStackPolicy.REPLACE_IF_STRONGER,
    )

    apply_effect(mock_troop, weak_effect)
    assert mock_troop.active_effects[0].config.value == 10.0

    # Apply weaker one again, should NOT replace
    apply_effect(
        mock_troop,
        BuffEffect(
            id="stronger_buff",
            name="W",
            value=5.0,
            duration_ticks=3,
            stack_policy=BuffStackPolicy.REPLACE_IF_STRONGER,
        ),
    )
    assert mock_troop.active_effects[0].config.value == 10.0

    # Apply stronger, SHOULD replace
    apply_effect(mock_troop, strong_effect)
    assert mock_troop.active_effects[0].config.value == 20.0


def test_independent_policy(mock_troop):
    effect = BuffEffect(
        id="indep", name="Indep", duration_ticks=5, stack_policy=BuffStackPolicy.INDEPENDENT
    )

    apply_effect(mock_troop, effect)
    apply_effect(mock_troop, effect)
    assert len(mock_troop.active_effects) == 2


def test_prune_expired(mock_troop):
    effect = BuffEffect(
        id="short", name="Short", duration_ticks=1, stack_policy=BuffStackPolicy.REFRESH
    )
    apply_effect(mock_troop, effect)
    assert len(mock_troop.active_effects) == 1

    prune_expired_effects(mock_troop)
    assert len(mock_troop.active_effects) == 0
