from __future__ import annotations
from typing import List

from src.graph_from_dao import DAOGraphAdapter
from src.routing import route_with_stops, second_shortest_path_yen, choose_alternative_if_close
from src.csv_dao import CsvDAO


def parse_nodes_list(text: str) -> List[int]:
    text = text.strip()
    if not text:
        return []
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def main() -> None:
    
    dao = CsvDAO("data/edges_laberinto.csv")

    graph = DAOGraphAdapter(dao)

    origin = int(input("Origen (id): "))
    destination = int(input("Destino (id): "))
    stops = parse_nodes_list(input("Intermedios (ids separados por coma, vacío si ninguno): "))

    best = route_with_stops(graph, origin, stops, destination)
    if best is None:
        print("No existe ruta posible.")
        return

    print("Ruta óptima:")
    print("Coste:", best.cost)
    print("Camino:", " -> ".join(map(str, best.path)))

    # Alternativa solo cuando NO hay intermedios 
    if not stops:
        alt = second_shortest_path_yen(graph, origin, destination)
        if choose_alternative_if_close(best, alt, 0.15):
            print("Alternativa dentro del 15%:")
            print("Coste:", alt.cost)
            print("Camino:", " -> ".join(map(str, alt.path)))
            choice = input("¿Quieres la alternativa? (s/n): ").strip().lower()
            if choice == "s":
                print("Elegida alternativa.")
        else:
            print("\n(No hay alternativa válida dentro del 15%.)")


if __name__ == "__main__":
    main()
