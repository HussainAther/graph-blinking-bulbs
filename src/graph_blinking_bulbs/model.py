from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Hashable, Iterable


class BulbState(str, Enum):
    OFF = "off"
    ON = "on"
    REFRACTORY = "refractory"


@dataclass
class _Node:
    state: BulbState = BulbState.OFF
    refractory_remaining: int = 0


@dataclass
class BulbGraph:
    """
    Deterministic synchronous graph of excitable "bulb" nodes.

    Rules for one time step:
      1. Every ON node sends one unit of excitation to each neighbor.
      2. OFF nodes with input >= threshold turn ON.
      3. ON nodes enter REFRACTORY state.
      4. REFRACTORY nodes count down toward OFF.

    The update is synchronous: all next states are computed from the
    same current-state snapshot.
    """

    adjacency: dict[Hashable, set[Hashable]]
    threshold: int = 1
    refractory_steps: int = 1
    nodes: dict[Hashable, _Node] = field(init=False)
    time: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.threshold < 1:
            raise ValueError("threshold must be >= 1")
        if self.refractory_steps < 0:
            raise ValueError("refractory_steps must be >= 0")

        # Defensive copy and symmetry check.
        self.adjacency = {
            node: set(neighbors) for node, neighbors in self.adjacency.items()
        }
        for node, neighbors in list(self.adjacency.items()):
            for neighbor in neighbors:
                self.adjacency.setdefault(neighbor, set()).add(node)

        self.nodes = {node: _Node() for node in self.adjacency}

    @classmethod
    def path(
        cls,
        n: int,
        *,
        threshold: int = 1,
        refractory_steps: int = 1,
    ) -> "BulbGraph":
        if n < 1:
            raise ValueError("n must be >= 1")
        adjacency = {i: set() for i in range(n)}
        for i in range(n - 1):
            adjacency[i].add(i + 1)
            adjacency[i + 1].add(i)
        return cls(adjacency, threshold=threshold, refractory_steps=refractory_steps)

    @classmethod
    def ring(
        cls,
        n: int,
        *,
        threshold: int = 1,
        refractory_steps: int = 1,
    ) -> "BulbGraph":
        if n < 3:
            raise ValueError("ring requires n >= 3")
        graph = cls.path(
            n,
            threshold=threshold,
            refractory_steps=refractory_steps,
        )
        graph.adjacency[0].add(n - 1)
        graph.adjacency[n - 1].add(0)
        return graph

    @classmethod
    def star(
        cls,
        leaves: int,
        *,
        threshold: int = 1,
        refractory_steps: int = 1,
    ) -> "BulbGraph":
        if leaves < 1:
            raise ValueError("leaves must be >= 1")
        adjacency = {0: set(range(1, leaves + 1))}
        for leaf in range(1, leaves + 1):
            adjacency[leaf] = {0}
        return cls(adjacency, threshold=threshold, refractory_steps=refractory_steps)

    def stimulate(self, *node_ids: Hashable) -> None:
        """Force one or more nodes ON at the current time."""
        for node_id in node_ids:
            self._require_node(node_id)
            node = self.nodes[node_id]
            node.state = BulbState.ON
            node.refractory_remaining = 0

    def reset(self) -> None:
        for node in self.nodes.values():
            node.state = BulbState.OFF
            node.refractory_remaining = 0
        self.time = 0

    def states(self) -> dict[Hashable, BulbState]:
        return {node_id: node.state for node_id, node in self.nodes.items()}

    def active_nodes(self) -> set[Hashable]:
        return {
            node_id
            for node_id, node in self.nodes.items()
            if node.state is BulbState.ON
        }

    def step(self) -> dict[Hashable, BulbState]:
        """Advance the simulation by one synchronous time step."""
        incoming = {node_id: 0 for node_id in self.nodes}

        for node_id, node in self.nodes.items():
            if node.state is BulbState.ON:
                for neighbor in self.adjacency[node_id]:
                    incoming[neighbor] += 1

        next_nodes: dict[Hashable, _Node] = {}

        for node_id, node in self.nodes.items():
            if node.state is BulbState.ON:
                if self.refractory_steps == 0:
                    next_nodes[node_id] = _Node(BulbState.OFF, 0)
                else:
                    next_nodes[node_id] = _Node(
                        BulbState.REFRACTORY,
                        self.refractory_steps,
                    )

            elif node.state is BulbState.REFRACTORY:
                remaining = node.refractory_remaining - 1
                if remaining <= 0:
                    next_nodes[node_id] = _Node(BulbState.OFF, 0)
                else:
                    next_nodes[node_id] = _Node(
                        BulbState.REFRACTORY,
                        remaining,
                    )

            else:  # OFF
                if incoming[node_id] >= self.threshold:
                    next_nodes[node_id] = _Node(BulbState.ON, 0)
                else:
                    next_nodes[node_id] = _Node(BulbState.OFF, 0)

        self.nodes = next_nodes
        self.time += 1
        return self.states()

    def run(self, steps: int) -> list[dict[Hashable, BulbState]]:
        if steps < 0:
            raise ValueError("steps must be >= 0")
        history = [self.states()]
        for _ in range(steps):
            history.append(self.step())
        return history

    def _require_node(self, node_id: Hashable) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id!r}")
