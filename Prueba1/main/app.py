"""
APLICACIÓN PRINCIPAL - Punto de entrada
Coordina: DAO + Algorithm + GUI
"""

from pathlib import Path
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.interfaz import GPSInterface, configurar_estilos
from dao.database import DatabaseManager

def main():
    """Función principal de la aplicación"""
    print("🚀 Iniciando Sistema GPS con Dijkstra...")
    print("📊 Proyecto Final DAM - Estructuras de Datos")
    
    # Configurar estilos GUI
    configurar_estilos()
    
    # Crear y ejecutar interfaz
    app = GPSInterface()
    app.run()
    
    print("👋 Aplicación finalizada")

if __name__ == "__main__":
    main()
