# test_tkinter.py
import sys

print("=" * 50)
print("DIAGNÓSTICO DE TKINTER")
print("=" * 50)

print(f"\n1. Versión de Python: {sys.version}")
print(f"2. Ejecutable: {sys.executable}")

try:
    import tkinter as tk
    print("\n3. ✅ tkinter importado correctamente")
    print(f"4. Versión de Tcl/Tk: {tk.TclVersion}")
    
    # Crear ventana de prueba
    root = tk.Tk()
    root.title("Test tkinter")
    tk.Label(root, text="✅ Tkinter funciona!").pack(padx=20, pady=20)
    tk.Button(root, text="Cerrar", command=root.destroy).pack(pady=10)
    
    print("5. ✅ Ventana de prueba creada")
    print("\nPresiona el botón 'Cerrar' en la ventana")
    
    root.mainloop()
    
except ImportError as e:
    print(f"\n3. ❌ ERROR: No se pudo importar tkinter")
    print(f"   Detalle: {e}")
    print("\nSOLUCIÓN:")
    print("- Linux: sudo apt-get install python3-tk")
    print("- macOS: brew install python-tk")
    print("- Windows: Reinstalar Python desde python.org")

except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 50)
