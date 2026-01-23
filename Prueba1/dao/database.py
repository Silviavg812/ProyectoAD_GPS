"""
CAPA DAO - Data Access Object
Responsable de: TODO lo relacionado con SQLite
NO contiene: Dijkstra, GUI, lógica de negocio
"""

import sqlite3
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class DatabaseManager:
    def __init__(self, db_path: str = 'data/gps.db'):
        self.db_path = db_path
        self._inicializar_base_datos()
    
    def _inicializar_base_datos(self):
        """Crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla nodos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodos (
                id_nodo INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Tabla aristas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aristas (
                id_arista INTEGER PRIMARY KEY AUTOINCREMENT,
                origen TEXT NOT NULL,
                destino TEXT NOT NULL,
                distancia REAL NOT NULL,
                tiempo REAL NOT NULL,
                FOREIGN KEY(origen) REFERENCES nodos(nombre),
                FOREIGN KEY(destino) REFERENCES nodos(nombre)
            )
        ''')
        
        # Tabla histórico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_rutas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origen TEXT NOT NULL,
                destino TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                coste REAL NOT NULL,
                tipo_coste TEXT NOT NULL,
                ruta_alternativa BOOLEAN DEFAULT 0,
                ruta TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cargar_csv(self, csv_path: str = 'data/mapa_gps.csv'):
        """Carga datos del CSV a SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        nodos_insertados = set()
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                origen = fila['origen'].strip()
                destino = fila['destino'].strip()
                distancia = float(fila['distancia'])
                tiempo = float(fila['tiempo'])
                
                # Insertar nodos únicos
                if origen not in nodos_insertados:
                    cursor.execute('INSERT OR IGNORE INTO nodos (nombre) VALUES (?)', (origen,))
                    nodos_insertados.add(origen)
                
                if destino not in nodos_insertados:
                    cursor.execute('INSERT OR IGNORE INTO nodos (nombre) VALUES (?)', (destino,))
                    nodos_insertados.add(destino)
                
                # Insertar arista
                cursor.execute('''
                    INSERT INTO aristas (origen, destino, distancia, tiempo)
                    VALUES (?, ?, ?, ?)
                ''', (origen, destino, distancia, tiempo))
        
        conn.commit()
        conn.close()
        print(f"✓ CSV cargado: {len(nodos_insertados)} nodos únicos")
    
    def obtener_nodos(self) -> List[str]:
        """Lista todos los nodos disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nombre FROM nodos ORDER BY nombre')
        nodos = [row[0] for row in cursor.fetchall()]
        conn.close()
        return nodos
    
    def construir_grafo(self, tipo_coste: str = 'distancia') -> Dict[str, List[Tuple[str, float]]]:
        """
        Construye grafo en memoria desde BD
        
        Retorna: {nodo: [(vecino, coste), ...]}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT origen, destino, distancia, tiempo FROM aristas')
        aristas = cursor.fetchall()
        conn.close()
        
        # Inicializar grafo
        grafo: Dict[str, List[Tuple[str, float]]] = {}
        cursor_nodos = sqlite3.connect(self.db_path).cursor()
        cursor_nodos.execute('SELECT nombre FROM nodos')
        for (nodo,) in cursor_nodos.fetchall():
            grafo[nodo] = []
        cursor_nodos.close()
        
        # Llenar aristas
        coste_idx = 2 if tipo_coste == 'distancia' else 3
        for origen, destino, distancia, tiempo in aristas:
            coste = distancia if tipo_coste == 'distancia' else tiempo
            grafo[origen].append((destino, coste))
        
        return grafo
    
    def guardar_ruta(self, origen: str, destino: str, coste: float, 
                    tipo_coste: str, ruta: List[str], alternativa: bool = False):
        """Guarda ruta en histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico_rutas (origen, destino, fecha_hora, coste, tipo_coste, ruta_alternativa, ruta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (origen, destino, datetime.now().isoformat(), coste, tipo_coste, alternativa, ' → '.join(ruta)))
        conn.commit()
        conn.close()
    
    def buscar_historico(self, origen: str, destino: str) -> Optional[Tuple[float, List[str]]]:
        """Busca ruta en caché"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT coste, ruta FROM historico_rutas 
            WHERE origen = ? AND destino = ?
            ORDER BY fecha_hora DESC LIMIT 1
        ''', (origen, destino))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            coste, ruta_str = resultado
            return (coste, ruta_str.split(' → '))
        return None
