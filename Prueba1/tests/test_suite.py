"""
SUITE DE PRUEBAS COMPLETA
Valida: DAO, Dijkstra, GUI, Requisitos del proyecto

Ejecutar: python -m pytest tests/test_suite.py -v
o:       python tests/test_suite.py
"""

import pytest
import sys
from pathlib import Path

# Añadir proyecto raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dao.database import DatabaseManager
from algorithm.dijkstra import dijkstra, ruta_alternativa
from gui.interfaz import GPSInterface
import sqlite3

class TestDatabaseManager:
    """Pruebas para la capa DAO"""
    
    @pytest.fixture
    def db_test(self):
        db = DatabaseManager('tests/test_gps.db')
        yield db
        # Cleanup
        if os.path.exists('tests/test_gps.db'):
            os.remove('tests/test_gps.db')
    
    def test_inicializar_bd(self, db_test):
        """Verifica que las tablas se crean correctamente"""
        conn = sqlite3.connect('tests/test_gps.db')
        cursor = conn.cursor()
        
        # Verificar tablas existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = [row[0] for row in cursor.fetchall()]
        
        assert 'nodos' in tablas
        assert 'aristas' in tablas
        assert 'historico_rutas' in tablas
        
        conn.close()
    
    def test_cargar_csv(self, db_test):
        """Verifica carga de CSV → BD"""
        db_test.cargar_csv('data/mapa_gps.csv')
        
        # Contar nodos y aristas
        conn = sqlite3.connect('tests/test_gps.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM nodos')
        nodos_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM aristas')
        aristas_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert nodos_count >= 40, f"Debe tener ≥40 nodos, tiene {nodos_count}"
        assert aristas_count >= 80, f"Debe tener ≥80 aristas, tiene {aristas_count}"
    
    def test_construir_grafo(self, db_test):
        """Verifica que construye grafo correcto"""
        db_test.cargar_csv('data/mapa_gps.csv')
        grafo = db_test.construir_grafo('distancia')
        
        assert isinstance(grafo, dict)
        assert len(grafo) >= 40
        assert 'Puerta_del_Sol' in grafo
        assert len(grafo['Puerta_del_Sol']) > 0
        
        # Verificar formato: [(vecino, coste), ...]
        primer_vecino, coste = grafo['Puerta_del_Sol'][0]
        assert isinstance(primer_vecino, str)
        assert isinstance(coste, float)
        assert coste >= 0

class TestDijkstra:
    """Pruebas para el algoritmo Dijkstra"""
    
    @pytest.fixture
    def db_test(self):
        db = DatabaseManager('tests/test_dijkstra.db')
        db.cargar_csv('data/mapa_gps.csv')
        return db
    
    def test_ruta_directa(self, db_test):
        """Ruta simple entre nodos conectados directamente"""
        grafo = db_test.construir_grafo('distancia')
        coste, ruta = dijkstra(grafo, 'Puerta_del_Sol', 'Plaza_Mayor')
        
        assert coste == 1.2  # Valor del CSV
        assert len(ruta) == 2
        assert ruta[0] == 'Puerta_del_Sol'
        assert ruta[1] == 'Plaza_Mayor'
    
    def test_ruta_larga(self, db_test):
        """Ruta con múltiples saltos"""
        grafo = db_test.construir_grafo('distancia')
        coste, ruta = dijkstra(grafo, 'Puerta_del_Sol', 'Alcorcon')
        
        assert coste < 50.0  # Ruta razonable
        assert coste != float('inf')
        assert len(ruta) > 3  # Múltiples nodos
        assert ruta[0] == 'Puerta_del_Sol'
        assert ruta[-1] == 'Alcorcon'
    
    def test_ruta_imposible(self, db_test):
        """Nodo destino no alcanzable"""
        grafo = db_test.construir_grafo('distancia')
        coste, ruta = dijkstra(grafo, 'Puerta_del_Sol', 'NODO_FANTASMA')
        
        assert coste == float('inf')
        assert ruta == []
    
    def test_intermedios(self, db_test):
        """Ruta obligando a pasar por nodo intermedio"""
        grafo = db_test.construir_grafo('distancia')
        coste, ruta = dijkstra(grafo, 'Puerta_del_Sol', 'Calle_Mayor', ['Plaza_Mayor'])
        
        assert 'Plaza_Mayor' in ruta
        assert ruta[0] == 'Puerta_del_Sol'
        assert ruta[-1] == 'Calle_Mayor'
    
    def test_distancia_vs_tiempo(self, db_test):
        """Misma ruta optimizada diferente"""
        grafo_dist = db_test.construir_grafo('distancia')
        grafo_tiempo = db_test.construir_grafo('tiempo')
        
        ruta_dist = dijkstra(grafo_dist, 'Bernabeu', 'Azca')[1]
        ruta_tiempo = dijkstra(grafo_tiempo, 'Bernabeu', 'Azca')[1]
        
        assert len(ruta_dist) > 0
        assert len(ruta_tiempo) > 0
    
    def test_alternativa(self, db_test):
        """Verifica ruta alternativa"""
        grafo = db_test.construir_grafo('distancia')
        coste_opt, ruta_opt = dijkstra(grafo, 'Paseo_Castellana', 'Chamartin')
        
        alternativa = ruta_alternativa(grafo, 'Paseo_Castellana', 'Chamartin', coste_opt)
        
        if alternativa:
            coste_alt, ruta_alt = alternativa
            assert coste_alt <= coste_opt * 1.15  # Dentro del 15%
            assert ruta_alt != ruta_opt  # Ruta diferente

class TestRequisitosProyecto:
    """Valida requisitos mínimos del proyecto"""
    
    @pytest.fixture
    def db(self):
        return DatabaseManager('tests/reqs.db')
    
    def test_nodos_minimos(self, db):
        """40+ nodos"""
        db.cargar_csv('data/mapa_gps.csv')
        nodos = db.obtener_nodos()
        assert len(nodos) >= 40
    
    def test_aristas_minimas(self, db):
        """80+ aristas"""
        db.cargar_csv('data/mapa_gps.csv')
        conn = sqlite3.connect('tests/reqs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM aristas')
        aristas = cursor.fetchone()[0]
        conn.close()
        assert aristas >= 80
    
    def test_unidireccionales(self, db):
        """40+ aristas unidireccionales"""
        db.cargar_csv('data/mapa_gps.csv')
        conn = sqlite3.connect('tests/reqs.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM aristas a
            WHERE NOT EXISTS (
                SELECT 1 FROM aristas b 
                WHERE b.origen = a.destino AND b.destino = a.origen
            )
        ''')
        uni = cursor.fetchone()[0]
        conn.close()
        assert uni >= 40

class TestIntegracionCompleta:
    """Prueba flujo completo aplicación"""
    
    def test_flujo_completo(self):
        """DAO → Grafo → Dijkstra → Resultado"""
        db = DatabaseManager('tests/integracion.db')
        db.cargar_csv('data/mapa_gps.csv')
        
        nodos = db.obtener_nodos()
        assert len(nodos) > 0
        
        grafo = db.construir_grafo()
        assert isinstance(grafo, dict)
        
        coste, ruta = dijkstra(grafo, nodos[0], nodos[1])
        assert isinstance(coste, float)
        assert isinstance(ruta, list)

# Entry point para ejecutar pruebas directamente
if __name__ == "__main__":
    pytest.main([__file__, '-v'])

