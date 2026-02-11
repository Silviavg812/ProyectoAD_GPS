from __future__ import annotations
from typing import Iterable, Protocol
from src.graph import Edge, NodeId


class GraphDAO(Protocol):
    def get_neighbors(self, node: NodeId) -> Iterable[Edge]:
        ...
