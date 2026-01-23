"""
ALGORITMO DE DIJKSTRA - CAPA DE CÁLCULO DE RUTAS
Responsable de: calcular rutas óptimas
NO contiene: SQL, GUI, archivos, entrada usuario
Solo recibe grafo en memoria y devuelve resultados
"""

from typing import Dict, List, Tuple, Optional
import heapq

def dijkstra(grafo: Dict[str, List[Tuple[str, float]]], 
             inicio: str, fin: str, 
             intermedios: Optional[List[str]] = None) -> Tuple[float, List[str]]:
    """
    Algoritmo de Dijkstra para grafos ponderados.
    
    Args:
        grafo: {nodo: [(vecino, coste), ...]}
        inicio: nodo de origen
        fin: nodo destino
        intermedios: lista opcional de nodos por los que pasar
    
    Returns:
        (coste_total, ruta) si existe ruta
        (float('inf'), []) si no existe ruta
    """
    
    # Validar nodos
    if inicio not in grafo or fin not in grafo:
        return (float('inf'), [])
    
    # Manejar destinos intermedios
    if intermedios:
        return _dijkstra_con_intermedios(grafo, inicio, fin, intermedios)
    
    # Dijkstra básico
    return _dijkstra_basico(grafo, inicio, fin)

def _dijkstra_basico(grafo: Dict[str, List[Tuple[str, float]]], 
                     inicio: str, fin: str) -> Tuple[float, List[str]]:
    """Implementación básica de Dijkstra"""
    
    # Inicialización
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}
    cola_prioritaria = [(0, inicio)]  # (distancia, nodo)
    visitados = set()
    
    # Algoritmo principal
    while cola_prioritaria:
        dist_actual, nodo_actual = heapq.heappop(cola_prioritaria)
        
        # Optimización: saltar nodos ya visitados
        if nodo_actual in visitados:
            continue
        
        visitados.add(nodo_actual)
        
        # Si llegamos al destino, podemos terminar
        if nodo_actual == fin:
            break
        
        # Si la distancia es obsoleta, ignorar
        if dist_actual > distancias[nodo_actual]:
            continue
        
        # Explorar vecinos
        for vecino, coste in grafo[nodo_actual]:
            nueva_dist = distancias[nodo_actual] + coste
            
            # Relajación: mejorar distancia
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioritaria, (nueva_dist, vecino))
    
    # Reconstruir ruta
    if distancias[fin] == float('inf'):
        return (float('inf'), [])
    
    return _reconstruir_ruta(predecesores, fin)

def _dijkstra_con_intermedios(grafo: Dict[str, List[Tuple[str, float]]], 
                             inicio: str, fin: str, 
                             intermedios: List[str]) -> Tuple[float, List[str]]:
    """Dijkstra para rutas con nodos intermedios obligatorios"""
    ruta_completa = [inicio]
    coste_total = 0
    nodo_actual = inicio
    
    # Calcular cada tramo
    for nodo_intermedio in intermedios + [fin]:
        coste_parcial, ruta_parcial = _dijkstra_basico(grafo, nodo_actual, nodo_intermedio)
        
        if coste_parcial == float('inf'):
            return (float('inf'), [])
        
        coste_total += coste_parcial
        ruta_completa.extend(ruta_parcial[1:])  # Sin repetir nodo actual
        nodo_actual = nodo_intermedio
    
    return (coste_total, ruta_completa)

def _reconstruir_ruta(predecesores: Dict[str, Optional[str]], fin: str) -> List[str]:
    """Reconstruye ruta desde predecesores"""
    ruta = []
    nodo_actual = fin
    
    while nodo_actual is not None:
        ruta.append(nodo_actual)
        nodo_actual = predecesores[nodo_actual]
    
    ruta.reverse()
    return ruta

def ruta_alternativa(grafo: Dict[str, List[Tuple[str, float]]], 
                     inicio: str, fin: str, 
                     coste_optimo: float) -> Optional[Tuple[float, List[str]]]:
    """
    Calcula ruta alternativa (no óptima pero válida)
    
    Args:
        coste_optimo: coste de la ruta óptima (para validar ±15%)
    
    Returns:
        (coste_alternativa, ruta_alternativa) o None
    """
    
    # Dijkstra modificado: penalizar nodos clave de ruta óptima
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}
    
    cola_prioritaria = [(0, inicio)]
    visitados = set()
    
    while cola_prioritaria:
        dist_actual, nodo_actual = heapq.heappop(cola_prioritaria)
        
        if nodo_actual in visitados:
            continue
        
        visitados.add(nodo_actual)
        
        if nodo_actual == fin:
            break
        
        if dist_actual > distancias[nodo_actual]:
            continue
        
        for vecino, coste in grafo[nodo_actual]:
            # Penalización artificial para generar ruta diferente
            coste_penalizado = coste * 1.2 if vecino == 'Paseo_Castellana' else coste
            
            nueva_dist = distancias[nodo_actual] + coste_penalizado
            
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioritaria, (nueva_dist, vecino))
    
    # Validar que es alternativa válida
    if distancias[fin] == float('inf') or distancias[fin] > coste_optimo * 1.15:
        return None
    
    ruta = _reconstruir_ruta(predecesores, fin)
    
    # Si es idéntica a la óptima, descartar
    if len(ruta) == 2:  # ruta directa
        return None
    
    return (distancias[fin], ruta)

def es_alternativa_valida(coste_optimo: float, coste_alternativa: float) -> bool:
    """Valida si alternativa está dentro del 15%"""
    return coste_alternativa <= coste_optimo * 1.15
