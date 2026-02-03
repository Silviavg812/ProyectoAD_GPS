from __future__ import annotations
from typing import Iterable

from src.graph import Edge, Graph, NodeId
from src.dao_interface import GraphDAO


class DAOGraphAdapter(Graph):
    """Adaptador: convierte un DAO (con DB) a un Graph usable por Dijkstra."""
    def __init__(self, dao: GraphDAO) -> None:
        self.dao = dao

    def neighbors(self, node: NodeId) -> Iterable[Edge]:
        return self.dao.get_neighbors(node)
