from __future__ import annotations
from typing import List, Optional

from src.graph_from_dao import DAOGraphAdapter
from src.routing import route_with_stops, second_shortest_path_yen, choose_alternative_if_close
from src.sqlite_dao import SqliteDAO
from src.dijkstra import PathResult


def parse_nodes_list(text: str) -> List[int]:
    """Parsea una lista de nodos separados por comas."""
    text = text.strip()
    if not text:
        return []
    return [int(x.strip()) for x in text.split(",") if x.strip()]



def main() -> None:
    print("=" * 50)
    print("     SIMULADOR GPS - ALGORITMO DE DIJKSTRA")
    print("=" * 50)
    print()
    
    # Inicializar DAO con SQLite
    dao = SqliteDAO("data/gps.db")
    
    # Cargar CSV en la base de datos (solo primera vez o si está vacía)
    print("📂 Cargando datos desde CSV a SQLite...")
    dao.cargar_desde_csv("data/edges_laberinto.csv")
    print("✅ Base de datos cargada correctamente.\n")
    
    # Crear adaptador del grafo
    graph = DAOGraphAdapter(dao)
    
    # Pedir datos al usuario con validación
    try:
        origin = int(input("🚩 Origen (id del nodo): "))
        destination = int(input("🏁 Destino (id del nodo): "))
        stops_input = input("📍 Nodos intermedios (separados por coma, Enter si ninguno): ")
        stops = parse_nodes_list(stops_input)
    except ValueError:
        print("❌ Error: Debes introducir números enteros válidos.")
        return
    
    print()
    print("-" * 50)
    
    # VERIFICAR HISTÓRICO PRIMERO (solo si NO hay intermedios)
    if not stops:
        print("🔍 Buscando en histórico de rutas...")
        historico = dao.buscar_en_historico(origin, destination)
        
        if historico:
            coste, camino = historico
            print("✅ ¡Ruta encontrada en el histórico!")
            print("   (No fue necesario recalcular con Dijkstra)\n")
            print(f"💰 Coste total: {coste}")
            print(f"🛣️  Camino: {' → '.join(map(str, camino))}")
            print("-" * 50)
            return
        else:
            print("ℹ️  No se encontró en el histórico. Calculando ruta...\n")
    
    # Calcular ruta óptima con Dijkstra
    best = route_with_stops(graph, origin, stops, destination)
    
    if best is None:
        print("❌ No existe ruta posible entre los puntos indicados.")
        print("-" * 50)
        return
    
    # Mostrar ruta óptima
    print("✅ RUTA ÓPTIMA CALCULADA:")
    print(f"💰 Coste total: {best.cost}")
    print(f"🛣️  Camino: {' → '.join(map(str, best.path))}")
    print()
    
    # Guardar en histórico (solo si NO hay intermedios)
    if not stops:
        dao.guardar_ruta(origin, destination, best.cost, best.path, False)
        print("💾 Ruta guardada en el histórico.\n")
    
    # Calcular ruta alternativa (solo cuando NO hay intermedios)
    if not stops:
        print("🔄 Buscando ruta alternativa...")
        alt = second_shortest_path_yen(graph, origin, destination)
        
        if choose_alternative_if_close(best, alt, 0.15):
            print(f"✅ RUTA ALTERNATIVA (dentro del 15%):")
            print(f"💰 Coste total: {alt.cost}")
            print(f"🛣️  Camino: {' → '.join(map(str, alt.path))}")
            print(f"📊 Diferencia: +{((alt.cost - best.cost) / best.cost * 100):.1f}%\n")
            
            choice = input("❓ ¿Deseas elegir la ruta alternativa? (s/n): ").strip().lower()
            
            if choice == "s":
                print("✅ Has elegido la ruta alternativa.")
                # Guardar que eligió la alternativa
                dao.guardar_ruta(origin, destination, alt.cost, alt.path, True)
            else:
                print("✅ Mantienes la ruta óptima.")
        else:
            print("ℹ️  No hay ruta alternativa válida dentro del 15%.")
    
    print("-" * 50)
    print("🎯 Proceso completado.")



if __name__ == "__main__":
    main()
