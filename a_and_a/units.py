"""Unit types"""
from typing import Tuple
from typing import Optional
import dataclasses

UNIT_YAML_TAG = u"!Unit"


@dataclasses.dataclass(frozen=True, eq=True, order=True)
class Unit:
    """A basic unit type"""

    name: str
    """The name of the unit"""
    ipc_value: int
    """The ipc cost of the unit"""
    attack_strength: float
    """Odds of rolling a hit when attacking"""
    defense_strength: float
    """Odds of rolling a hit when defending"""
    required_hits: int
    """How many hits it takes to destroy the unit"""
    current_hits: int = 0
    """The number of hits the unit currently has"""

    def __post_init__(self):
        if not 0 <= self.attack_strength <= 1:
            raise ValueError("Invalid attack strength")
        if not 0 <= self.defense_strength <= 1:
            raise ValueError("Invalid defense strength")

    @property
    def non_combatant(self):
        """Is a non_combatant"""
        return self.attack_strength == 0 and self.defense_strength == 0

    def take_hits(self, n=1) -> Optional["Unit"]:
        """The result of the unit taking n hits, None if killed"""
        new_hits = self.current_hits + n
        if new_hits == self.required_hits:
            return None
        elif new_hits > self.required_hits:
            raise ValueError("Too many hits")
        return dataclasses.replace(self, current_hits=new_hits)

    def hits_cost(self, n=1) -> int:
        """Returns the ipc cost of this unit sustaining n hits."""
        if self.current_hits + n >= self.required_hits:
            return self.ipc_value
        return 0

    @staticmethod
    def yaml_representer(dumper, data):
        """Represent the data as yaml"""
        return dumper.represent_mapping(UNIT_YAML_TAG, dataclasses.asdict(data))

    @staticmethod
    def yaml_constructor(loader, node):
        """Build a Unit from yaml"""
        value = loader.construct_mapping(node)
        return Unit(**value)


@dataclasses.dataclass(frozen=True, eq=True)
class BattleSetup:
    """The setup for a battle."""

    battlefield: str
    """The location of the battle"""
    attackers: Tuple[Unit, ...]
    """The attackers"""
    defenders: Tuple[Unit, ...]
    """The defenders"""

    def __post_init__(self):
        """Some validation and normalization"""
        object.__setattr__(self, "attackers", tuple(sorted(self.attackers)))
        object.__setattr__(self, "defenders", tuple(sorted(self.defenders)))

    @property
    def attacker_ipc(self):
        """The combined ipc value of the attackers"""
        return sum(a.ipc_value for a in self.attackers)

    @property
    def defender_ipc(self):
        """The combined ipc value of the defenders"""
        return sum(a.ipc_value for a in self.defenders)


fighter = Unit(
    name="Fighter",
    ipc_value=10,
    attack_strength=0.5,
    defense_strength=2 / 3,
    required_hits=1,
)

bomber = Unit(
    name="Bomber",
    ipc_value=12,
    attack_strength=2 / 3,
    defense_strength=1 / 6,
    required_hits=1,
)

infantry = Unit(
    name="Infantry",
    ipc_value=3,
    attack_strength=1 / 6,
    defense_strength=1 / 3,
    required_hits=1,
)

tank = Unit(
    name="Tank",
    ipc_value=6,
    attack_strength=0.5,
    defense_strength=0.5,
    required_hits=1,
)

destroyer = Unit(
    name="Destroyer",
    ipc_value=8,
    attack_strength=1 / 3,
    defense_strength=1 / 3,
    required_hits=1,
)

transport = Unit(
    name="Transport",
    ipc_value=7,
    attack_strength=0,
    defense_strength=0,
    required_hits=1,
)

submarine = Unit(
    name="Submarine",
    ipc_value=6,
    attack_strength=1 / 3,
    defense_strength=1 / 6,
    required_hits=1,
)

aircraft_carrier = Unit(
    name="Aircraft Carrier",
    ipc_value=12,
    attack_strength=1 / 6,
    defense_strength=1 / 3,
    required_hits=1,
)

battleship = Unit(
    name="Battleship",
    ipc_value=16,
    attack_strength=2 / 3,
    defense_strength=2 / 3,
    required_hits=2,
)
