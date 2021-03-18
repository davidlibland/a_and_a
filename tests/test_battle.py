"""Tests for the battle logic"""
import pytest

import a_and_a.battle as battle
import a_and_a.units as units


def test_fighter_attack_get_hits(fighter_unit):
    """Tests that we get the correct number of hits for some basic units"""
    hits = battle.get_hits(battle.BattleMode.ATTACK, "air", fighter_unit)
    assert hits[0] == 0.5
    assert hits[1] == 0.5
    assert sum(hits.values()) == 1


def test_fighter_defence_get_hits(fighter_unit):
    """Tests that we get the correct number of hits for some basic units"""
    hits = battle.get_hits(battle.BattleMode.DEFEND, "air", fighter_unit)
    assert hits[0] == 1 - 2 / 3
    assert hits[1] == 2 / 3
    assert sum(hits.values()) == 1


def test_fighter_and_infantry_attack_get_hits(fighter_unit, infantry_unit):
    """Tests that we get the correct number of hits for some basic units"""
    hits = battle.get_hits(battle.BattleMode.ATTACK, "air", fighter_unit, infantry_unit)
    assert hits[0] == 3 * 5 / 36
    assert hits[1] == (3 * 5 + 3 * 1) / 36
    assert hits[2] == 3 / 36
    assert sum(hits.values()) == 1


@pytest.mark.parametrize(
    "a, b, c",
    [
        ({0: 1}, {0: 1}, {0: 1}),
        ({0: 1}, {2: 1}, {2: 1}),
        ({0: 1, 1: 1}, {2: 1}, {2: 1, 3: 1}),
        ({0: 1, 1: 1}, {2: 1, 1: 1}, {1: 1, 2: 2, 3: 1}),
    ],
)
def test_convolve(a, b, c):
    """Test that the convolutions are correct"""
    assert dict(battle.convolve_counters(a, b)) == dict(c)


def test_battle_steps_simple(infantry_unit, fighter_unit):
    """Tests the next step of a battle with one unit is correct"""
    setup = units.BattleSetup(
        battlefield="land", attackers=(infantry_unit,), defenders=(fighter_unit,)
    )
    next_steps = battle.battle_steps[setup]
    assert len(next_steps) == 3
    assert is_close(sum(next_steps.values()), 1)
    assert is_close(
        next_steps[
            units.BattleSetup(
                battlefield="land", attackers=(infantry_unit,), defenders=()
            )
        ],
        1 * 2 / 36,
    )
    assert is_close(
        next_steps[
            units.BattleSetup(
                battlefield="land", attackers=(), defenders=(fighter_unit,)
            )
        ],
        5 * 4 / 36,
    )
    assert is_close(
        next_steps[units.BattleSetup(battlefield="land", attackers=(), defenders=())],
        1 * 4 / 36,
    )


def test_battle_steps_two_units(infantry_unit, fighter_unit):
    """Tests the next step of a battle with two units is correct"""
    setup = units.BattleSetup(
        battlefield="land",
        attackers=(infantry_unit, infantry_unit),
        defenders=(fighter_unit, fighter_unit),
    )
    next_steps = battle.battle_steps[setup]
    assert len(next_steps) == 8
    assert is_close(sum(next_steps.values()), 1)
    assert is_close(
        next_steps[
            units.BattleSetup(
                battlefield="land",
                attackers=(infantry_unit, infantry_unit),
                defenders=(),
            )
        ],
        1 * 1 * 2 * 2 / 36 ** 2,
    )
    assert is_close(
        next_steps[
            units.BattleSetup(
                battlefield="land",
                attackers=(infantry_unit,),
                defenders=(fighter_unit,),
            )
        ],
        2 * 5 * 2 * 4 * 2 / 36 ** 2,
    )
    assert is_close(
        next_steps[
            units.BattleSetup(
                battlefield="land", attackers=(), defenders=(fighter_unit, fighter_unit)
            )
        ],
        5 * 5 * 4 * 4 / 36 ** 2,
    )
    assert is_close(
        next_steps[units.BattleSetup(battlefield="land", attackers=(), defenders=())],
        1 * 1 * 4 * 4 / 36 ** 2,
    )


def test_battle_simple(infantry_unit, fighter_unit):
    """tests a battle with one unit on each side"""
    setup = units.BattleSetup(
        battlefield="land", attackers=(infantry_unit,), defenders=(fighter_unit,)
    )
    results = battle.battle_results[setup]
    assert len(results) == 3
    assert is_close(
        results[
            units.BattleSetup(
                battlefield="land", attackers=(infantry_unit,), defenders=()
            )
        ],
        1 * 2 / 26,
    )
    assert is_close(
        results[
            units.BattleSetup(
                battlefield="land", attackers=(), defenders=(fighter_unit,)
            )
        ],
        5 * 4 / 26,
    )
    assert is_close(
        results[units.BattleSetup(battlefield="land", attackers=(), defenders=())],
        1 * 4 / 26,
    )


def test_battle_two_units(infantry_unit, fighter_unit):
    """Tests a battle with two units"""
    setup = units.BattleSetup(
        battlefield="land",
        attackers=(infantry_unit, infantry_unit),
        defenders=(fighter_unit, fighter_unit),
    )
    results = battle.battle_results[setup]
    assert len(results) == 1 + 2 + 2
    assert sorted(results, key=results.__getitem__)[-1].attackers == ()
    assert sorted(results, key=results.__getitem__)[-2].attackers == ()
    assert sorted(results, key=results.__getitem__)[-3].attackers == ()
    assert sorted(results, key=results.__getitem__)[-3].defenders == ()
    assert sorted(results, key=results.__getitem__)[-4].defenders == ()
    assert sorted(results, key=results.__getitem__)[-5].defenders == ()


def test_battle_cost(infantry_unit, fighter_unit):
    """Tests a battle with two units to get the expect costs."""
    setup = units.BattleSetup(
        battlefield="land",
        attackers=(infantry_unit, infantry_unit),
        defenders=(fighter_unit, fighter_unit),
    )
    costs = battle.get_expected_costs(setup)
    assert 0 < costs["attacker"] < setup.attacker_ipc
    assert 0 < costs["defender"] < setup.defender_ipc


def test_battle_odds(infantry_unit, fighter_unit):
    """Tests a battle with two units to get the expect costs."""
    setup = units.BattleSetup(
        battlefield="land",
        attackers=(infantry_unit, infantry_unit),
        defenders=(fighter_unit, fighter_unit),
    )
    odds = battle.get_winning_odds(setup)
    assert 0 < odds["attacker"] < 1
    assert 0 < odds["defender"] < 1
    assert 0 < odds["draw"] < 1
    assert is_close(sum(odds.values()), 1)


def test_clear_battle_odds(transport_unit, fighter_unit):
    """Tests a battle with two units to get the expect costs."""
    setup = units.BattleSetup(
        battlefield="land",
        attackers=(fighter_unit, fighter_unit),
        defenders=(transport_unit, transport_unit),
    )
    odds = battle.get_winning_odds(setup)
    assert odds["attacker"] == 1
    assert odds["defender"] == 0
    assert odds["draw"] == 0

    setup = units.BattleSetup(
        battlefield="land",
        attackers=(transport_unit, transport_unit),
        defenders=(transport_unit,),
    )
    odds = battle.get_winning_odds(setup)
    assert odds["attacker"] == 0
    assert odds["defender"] == 0
    assert odds["draw"] == 1


def is_close(a, b):
    """Checks if two values are close"""
    return abs(a - b) < 1e5
