from __future__ import annotations
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.graph import Graph, NodeId

INF = float("inf")


@dataclass(frozen=True)
class PathResult:
    cost: float
    path: List[NodeId]


def dijkstra(graph: Graph, start: NodeId, goal: NodeId) -> Optional[PathResult]:
    dist: Dict[NodeId, float] = {start: 0.0}
    prev: Dict[NodeId, Optional[NodeId]] = {start: None}
    pq: List[Tuple[float, NodeId]] = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d != dist.get(u, INF):
            continue
        if u == goal:
            return PathResult(cost=d, path=_reconstruct(prev, goal))

        for e in graph.neighbors(u):
            nd = d + e.cost
            if nd < dist.get(e.to, INF):
                dist[e.to] = nd
                prev[e.to] = u
                heapq.heappush(pq, (nd, e.to))

    return None


def _reconstruct(prev: Dict[NodeId, Optional[NodeId]], goal: NodeId) -> List[NodeId]:
    path: List[NodeId] = []
    cur: Optional[NodeId] = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path
