"""
Script de diagnóstico rápido para ver columnas de aristas
"""

import sqlite3

try:
    conn = sqlite3.connect("data/gps.db")
    cursor = conn.cursor()
    
    # Ver estructura de la tabla aristas
    cursor.execute("PRAGMA table_info(aristas);")
    columnas = cursor.fetchall()
    
    print("=" * 60)
    print("COLUMNAS EN LA TABLA 'aristas'")
    print("=" * 60)
    
    for col in columnas:
        col_id, nombre, tipo, notnull, default, pk = col
        print(f"{col_id}. {nombre:15} - {tipo:10}")
    
    # Mostrar una fila de ejemplo
    cursor.execute("SELECT * FROM aristas LIMIT 1;")
    fila = cursor.fetchone()
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE FILA")
    print("=" * 60)
    
    for i, col in enumerate(columnas):
        print(f"{col[1]:15} = {fila[i]}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")