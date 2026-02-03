import sqlite3
from typing import Iterable, List, Optional
from datetime import datetime
from src.graph import Edge, NodeId
from src.dao_interface import GraphDAO

class SqliteDAO(GraphDAO):
    def __init__(self, db_path: str = "data/gps.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Crea las tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de nodos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodos (
                id INTEGER PRIMARY KEY
            )
        ''')
        
        # Tabla de aristas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aristas (
                origin INTEGER NOT NULL,
                destination INTEGER NOT NULL,
                cost REAL NOT NULL,
                PRIMARY KEY (origin, destination)
            )
        ''')
        
        # Tabla de histórico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin INTEGER NOT NULL,
                destination INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                coste_total REAL NOT NULL,
                camino TEXT NOT NULL,
                eligio_alternativa INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cargar_desde_csv(self, csv_path: str):
        """Lee CSV y lo carga en SQLite (solo primera vez)"""
        import csv
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpiar tablas
        cursor.execute("DELETE FROM aristas")
        cursor.execute("DELETE FROM nodos")
        
        nodos_set = set()
        
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = int(row["origin"])
                v = int(row["destination"])
                cost = float(row["cost"])
                
                nodos_set.add(u)
                nodos_set.add(v)
                
                cursor.execute(
                    "INSERT OR REPLACE INTO aristas (origin, destination, cost) VALUES (?, ?, ?)",
                    (u, v, cost)
                )
        
        # Insertar nodos
        for nodo in nodos_set:
            cursor.execute("INSERT OR IGNORE INTO nodos (id) VALUES (?)", (nodo,))
        
        conn.commit()
        conn.close()
    
    def get_neighbors(self, node: NodeId) -> Iterable[Edge]:
        """Consulta SQL para obtener vecinos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT destination, cost FROM aristas WHERE origin = ?",
            (node,)
        )
        
        edges = [Edge(to=row[0], cost=row[1]) for row in cursor.fetchall()]
        conn.close()
        return edges
    
    def guardar_ruta(self, origin: int, destination: int, coste: float, 
                     camino: List[int], eligio_alt: bool = False):
        """Guarda una ruta en el histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fecha = datetime.now().isoformat()
        camino_str = ",".join(map(str, camino))
        
        cursor.execute(
            """INSERT INTO historico 
               (origin, destination, fecha, coste_total, camino, eligio_alternativa)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (origin, destination, fecha, coste, camino_str, int(eligio_alt))
        )
        
        conn.commit()
        conn.close()
    
    def buscar_en_historico(self, origin: int, destination: int) -> Optional[tuple]:
        """Busca en histórico si ya se calculó esta ruta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT coste_total, camino FROM historico 
               WHERE origin = ? AND destination = ?
               ORDER BY fecha DESC LIMIT 1""",
            (origin, destination)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            coste = row[0]
            camino = [int(x) for x in row[1].split(",")]
            return (coste, camino)
        return None
