"""
APLICACIÓN PRINCIPAL - Punto de entrada
Coordina: DAO + Algorithm + GUI
"""

from pathlib import Path
import sys
import os

# Obtener la ruta absoluta del proyecto
# app.py está en: ProyectoAD_GPS-main/Prueba1/main/app.py
# Queremos llegar a: ProyectoAD_GPS-main/Prueba1/
SCRIPT_DIR = Path(__file__).resolve().parent  # main/
PROJECT_DIR = SCRIPT_DIR.parent  # Prueba1/
ROOT_DIR = PROJECT_DIR.parent  # ProyectoAD_GPS-main/ (opcional)

print(f"📁 Directorio script: {SCRIPT_DIR}")
print(f"📁 Directorio proyecto: {PROJECT_DIR}")

# Añadir raíz al sys.path para imports
sys.path.insert(0, str(PROJECT_DIR))

from gui.interfaz import GPSInterface, configurar_estilos
from dao.database import DatabaseManager


def get_csv_path() -> Path:
    """Devuelve la ruta ABSOLUTA correcta al CSV"""
    csv_path = PROJECT_DIR / "data" / "mapa_gps.csv"
    
    print(f"\n🔍 Buscando CSV en:")
    print(f"   Ruta construida: {csv_path}")
    print(f"   Existe: {csv_path.exists()}")
    
    if not csv_path.exists():
        print(f"\n📁 Contenido de {PROJECT_DIR / 'data'}:")
        if (PROJECT_DIR / 'data').exists():
            for item in os.listdir(PROJECT_DIR / 'data'):
                print(f"   - {item}")
        else:
            print(f"   ❌ ¡La carpeta 'data' no existe!")
    
    return csv_path


def inicializar_base_datos_si_vacia():
    print("\n" + "="*50)
    print("⚙️ INICIALIZANDO BASE DE DATOS")
    print("="*50)
    
    # Crear DatabaseManager (ya maneja su propia ruta interna)
    db = DatabaseManager()
    
    # Verificar nodos existentes
    nodos = db.obtener_nodos()
    print(f"\n📊 Estado inicial de la BD:")
    print(f"   Total nodos: {len(nodos)}")
    if nodos:
        print(f"   Ejemplos: {nodos[:5]}")
        print("✓ Base de datos ya inicializada")
        return
    
    print("🔍 Base de datos vacía → importando mapa desde CSV...")
    
    # Obtener ruta del CSV
    csv_path = get_csv_path()
    
    if not csv_path.is_file():
        print(f"\n❌ ERROR: No se encuentra el archivo CSV")
        print(f"   Ruta buscada: {csv_path}")
        
        # Buscar alternativas
        print(f"\n🔍 Buscando CSV en otras ubicaciones...")
        posibles_csv = list(PROJECT_DIR.rglob("*.csv"))
        if posibles_csv:
            print("   Archivos CSV encontrados:")
            for csv in posibles_csv:
                print(f"   - {csv}")
        else:
            print("   No se encontró ningún archivo CSV en el proyecto")
        
        # Crear carpeta data si no existe
        data_dir = PROJECT_DIR / "data"
        if not data_dir.exists():
            print(f"\n⚠️ La carpeta 'data' no existe. Creando...")
            data_dir.mkdir(exist_ok=True)
            print(f"   Carpeta creada: {data_dir}")
            
            # Ejemplo de cómo sería el CSV
            print(f"\n💡 El archivo CSV debe tener este formato:")
            print("   origen,destino,distancia,tiempo")
            print("   A,B,10.5,15.2")
            print("   B,C,8.3,12.7")
            print("   ...")
        
        return
    
    try:
        print(f"\n✅ CSV encontrado. Cargando datos...")
        print(f"   Tamaño: {csv_path.stat().st_size} bytes")
        
        db.cargar_csv(str(csv_path))
        
        # Verificar que se cargaron los datos
        nodos_despues = db.obtener_nodos()
        print(f"\n📊 Después de cargar CSV:")
        print(f"   Total nodos: {len(nodos_despues)}")
        if nodos_despues:
            print(f"   Primeros 5: {nodos_despues[:5]}")
            print("✓ Mapa importado correctamente")
        else:
            print("⚠️ ¡Aún no hay nodos! Revisa el formato del CSV")
            
    except Exception as e:
        print(f"\n❌ Error durante la importación:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Detalle: {e}")
        
        # Información adicional para debug
        import traceback
        print(f"\n🔍 Traceback completo:")
        traceback.print_exc()


def main():
    print("\n" + "="*60)
    print("🚀 SISTEMA GPS CON ALGORITMO DIJKSTRA")
    print("📊 Proyecto Final DAM - Estructuras de Datos")
    print("="*60)
    
    # Mostrar información del entorno
    print(f"\n📁 Entorno de ejecución:")
    print(f"   Python: {sys.version}")
    print(f"   Directorio trabajo: {os.getcwd()}")
    print(f"   Script ejecutado: {__file__}")
    
    # Inicializar base de datos
    inicializar_base_datos_si_vacia()
    
    # Configurar estilos
    print(f"\n🎨 Configurando interfaz gráfica...")
    configurar_estilos()
    
    # Iniciar aplicación
    print(f"\n🖥️ Iniciando interfaz gráfica...")
    app = GPSInterface()
    app.run()
    
    print("\n👋 Aplicación finalizada correctamente")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)