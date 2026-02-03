from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, List, Protocol

NodeId = int

@dataclass(frozen=True)
class Edge:
    to: NodeId
    cost: float  # no negativo


class Graph(Protocol):
    """Interfaz mínima del grafo para Dijkstra (sin SQL ni UI)."""
    def neighbors(self, node: NodeId) -> Iterable[Edge]:
        ...


class AdjacencyListGraph:
    """Grafo dirigido ponderado en memoria."""
    def __init__(self) -> None:
        self._adj: Dict[NodeId, List[Edge]] = {}

    def add_node(self, node: NodeId) -> None:
        self._adj.setdefault(node, [])

    def add_edge(self, u: NodeId, v: NodeId, cost: float) -> None:
        if cost < 0:
            raise ValueError("El coste no puede ser negativo")
        self.add_node(u)
        self.add_node(v)
        self._adj[u].append(Edge(v, float(cost)))

    def neighbors(self, node: NodeId) -> Iterable[Edge]:
        return self._adj.get(node, [])
