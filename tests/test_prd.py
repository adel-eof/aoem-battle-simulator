from aoemsim.engine.prd import PrdEngine


def test_prd_determinism():
    """Given seed and urutan aksi identik, When battle diulang, Then hasil trigger PRD identik."""
    engine1 = PrdEngine()
    engine2 = PrdEngine()
    
    skill_id = "test_skill"
    base_chance = 0.2
    
    # Roll 10 times with identical rolls
    rolls = [0.1, 0.9, 0.05, 0.5, 0.1, 0.2, 0.8, 0.01, 0.4, 0.1]
    
    results1 = [engine1.evaluate_trigger(skill_id, base_chance, r) for r in rolls]
    results2 = [engine2.evaluate_trigger(skill_id, base_chance, r) for r in rolls]
    
    assert results1 == results2

def test_prd_accumulation():
    """
    Given skill active dengan base chance tertentu,
    When trigger dievaluasi berulang,
    Then evaluasi menggunakan state PRD per skill.
    """
    engine = PrdEngine()
    skill_id = "test_accumulation"
    base_chance = 0.1
    
    # In PRD, if we keep failing, the chance should increase.
    # Our simple placeholder uses C * (fail_count + 1)
    # With base_chance 0.1, C is 0.01 (0.1 * 0.1)
    # Roll 0.05 should fail first time (0.05 < 0.01 is False)
    # But pass later after enough fails.
    
    # 1st roll: chance 0.01. roll 0.05 -> False. fail_count = 1
    assert engine.evaluate_trigger(skill_id, base_chance, 0.05) is False
    
    # 2nd roll: chance 0.01 * 2 = 0.02. roll 0.05 -> False. fail_count = 2
    assert engine.evaluate_trigger(skill_id, base_chance, 0.05) is False
    
    # 3rd roll: chance 0.01 * 3 = 0.03. roll 0.05 -> False. fail_count = 3
    assert engine.evaluate_trigger(skill_id, base_chance, 0.05) is False
    
    # 4th roll: chance 0.01 * 4 = 0.04. roll 0.05 -> False. fail_count = 4
    assert engine.evaluate_trigger(skill_id, base_chance, 0.05) is False
    
    # 5th roll: chance 0.01 * 5 = 0.05. roll 0.049 -> True (success!)
    assert engine.evaluate_trigger(skill_id, base_chance, 0.049) is True
    
    # 6th roll: reset! chance 0.01. roll 0.05 -> False.
    assert engine.evaluate_trigger(skill_id, base_chance, 0.05) is False

def test_prd_per_skill_isolation():
    """State PRD dilacak terpisah per skill."""
    engine = PrdEngine()
    
    # Skill A fails repeatedly
    engine.evaluate_trigger("A", 0.1, 0.9)
    engine.evaluate_trigger("A", 0.1, 0.9)
    
    assert engine.get_state("A").fail_count == 2
    assert engine.get_state("B").fail_count == 0
