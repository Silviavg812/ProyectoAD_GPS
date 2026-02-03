from __future__ import annotations
import heapq
from typing import Dict, List, Optional, Set, Tuple

from src.graph import Graph, NodeId
from src.dijkstra import dijkstra, PathResult, INF


def route_with_stops(graph: Graph, origin: NodeId, stops: List[NodeId], destination: NodeId) -> Optional[PathResult]:
    """Calcula ruta pasando por 0 o más destinos intermedios."""
    full_path: List[NodeId] = []
    total_cost = 0.0

    sequence = [origin] + stops + [destination]
    for i in range(len(sequence) - 1):
        a, b = sequence[i], sequence[i + 1]
        res = dijkstra(graph, a, b)
        if res is None:
            return None

        total_cost += res.cost
        if not full_path:
            full_path.extend(res.path)
        else:
            full_path.extend(res.path[1:])  # evita repetir el nodo de unión

    return PathResult(cost=total_cost, path=full_path)


def choose_alternative_if_close(best: PathResult, alt: Optional[PathResult], threshold: float = 0.15) -> bool:
    """True si alt existe y está dentro del 15% (por defecto) respecto a best."""
    if alt is None:
        return False
    if best.cost <= 0:
        return False
    return alt.cost <= best.cost * (1.0 + threshold)


def second_shortest_path_yen(graph: Graph, start: NodeId, goal: NodeId) -> Optional[PathResult]:
    """Devuelve el segundo camino más corto (si existe) usando Yen (k=2)."""
    best = dijkstra(graph, start, goal)
    if best is None:
        return None

    A = [best.path]  # caminos aceptados (solo el mejor)
    B: List[Tuple[float, List[NodeId]]] = []

    for i in range(len(best.path) - 1):
        spur_node = best.path[i]
        root_path = best.path[: i + 1]

        blocked_edges: Set[tuple[int, int]] = set()
        for p in A:
            if len(p) > i and p[: i + 1] == root_path:
                blocked_edges.add((p[i], p[i + 1]))

        spur_res = _dijkstra_with_blocks(
            graph,
            spur_node,
            goal,
            blocked_edges=blocked_edges,
            blocked_nodes=set(root_path[:-1]),
        )
        if spur_res is None:
            continue

        total_path = root_path[:-1] + spur_res.path
        total_cost = _path_cost(graph, total_path)
        heapq.heappush(B, (total_cost, total_path))

    if not B:
        return None

    cost2, path2 = heapq.heappop(B)
    return PathResult(cost=cost2, path=path2)


def _path_cost(graph: Graph, path: List[NodeId]) -> float:
    cost = 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        found = False
        for e in graph.neighbors(u):
            if e.to == v:
                cost += e.cost
                found = True
                break
        if not found:
            raise ValueError(f"No existe arista {u}->{v}")
    return cost


def _dijkstra_with_blocks(
    graph: Graph,
    start: NodeId,
    goal: NodeId,
    blocked_edges: Set[tuple[int, int]],
    blocked_nodes: Set[NodeId],
) -> Optional[PathResult]:
    dist: Dict[NodeId, float] = {start: 0.0}
    prev: Dict[NodeId, NodeId | None] = {start: None}
    pq: List[Tuple[float, NodeId]] = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d != dist.get(u, INF):
            continue
        if u == goal:
            path: List[NodeId] = []
            cur: NodeId | None = goal
            while cur is not None:
                path.append(cur)
                cur = prev.get(cur)
            path.reverse()
            return PathResult(cost=d, path=path)

        for e in graph.neighbors(u):
            if (u, e.to) in blocked_edges:
                continue
            if e.to in blocked_nodes:
                continue
            nd = d + e.cost
            if nd < dist.get(e.to, INF):
                dist[e.to] = nd
                prev[e.to] = u
                heapq.heappush(pq, (nd, e.to))

    return None
