"""Fixtures for tests"""
import pytest

import a_and_a.units as units


@pytest.fixture()
def fighter_unit():
    """A fighter unit"""
    return units.Unit(
        name="Fighter",
        ipc_value=10,
        attack_strength=0.5,
        defense_strength=2 / 3,
        required_hits=1,
    )


@pytest.fixture()
def infantry_unit():
    """A fighter unit"""
    return units.Unit(
        name="Infantry",
        ipc_value=3,
        attack_strength=1 / 6,
        defense_strength=1 / 3,
        required_hits=1,
    )


@pytest.fixture()
def transport_unit():
    """A fighter unit"""
    return units.Unit(
        name="Transport",
        ipc_value=7,
        attack_strength=0,
        defense_strength=0,
        required_hits=1,
    )


@pytest.fixture()
def tank_unit():
    """A fighter unit"""
    return units.Unit(
        name="Tank",
        ipc_value=6,
        attack_strength=0.5,
        defense_strength=0.5,
        required_hits=1,
    )
