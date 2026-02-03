"""
Script de diagnóstico para verificar estructura de la base de datos
"""

import sqlite3

def diagnosticar_db(db_path="data/gps.db"):
    """
    Muestra la estructura de la base de datos
    """
    print("=" * 60)
    print("DIAGNÓSTICO DE BASE DE DATOS GPS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        print(f"\n📊 Tablas encontradas: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
        
        # Verificar tabla 'aristas'
        if ('aristas',) in tablas:
            print("\n✅ Tabla 'aristas' encontrada")
            
            # Obtener columnas de la tabla aristas
            cursor.execute("PRAGMA table_info(aristas);")
            columnas = cursor.fetchall()
            
            print("\n📋 Columnas en 'aristas':")
            for col in columnas:
                col_id, nombre, tipo, notnull, default, pk = col
                print(f"  {col_id}. {nombre:15} - {tipo:10} (PK: {pk}, NOT NULL: {notnull})")
            
            # Mostrar algunas filas de ejemplo
            cursor.execute("SELECT * FROM aristas LIMIT 3;")
            filas = cursor.fetchall()
            
            print(f"\n📝 Primeras 3 filas de 'aristas':")
            nombres_columnas = [desc[1] for desc in columnas]
            print(f"  {nombres_columnas}")
            for fila in filas:
                print(f"  {fila}")
        
        else:
            print("\n❌ Tabla 'aristas' NO encontrada")
            print("Tablas disponibles:", [t[0] for t in tablas])
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("FIN DEL DIAGNÓSTICO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    diagnosticar_db()