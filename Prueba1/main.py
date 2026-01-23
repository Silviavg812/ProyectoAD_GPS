#!/usr/bin/env python3
"""
PUNTO DE ENTRADA PRINCIPAL
Ejecuta: python main.py
"""

import sys
from pathlib import Path

# Asegurar que el path incluye el proyecto raíz
sys.path.insert(0, str(Path(__file__).parent))

from main.app import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)
