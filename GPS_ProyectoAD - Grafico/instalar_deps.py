"""
Script para instalar automáticamente las dependencias que faltan
"""

import subprocess
import sys

def instalar_dependencias():
    """
    Instala matplotlib y networkx en el Python actual
    """
    print("=" * 60)
    print("INSTALADOR DE DEPENDENCIAS GPS")
    print("=" * 60)
    
    print(f"\nPython detectado: {sys.executable}")
    print(f"Versión: {sys.version}\n")
    
    dependencias = ["matplotlib", "networkx"]
    
    for dep in dependencias:
        print(f"📦 Instalando {dep}...")
        try:
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                dep
            ])
            print(f"✅ {dep} instalado correctamente\n")
        except Exception as e:
            print(f"❌ Error instalando {dep}: {e}\n")
    
    # Verificar
    print("\n" + "=" * 60)
    print("VERIFICACIÓN")
    print("=" * 60)
    
    try:
        import matplotlib
        import networkx
        print("✅ matplotlib instalado - Versión:", matplotlib.__version__)
        print("✅ networkx instalado - Versión:", networkx.__version__)
        print("\n🎉 ¡Todas las dependencias instaladas correctamente!")
        print("\nAhora puedes ejecutar: python gui.py")
    except ImportError as e:
        print(f"❌ Aún hay problemas: {e}")
        print("\nIntenta manualmente:")
        print(f"  {sys.executable} -m pip install matplotlib networkx")

if __name__ == "__main__":
    instalar_dependencias()