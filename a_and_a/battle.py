"""The logic around a battle"""
from typing import Mapping
from typing import Counter
from typing import Tuple
import collections
import enum

import a_and_a.units as a_units


class BattleMode(enum.Enum):
    """Whether one side is attacking or defending"""

    ATTACK = "ATTACK"
    DEFEND = "DEFEND"


def x_shift_counter(shift: int, counter: Counter[int]) -> Counter[int]:
    """Shifts the keys of a counter"""
    return collections.Counter({c + shift: val for c, val in counter})


def y_scale_counter(scale: int, counter: collections.Counter) -> Counter[int]:
    """Scales the values of a counter"""
    return collections.Counter({c: scale * val for c, val in counter})


def convolve_counters(a: Mapping[int, float], b: Mapping[int, float]) -> Counter[int]:
    """Convolves two counters"""
    result = collections.Counter()
    for a_c, a_v in a.items():
        for b_c, b_v in b.items():
            result[a_c + b_c] += a_v * b_v
    return result


def get_hits(mode: BattleMode, battlefield: str, *units: a_units.Unit) -> Counter[int]:
    """Returns a counter of the number of hits, with counts defining an
    empirical distribution"""
    del battlefield  # unused
    hits = collections.Counter({0: 1})
    for unit in units:
        if mode is BattleMode.ATTACK:
            new_hits = {
                0: 1 - unit.attack_strength,
                1: unit.attack_strength,
            }
        elif mode is BattleMode.DEFEND:
            new_hits = {
                0: 1 - unit.defense_strength,
                1: unit.defense_strength,
            }
        else:
            raise ValueError("Unrecognized Mode.")
        hits = convolve_counters(hits, new_hits)
    return hits


class LazyResult(dict):
    """A dictionary which can be used to cache results"""

    def __init__(self, result_constructor):
        super().__init__()
        self.result_constructor = result_constructor

    def __missing__(self, key):
        self[key] = self.result_constructor(self, key)
        return self[key]


def compute_battle_step(
    cache, setup: a_units.BattleSetup
) -> Counter[a_units.BattleSetup]:
    """Computes the next available steps after rolling the dice for one stage."""
    del cache  # unused
    if not setup.attackers or not setup.defenders:
        return collections.Counter({setup: 1})
    attack_hits = get_hits(BattleMode.ATTACK, setup.battlefield, *setup.attackers)
    defense_hits = get_hits(BattleMode.DEFEND, setup.battlefield, *setup.defenders)
    result = collections.Counter()
    for n_a_hits, n_a_count in attack_hits.items():
        new_defenders = take_cheapest_hits(n_a_hits, *setup.defenders)
        for n_d_hits, n_d_count in defense_hits.items():
            new_attackers = take_cheapest_hits(n_d_hits, *setup.attackers)
            new_setup = a_units.BattleSetup(
                battlefield=setup.battlefield,
                attackers=new_attackers,
                defenders=new_defenders,
            )
            if new_setup != setup:
                result[new_setup] += n_a_count * n_d_count
    # Readjust the counts to sum to 1.
    total = sum(result.values())
    if total != 1:
        result = collections.Counter({k: v / total for k, v in result.items()})
    return result


def take_cheapest_hits(n: int, *units: a_units.Unit) -> Tuple[a_units.Unit, ...]:
    """Takes the cheapest hit from the given units."""
    if n == 0 or not units:
        return tuple(units)
    cheapest_unit, *others = sorted(units, key=lambda unit: unit.hits_cost(1))
    hit_unit = cheapest_unit.take_hits(1)
    if hit_unit is None:
        return take_cheapest_hits(n - 1, *others)
    return take_cheapest_hits(n - 1, hit_unit, *others)


battle_steps = LazyResult(result_constructor=compute_battle_step)


def compute_battle_results(
    cache, setup: a_units.BattleSetup
) -> Counter[a_units.BattleSetup]:
    """Computes the likely scenarios for a battle setup, with counts of their occurrence."""
    final_result = collections.Counter()
    if not setup.attackers or not setup.defenders:
        final_result[setup] += 1
        return final_result
    next_results = battle_steps[setup]
    while next_results:
        next_setup = sorted(
            next_results,
            key=lambda setup_: -len(setup_.attackers) + -len(setup_.defenders),
        )[0]
        next_cnt = next_results.pop(next_setup)
        for final_setup, cnt in cache[next_setup].items():
            final_result[final_setup] += cnt * next_cnt
    return final_result


battle_results = LazyResult(result_constructor=compute_battle_results)
