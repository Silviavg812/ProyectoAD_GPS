from __future__ import annotations
from typing import Iterable, Protocol
from src.graph import Edge, NodeId


class GraphDAO(Protocol):
    """Tu compañero implementa esto con SQLite. Aquí solo la interfaz."""
    def get_neighbors(self, node: NodeId) -> Iterable[Edge]:
        ...
