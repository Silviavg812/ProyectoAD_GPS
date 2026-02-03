from __future__ import annotations
import csv
from collections import defaultdict
from typing import DefaultDict, Iterable, List

from src.graph import Edge, NodeId


class CsvDAO:
    """DAO de prueba: lee aristas desde data/edges.csv (sin SQLite).
    Formato: origin,destination,cost
    """
    def __init__(self, edges_csv_path: str) -> None:
        self._adj: DefaultDict[NodeId, List[Edge]] = defaultdict(list)
        with open(edges_csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = int(row["origin"])
                v = int(row["destination"])
                cost = float(row["cost"])
                self._adj[u].append(Edge(to=v, cost=cost))

    def get_neighbors(self, node: NodeId) -> Iterable[Edge]:
        return self._adj.get(node, [])
