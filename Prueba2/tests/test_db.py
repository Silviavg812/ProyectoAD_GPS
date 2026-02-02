import sqlite3
import os

ruta_db = "data/gps.db"

print("Directorio actual:", os.getcwd())
print("¿Existe carpeta data?", os.path.isdir("data"))

try:
    os.makedirs("data", exist_ok=True)  # crea la carpeta si no existe
    conn = sqlite3.connect(ruta_db)
    print("¡Base de datos creada/abierto correctamente!")
    conn.close()
except Exception as e:
    print("Error:", str(e))