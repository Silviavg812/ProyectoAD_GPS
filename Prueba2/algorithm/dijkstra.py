"""
ALGORITMO DE DIJKSTRA - CAPA DE CÁLCULO DE RUTAS
Responsable de: calcular rutas óptimas
NO contiene: SQL, GUI, archivos, entrada usuario
Solo recibe grafo en memoria y devuelve resultados

IMPORTANTE: Este módulo NO debe importar DatabaseManager directamente.
Solo trabaja con grafos que ya están en memoria.
"""

from typing import Dict, List, Tuple, Optional
import heapq
import sys
from pathlib import Path


def verificar_estructura_grafo(grafo: Dict[str, List[Tuple[str, float]]]) -> bool:
    """
    Verifica que la estructura del grafo sea válida.
    Útil para debugging.
    """
    if not grafo:
        print("❌ ERROR: Grafo vacío")
        return False
    
    nodos_con_problemas = []
    
    for nodo, conexiones in grafo.items():
        if not isinstance(nodo, str):
            nodos_con_problemas.append((nodo, "Nodo no es string"))
            continue
            
        if not isinstance(conexiones, list):
            nodos_con_problemas.append((nodo, f"Conexiones no es lista: {type(conexiones)}"))
            continue
        
        for conexion in conexiones:
            if not isinstance(conexion, tuple) or len(conexion) != 2:
                nodos_con_problemas.append((nodo, f"Conexión inválida: {conexion}"))
            else:
                vecino, coste = conexion
                if not isinstance(vecino, str):
                    nodos_con_problemas.append((nodo, f"Vecino no es string: {vecino}"))
                if not isinstance(coste, (int, float)):
                    nodos_con_problemas.append((nodo, f"Coste no es número: {coste}"))
    
    if nodos_con_problemas:
        print(f"⚠️  Problemas en el grafo:")
        for nodo, problema in nodos_con_problemas[:5]:  # Mostrar solo primeros 5
            print(f"   - {nodo}: {problema}")
        if len(nodos_con_problemas) > 5:
            print(f"   ... y {len(nodos_con_problemas) - 5} más")
        return False
    
    print(f"✅ Grafo verificado: {len(grafo)} nodos")
    return True


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
    
    print(f"\n" + "="*60)
    print(f"🚀 ALGORITMO DIJKSTRA")
    print("="*60)
    print(f"   Ruta solicitada: {inicio} → {fin}")
    print(f"   Intermedios: {intermedios if intermedios else 'Ninguno'}")
    print(f"   Nodos en grafo: {len(grafo)}")
    
    # Verificar estructura del grafo
    if not verificar_estructura_grafo(grafo):
        print(f"❌ ERROR: Estructura del grafo inválida")
        return (float('inf'), [])
    
    # Validar nodos
    if inicio not in grafo:
        print(f"❌ ERROR: Nodo inicio '{inicio}' no está en grafo")
        print(f"   Nodos disponibles (primeros 10): {list(grafo.keys())[:10]}")
        return (float('inf'), [])
    
    if fin not in grafo:
        print(f"❌ ERROR: Nodo fin '{fin}' no está en grafo")
        print(f"   Nodos disponibles (primeros 10): {list(grafo.keys())[:10]}")
        return (float('inf'), [])
    
    # Validar nodos intermedios
    if intermedios:
        nodos_invalidos = [nodo for nodo in intermedios if nodo not in grafo]
        if nodos_invalidos:
            print(f"❌ ERROR: Nodos intermedios no están en grafo: {nodos_invalidos}")
            return (float('inf'), [])
    
    # Manejar destinos intermedios
    if intermedios:
        print(f"\n📍 Calculando ruta con intermedios...")
        resultado = _dijkstra_con_intermedios(grafo, inicio, fin, intermedios)
    else:
        # Dijkstra básico
        print(f"\n📍 Calculando ruta básica...")
        resultado = _dijkstra_basico(grafo, inicio, fin)
    
    print("="*60)
    return resultado


def _dijkstra_basico(grafo: Dict[str, List[Tuple[str, float]]], 
                     inicio: str, fin: str) -> Tuple[float, List[str]]:
    """Implementación básica de Dijkstra"""
    
    print(f"\n   🔍 Dijkstra básico: {inicio} → {fin}")
    print(f"      Nodo inicio en grafo: {inicio in grafo}")
    print(f"      Nodo fin en grafo: {fin in grafo}")
    
    # Inicialización
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}
    cola_prioritaria = [(0, inicio)]  # (distancia, nodo)
    visitados = set()
    
    # Estadísticas
    iteraciones = 0
    nodos_expandidos = 0
    
    print(f"      Nodos inicializados: {len(distancias)}")
    print(f"      Conexiones desde inicio ({inicio}): {len(grafo.get(inicio, []))}")
    
    # Algoritmo principal
    while cola_prioritaria:
        iteraciones += 1
        dist_actual, nodo_actual = heapq.heappop(cola_prioritaria)
        
        if nodo_actual in visitados:
            continue
        
        visitados.add(nodo_actual)
        
        if nodo_actual == fin:
            print(f"      ✅ Destino alcanzado en iteración {iteraciones}")
            break
        
        if dist_actual > distancias[nodo_actual]:
            continue
        
        if nodo_actual not in grafo:
            print(f"      ⚠️  Nodo actual '{nodo_actual}' no está en grafo, saltando")
            continue
        
        # Explorar vecinos
        conexiones = grafo.get(nodo_actual, [])
        nodos_expandidos += 1
        
        if not conexiones:
            print(f"      ⚠️  Nodo '{nodo_actual}' no tiene conexiones")
            continue
        
        for vecino, coste in conexiones:
            if vecino not in distancias:
                print(f"      ⚠️  Vecino '{vecino}' no está en distancias, saltando")
                continue
            
            # Validar que el coste sea positivo
            if coste <= 0:
                print(f"      ⚠️  Coste no positivo de {nodo_actual} a {vecino}: {coste}")
                continue
                
            nueva_dist = distancias[nodo_actual] + coste
            
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioritaria, (nueva_dist, vecino))
    
    # Reconstruir ruta
    if distancias[fin] == float('inf'):
        print(f"\n      ❌ No hay ruta de {inicio} a {fin}")
        print(f"      📊 Estadísticas:")
        print(f"         - Iteraciones: {iteraciones}")
        print(f"         - Nodos visitados: {len(visitados)}/{len(grafo)}")
        print(f"         - Nodos expandidos: {nodos_expandidos}")
        return (float('inf'), [])
    
    ruta = _reconstruir_ruta(predecesores, fin)
    
    print(f"\n      ✅ RUTA ENCONTRADA")
    print(f"         - Nodos en ruta: {len(ruta)}")
    print(f"         - Coste total: {distancias[fin]:.2f}")
    print(f"         - Ruta: {' → '.join(ruta)}")
    print(f"      📊 Estadísticas:")
    print(f"         - Iteraciones: {iteraciones}")
    print(f"         - Nodos visitados: {len(visitados)}/{len(grafo)}")
    print(f"         - Nodos expandidos: {nodos_expandidos}")
    
    return (distancias[fin], ruta)


def _dijkstra_con_intermedios(grafo: Dict[str, List[Tuple[str, float]]], 
                             inicio: str, fin: str, 
                             intermedios: List[str]) -> Tuple[float, List[str]]:
    """Dijkstra para rutas con nodos intermedios obligatorios"""
    print(f"      🔄 Dijkstra con {len(intermedios)} intermedios")
    print(f"      Ruta completa: {inicio} → {' → '.join(intermedios)} → {fin}")
    
    ruta_completa = []
    coste_total = 0
    nodo_actual = inicio
    
    # Lista de todos los destinos (intermedios + fin final)
    destinos = intermedios + [fin]
    
    # Calcular cada tramo
    for i, siguiente_destino in enumerate(destinos):
        print(f"\n      📍 Tramo {i+1}/{len(destinos)}: {nodo_actual} → {siguiente_destino}")
        
        coste_parcial, ruta_parcial = _dijkstra_basico(grafo, nodo_actual, siguiente_destino)
        
        if coste_parcial == float('inf'):
            print(f"      ❌ No hay ruta de {nodo_actual} a {siguiente_destino}")
            print(f"      ⚠️  Ruta completa no posible")
            return (float('inf'), [])
        
        coste_total += coste_parcial
        
        if i == 0:
            # Primer tramo: incluir todo
            ruta_completa.extend(ruta_parcial)
        else:
            # Tramo siguiente: evitar duplicar nodo_actual
            if ruta_parcial and ruta_parcial[0] == nodo_actual:
                ruta_completa.extend(ruta_parcial[1:])
            else:
                ruta_completa.extend(ruta_parcial)
        
        print(f"      ✓ Tramo completado: +{coste_parcial:.2f} (total: {coste_total:.2f})")
        nodo_actual = siguiente_destino
    
    # Validar ruta final
    if not ruta_completa:
        print(f"      ❌ Ruta completa vacía")
        return (float('inf'), [])
    
    print(f"\n      ✅ RUTA COMPLETA CON INTERMEDIOS")
    print(f"         - Nodos totales: {len(ruta_completa)}")
    print(f"         - Coste total: {coste_total:.2f}")
    print(f"         - Ruta completa: {' → '.join(ruta_completa)}")
    
    return (coste_total, ruta_completa)


def _reconstruir_ruta(predecesores: Dict[str, Optional[str]], fin: str) -> List[str]:
    """Reconstruye ruta desde predecesores"""
    ruta = []
    nodo_actual = fin
    
    # Seguir la cadena de predecesores
    while nodo_actual is not None:
        ruta.append(nodo_actual)
        nodo_actual = predecesores.get(nodo_actual)
    
    # Invertir para tener inicio → fin
    ruta.reverse()
    
    # Validaciones
    if not ruta:
        print(f"      ⚠️  Ruta reconstruida vacía")
        return []
    
    if len(ruta) < 2:
        print(f"      ⚠️  Ruta muy corta: {ruta}")
    
    # Verificar que no haya None en la ruta
    if None in ruta:
        print(f"      ⚠️  Ruta contiene None: {ruta}")
        ruta = [nodo for nodo in ruta if nodo is not None]
    
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
    
    print(f"\n" + "="*60)
    print(f"🔄 BUSCANDO RUTA ALTERNATIVA")
    print(f"   Ruta óptima: {inicio} → {fin} (coste: {coste_optimo:.2f})")
    print("="*60)
    
    # Dijkstra modificado: penalizar nodos clave
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    predecesores = {nodo: None for nodo in grafo}
    
    cola_prioritaria = [(0, inicio)]
    visitados = set()
    iteraciones = 0
    
    while cola_prioritaria:
        iteraciones += 1
        dist_actual, nodo_actual = heapq.heappop(cola_prioritaria)
        
        if nodo_actual in visitados:
            continue
        
        visitados.add(nodo_actual)
        
        if nodo_actual == fin:
            break
        
        if dist_actual > distancias[nodo_actual]:
            continue
        
        for vecino, coste_base in grafo.get(nodo_actual, []):
            # Penalización artificial para generar ruta diferente
            # Basada en características del nombre del nodo
            factor_penalizacion = 1.0
            
            # Penalizar nodos comunes (ajusta según tus datos)
            palabras_comunes = ['centro', 'plaza', 'principal', 'av', 'av.', 'calle']
            if any(palabra in vecino.lower() for palabra in palabras_comunes):
                factor_penalizacion = 1.3
            
            coste_penalizado = coste_base * factor_penalizacion
            
            nueva_dist = distancias[nodo_actual] + coste_penalizado
            
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioritaria, (nueva_dist, vecino))
    
    # Validar alternativa
    if distancias[fin] == float('inf'):
        print(f"❌ No se encontró ruta alternativa")
        return None
    
    porcentaje_mas = ((distancias[fin] - coste_optimo) / coste_optimo) * 100
    
    if distancias[fin] > coste_optimo * 1.15:
        print(f"❌ Alternativa demasiado costosa:")
        print(f"   - Coste óptimo: {coste_optimo:.2f}")
        print(f"   - Coste alternativa: {distancias[fin]:.2f}")
        print(f"   - Diferencia: +{porcentaje_mas:.1f}% (máx: +15%)")
        return None
    
    ruta = _reconstruir_ruta(predecesores, fin)
    
    # Si es idéntica o muy corta, descartar
    if len(ruta) <= 2:
        print(f"❌ Alternativa es demasiado simple (solo {len(ruta)} nodos)")
        return None
    
    print(f"✅ ALTERNATIVA ENCONTRADA")
    print(f"   - Coste: {distancias[fin]:.2f} (+{porcentaje_mas:.1f}%)")
    print(f"   - Nodos en ruta: {len(ruta)}")
    print(f"   - Ruta: {' → '.join(ruta)}")
    print(f"📊 Estadísticas:")
    print(f"   - Iteraciones: {iteraciones}")
    print(f"   - Nodos visitados: {len(visitados)}")
    
    return (distancias[fin], ruta)


def es_alternativa_valida(coste_optimo: float, coste_alternativa: float) -> bool:
    """Valida si alternativa está dentro del 15%"""
    diferencia = ((coste_alternativa - coste_optimo) / coste_optimo) * 100
    es_valida = coste_alternativa <= coste_optimo * 1.15
    
    if es_valida:
        print(f"✅ Alternativa válida: +{diferencia:.1f}%")
    else:
        print(f"❌ Alternativa no válida: +{diferencia:.1f}% (máx: +15%)")
    
    return es_valida


# Si este archivo se ejecuta directamente, hacer pruebas
if __name__ == "__main__":
    print("🧪 PRUEBAS DIJKSTRA")
    print("="*60)
    
    # Grafo de ejemplo simple
    grafo_ejemplo = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }
    
    # Prueba básica
    print("\nPrueba 1: A → D")
    coste, ruta = dijkstra(grafo_ejemplo, 'A', 'D')
    print(f"   Resultado: coste={coste}, ruta={ruta}")
    
    # Prueba con intermedio
    print("\nPrueba 2: A → D pasando por C")
    coste2, ruta2 = dijkstra(grafo_ejemplo, 'A', 'D', ['C'])
    print(f"   Resultado: coste={coste2}, ruta={ruta2}")
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")