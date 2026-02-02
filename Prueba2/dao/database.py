"""
CAPA DAO - Data Access Object
Responsable de: TODO lo relacionado con SQLite
NO contiene: Dijkstra, GUI, lógica de negocio
"""

import sqlite3
import csv
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path: str = None):
        # Ruta absoluta a gps.db (independiente del directorio de ejecución)
        project_root = Path(__file__).resolve().parents[1]  # sube hasta Prueba1
        
        # Asegurar que el directorio 'data' existe
        data_dir = project_root / 'data'
        data_dir.mkdir(exist_ok=True, parents=True)  # ← CREA DIRECTORIO SI NO EXISTE
        
        default_db = data_dir / 'gps.db'
        self.db_path = db_path or str(default_db)
        
        print(f"\n📍 CONFIGURACIÓN BASE DE DATOS:")
        print(f"   Ruta proyecto: {project_root}")
        print(f"   Directorio data: {data_dir}")
        print(f"   Existe directorio: {data_dir.exists()}")
        print(f"   Ruta DB completa: {self.db_path}")
        
        # Verificar permisos
        try:
            if data_dir.exists():
                print(f"   Permisos directorio: {oct(data_dir.stat().st_mode)[-3:]}")
        except:
            print(f"   ⚠️  No se pudo leer permisos del directorio")
        
        self._inicializar_base_datos()
    
    def _inicializar_base_datos(self):
        """Crea las tablas necesarias si no existen"""
        print(f"\n📍 INICIALIZANDO BASE DE DATOS...")
        
        try:
            # Intentar crear directorio padre si no existe
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(exist_ok=True, parents=True)
            
            print(f"   Directorio DB: {db_dir}")
            print(f"   Existe directorio: {db_dir.exists()}")
            
            # Crear archivo vacío si no existe (para verificar permisos)
            if not os.path.exists(self.db_path):
                print(f"   Creando archivo DB: {self.db_path}")
                with open(self.db_path, 'w') as f:
                    f.write('')  # Archivo vacío
            
            # Verificar permisos de escritura
            if os.access(db_dir, os.W_OK):
                print(f"   ✅ Permisos de escritura OK")
            else:
                print(f"   ❌ SIN PERMISOS DE ESCRITURA en {db_dir}")
            
            # Conectar a SQLite
            print(f"   Conectando a SQLite...")
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
            
            # Tabla histórico de rutas
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
            print(f"   ✅ Tablas creadas/verificadas")
            
        except sqlite3.OperationalError as e:
            print(f"❌ ERROR SQLite: {e}")
            print(f"   Ruta DB: {self.db_path}")
            raise
        except Exception as e:
            print(f"❌ ERROR inesperado: {e}")
            raise
    
    def cargar_csv(self, csv_path: str):
        """
        Carga datos del CSV con formato:
        origen,destino,distancia,tiempo
        """
        print(f"\n" + "="*60)
        print(f"CARGANDO CSV: {csv_path}")
        print("="*60)
        
        # Verificar que el CSV existe
        if not os.path.exists(csv_path):
            print(f"❌ ERROR: Archivo CSV no encontrado en: {csv_path}")
            print(f"   Directorio actual: {os.getcwd()}")
            print(f"   Archivos en directorio: {os.listdir(os.path.dirname(csv_path))}")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        nodos_insertados = set()
        lineas_procesadas = 0
        errores = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                print(f"📍 CSV detectado con columnas: {reader.fieldnames}")
                print(f"📍 Primeras líneas del CSV:")
                
                # Leer primeras líneas para diagnóstico
                f.seek(0)
                for i, line in enumerate(f):
                    if i < 5:  # Mostrar primeras 5 líneas
                        print(f"   Línea {i}: {line.strip()}")
                    else:
                        break
                
                # Volver al inicio
                f.seek(0)
                next(f)  # Saltar header
                
                for fila in reader:
                    try:
                        origen = fila['origen'].strip()
                        destino = fila['destino'].strip()
                        distancia = float(fila['distancia'])
                        tiempo = float(fila['tiempo'])
                        
                        # Insertar nodos si no existen
                        if origen not in nodos_insertados:
                            cursor.execute('INSERT OR IGNORE INTO nodos (nombre) VALUES (?)', (origen,))
                            nodos_insertados.add(origen)
                        
                        if destino not in nodos_insertados:
                            cursor.execute('INSERT OR IGNORE INTO nodos (nombre) VALUES (?)', (destino,))
                            nodos_insertados.add(destino)
                        
                        # Insertar arista
                        cursor.execute('''
                            INSERT OR IGNORE INTO aristas (origen, destino, distancia, tiempo)
                            VALUES (?, ?, ?, ?)
                        ''', (origen, destino, distancia, tiempo))
                        
                        lineas_procesadas += 1
                        
                        if lineas_procesadas <= 5:  # Mostrar primeras 5 conexiones
                            print(f"   ✓ Arista {lineas_procesadas}: {origen} → {destino}")
                    
                    except (ValueError, KeyError) as e:
                        print(f"   ❌ Error en fila: {fila} → {e}")
                        errores += 1
                        continue
                    except Exception as e:
                        print(f"   ❌ Error inesperado: {e}")
                        errores += 1
                        continue
        
        except FileNotFoundError:
            print(f"❌ No se encontró el archivo CSV: {csv_path}")
            conn.close()
            return
        except Exception as e:
            print(f"❌ Error grave al leer CSV: {e}")
            conn.close()
            return
        
        conn.commit()
        conn.close()
        
        print("\n📊 RESUMEN CARGA CSV:")
        print(f"   ✅ Líneas procesadas: {lineas_procesadas}")
        print(f"   ✅ Nodos únicos insertados: {len(nodos_insertados)}")
        print(f"   ❌ Errores: {errores}")
        if nodos_insertados:
            print(f"   📍 Nodos insertados: {sorted(list(nodos_insertados))[:10]}...")
        print("="*60)
    
    def obtener_nodos(self) -> List[str]:
        """Lista todos los nombres de nodos disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nombre FROM nodos ORDER BY nombre')
        nodos = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"📍 obtener_nodos() devuelve: {len(nodos)} nodos")
        if nodos:
            print(f"   Ejemplos: {nodos[:10]}")
        else:
            print("   ⚠️  No hay nodos en la base de datos")
        
        return nodos
    
    def construir_grafo(self, tipo_coste: str = 'distancia') -> Dict[str, List[Tuple[str, float]]]:
        """
        Construye grafo en memoria desde la BD
        Retorna: {nodo: [(vecino, coste), ...]}
        """
        print(f"\n" + "="*60)
        print(f"CONSTRUYENDO GRAFO - Tipo: {tipo_coste}")
        print("="*60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT origen, destino, distancia, tiempo FROM aristas')
        aristas = cursor.fetchall()
        
        # 1. Obtener TODOS los nodos de la tabla nodos
        cursor.execute('SELECT nombre FROM nodos ORDER BY nombre')
        nodos_db = [row[0] for row in cursor.fetchall()]
        
        print(f"📍 NODOS en tabla 'nodos': {len(nodos_db)}")
        if nodos_db:
            print(f"   Ejemplos: {nodos_db[:10]}")
        else:
            print("   ⚠️  TABLA NODOS VACÍA!")
        
        # 2. Verificar nodos únicos en aristas
        nodos_en_aristas = set()
        for origen, destino, _, _ in aristas:
            nodos_en_aristas.add(origen)
            nodos_en_aristas.add(destino)
        
        print(f"📍 NODOS en aristas: {len(nodos_en_aristas)}")
        
        # 3. Verificar diferencias
        faltan_en_nodos = nodos_en_aristas - set(nodos_db)
        if faltan_en_nodos:
            print(f"⚠️  NODOS en aristas que NO están en tabla nodos:")
            for nodo in faltan_en_nodos:
                print(f"   - {nodo}")
        
        # 4. Crear grafo
        grafo: Dict[str, List[Tuple[str, float]]] = {}
        
        # Inicializar con TODOS los nodos de la tabla nodos
        for nodo in nodos_db:
            grafo[nodo] = []
        
        print(f"📍 GRAFO inicializado con {len(grafo)} nodos")
        
        # 5. Llenar conexiones
        conexiones_validas = 0
        conexiones_invalidas = 0
        
        for origen, destino, distancia, tiempo in aristas:
            coste = distancia if tipo_coste == 'distancia' else tiempo
            
            # Validar existencia de nodos
            if origen not in grafo:
                print(f"❌ ERROR: Origen '{origen}' no está en grafo")
                conexiones_invalidas += 1
                continue
            
            if destino not in grafo:
                print(f"❌ ERROR: Destino '{destino}' no está en grafo")
                conexiones_invalidas += 1
                continue
            
            grafo[origen].append((destino, coste))
            conexiones_validas += 1
        
        # 6. Mostrar resumen
        print(f"\n📊 RESUMEN GRAFO:")
        print(f"   ✅ Conexiones válidas: {conexiones_validas}")
        print(f"   ❌ Conexiones inválidas: {conexiones_invalidas}")
        print(f"   📍 Nodos en grafo: {len(grafo)}")
        
        # Mostrar primeros nodos con sus conexiones
        print(f"\n🔍 Primeros 5 nodos del grafo:")
        for i, (nodo, conexiones) in enumerate(list(grafo.items())[:5]):
            print(f"   {nodo}: {len(conexiones)} conexiones")
            for vecino, coste in conexiones[:3]:  # Mostrar hasta 3 conexiones
                print(f"     → {vecino} ({coste})")
            if len(conexiones) > 3:
                print(f"     ... y {len(conexiones)-3} más")
        
        conn.close()
        print("="*60)
        return grafo
    
    def guardar_ruta(self, origen: str, destino: str, coste: float, 
                     tipo_coste: str, ruta: List[str], alternativa: bool = False):
        """Guarda una ruta calculada en el histórico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO historico_rutas 
            (origen, destino, fecha_hora, coste, tipo_coste, ruta_alternativa, ruta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            origen, 
            destino, 
            datetime.now().isoformat(), 
            coste, 
            tipo_coste, 
            alternativa, 
            ' → '.join(ruta)
        ))
        conn.commit()
        conn.close()
    
    def buscar_historico(self, origen: str, destino: str) -> Optional[Tuple[float, List[str]]]:
        """Busca ruta en caché histórico - versión robusta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT coste, ruta FROM historico_rutas 
            WHERE origen = ? AND destino = ? AND ruta_alternativa = 0
            ORDER BY fecha_hora DESC LIMIT 1
        ''', (origen, destino))
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado and resultado[1]:  # coste y ruta existen
            coste, ruta_str = resultado
            # Split seguro que maneja espacios y nodos vacíos
            ruta_lista = [nodo.strip() for nodo in ruta_str.split(' → ') if nodo.strip()]
            return (coste, ruta_lista)
        elif resultado:  # solo coste, ruta vacía
            return (resultado[0], [])
        return None