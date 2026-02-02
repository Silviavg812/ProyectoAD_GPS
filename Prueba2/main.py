#!/usr/bin/env python3
"""
PUNTO DE ENTRADA PRINCIPAL
Ejecuta: python main.py
"""

import sys
from pathlib import Path

# Asegurar que el path incluye el proyecto raíz
sys.path.insert(0, str(Path(__file__).parent))

from gui.interfaz import GPSInterface

if __name__ == "__main__":
    try:
        print("="*60)
        print("🗺️  SISTEMA GPS - RUTAS ÓPTIMAS")
        print("="*60)
        
        # Configurar estilos
        from gui.interfaz import configurar_estilos
        configurar_estilos()
        
        # Iniciar interfaz
        app = GPSInterface()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)