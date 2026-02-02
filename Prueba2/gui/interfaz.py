"""
INTERFAZ GRÁFICA - Tkinter
Responsable de: mostrar GUI, recoger entrada usuario
NO contiene: SQL (usa DAO), Dijkstra (usa Algorithm)
Solo coordina capas
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from typing import List, Tuple, Optional
from pathlib import Path

from dao.database import DatabaseManager
from algorithm.dijkstra import dijkstra, ruta_alternativa, es_alternativa_valida


class GPSInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗺️ Sistema GPS - Rutas Óptimas (DAM)")
        self.root.geometry("1200x750")
        self.root.configure(bg='#f8f9fa')

        # Estado de la aplicación
        self.db_manager: Optional[DatabaseManager] = None
        self.nodos: List[str] = []
        self.grafo_distancia = {}
        self.grafo_tiempo = {}
        self.tipo_coste = tk.StringVar(value="distancia")

        # Calculamos rutas absolutas (independientes del directorio de ejecución)
        self.project_root = Path(__file__).resolve().parent.parent  # sube hasta Prueba1
        self.csv_path = self.project_root / "data" / "mapa_gps.csv"

        self._crear_widgets()
        self._inicializar_app()
        
        # Eliminar ventanas fantasma creadas por Tkinter
        self.root.update_idletasks()
        for child in list(self.root.winfo_children()):
            if isinstance(child, tk.Toplevel) or child.winfo_class() == 'Toplevel':
                child.destroy()
        
        # Forzar que la ventana principal sea la única visible
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _crear_widgets(self):
        """Crea todos los elementos visuales de la interfaz"""
        
        # Frame principal (split horizontal: entrada | resultados)
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel izquierdo: Entrada de datos
        self.frame_entrada = ttk.LabelFrame(paned_window, text="📍 Parámetros de Ruta", padding=15)
        paned_window.add(self.frame_entrada, weight=1)

        ttk.Label(self.frame_entrada, text="Origen:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.combo_origen = ttk.Combobox(self.frame_entrada, width=25, state='readonly', font=('Arial', 9))
        self.combo_origen.grid(row=0, column=1, pady=5, padx=(10,0), sticky='ew')

        ttk.Label(self.frame_entrada, text="Destino:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.combo_destino = ttk.Combobox(self.frame_entrada, width=25, state='readonly', font=('Arial', 9))
        self.combo_destino.grid(row=1, column=1, pady=5, padx=(10,0), sticky='ew')

        ttk.Label(self.frame_entrada, text="Intermedio (opcional):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(15,5))
        self.combo_intermedio = ttk.Combobox(self.frame_entrada, width=25, state='readonly', font=('Arial', 9))
        self.combo_intermedio.grid(row=2, column=1, pady=5, padx=(10,0), sticky='ew')

        # Selección de tipo de coste (distancia o tiempo)
        frame_coste = ttk.LabelFrame(self.frame_entrada, text="⚡ Optimizar por:", padding=10)
        frame_coste.grid(row=3, column=0, columnspan=2, sticky='ew', pady=15)

        ttk.Radiobutton(frame_coste, text="📏 Distancia (km)", variable=self.tipo_coste,
                       value='distancia', command=self._cambiar_tipo_coste).pack(anchor='w')
        ttk.Radiobutton(frame_coste, text="⏱️ Tiempo (min)", variable=self.tipo_coste,
                       value='tiempo', command=self._cambiar_tipo_coste).pack(anchor='w', pady=(5,0))

        # Botón principal para calcular
        self.btn_calcular = ttk.Button(self.frame_entrada, text="🚀 CALCULAR RUTA", 
                                      command=self.calcular_ruta, style='Accent.TButton')
        self.btn_calcular.grid(row=4, column=0, columnspan=2, pady=20, sticky='ew')

        # Estado actual
        self.label_estado = ttk.Label(self.frame_entrada, text="🔄 Iniciando...", foreground='orange')
        self.label_estado.grid(row=5, column=0, columnspan=2, pady=10, sticky='w')

        # Configurar que la columna de los combobox se expanda
        self.frame_entrada.columnconfigure(1, weight=1)

        # Panel derecho: Resultados
        self.frame_resultados = ttk.LabelFrame(paned_window, text="📊 Resultados", padding=15)
        paned_window.add(self.frame_resultados, weight=3)

        # Área de texto con scroll para mostrar rutas
        self.text_resultados = scrolledtext.ScrolledText(
            self.frame_resultados, 
            height=30, 
            width=60,
            font=('Consolas', 9),
            bg='#ffffff',
            fg='#2d3748',
            wrap=tk.WORD
        )
        self.text_resultados.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        # Botones de acción
        frame_botones = ttk.Frame(self.frame_resultados)
        frame_botones.pack(fill=tk.X)

        ttk.Button(frame_botones, text="🗑️ Limpiar", command=self.limpiar_resultados).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(frame_botones, text="📋 Copiar", command=self.copiar_resultados).pack(side=tk.LEFT)
        ttk.Button(frame_botones, text="🔄 Recargar Mapa", command=self.recargar_mapa).pack(side=tk.RIGHT)

    def _inicializar_app(self):
        """Inicializa la aplicación: conecta a BD y carga nodos + grafos"""
        try:
            print("\n" + "="*60)
            print("INICIALIZANDO APLICACIÓN")
            print("="*60)
            
            self.label_estado.config(text="📥 Cargando base de datos...", foreground='orange')
            self.root.update()

            # Crear instancia del gestor de base de datos
            self.db_manager = DatabaseManager()
            
            print(f"📍 Ruta CSV: {self.csv_path}")
            print(f"📍 Existe CSV: {self.csv_path.is_file()}")
            
            # FORZAR CARGA DEL CSV SIEMPRE (eliminar datos antiguos)
            self.label_estado.config(text="🗑️  Limpiando datos antiguos...", foreground='orange')
            self.root.update()
            
            # Limpiar base de datos
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM aristas')
            cursor.execute('DELETE FROM nodos')
            cursor.execute('DELETE FROM historico_rutas')
            conn.commit()
            conn.close()
            print("✅ Base de datos limpiada")
            
            # Cargar CSV
            if self.csv_path.is_file():
                self.label_estado.config(text="📥 Cargando mapa desde CSV...", foreground='orange')
                self.root.update()
                
                print(f"📍 Cargando CSV: {self.csv_path}")
                self.db_manager.cargar_csv(str(self.csv_path))
            else:
                messagebox.showerror(
                    "Archivo no encontrado",
                    f"No se encontró: {self.csv_path}\n\nEsperado en: {self.csv_path}"
                )
                print(f"❌ CSV no encontrado en: {self.csv_path}")
                return
            
            # Cargar nodos y construir grafos
            self.nodos = self.db_manager.obtener_nodos()
            
            print(f"\n📊 Nodos cargados: {len(self.nodos)}")
            if self.nodos:
                print(f"   Ejemplos: {self.nodos[:10]}")
            
            if not self.nodos:
                messagebox.showerror("Error", "No se pudieron cargar nodos del CSV")
                print("❌ No se pudieron cargar nodos")
                return
            
            # Construir grafos
            self.label_estado.config(text="🏗️  Construyendo grafos...", foreground='orange')
            self.root.update()
            
            print(f"\n📍 Construyendo grafo distancia...")
            self.grafo_distancia = self.db_manager.construir_grafo('distancia')
            
            print(f"\n📍 Construyendo grafo tiempo...")
            self.grafo_tiempo = self.db_manager.construir_grafo('tiempo')
            
            # Rellenar combobox
            self.combo_origen['values'] = self.nodos
            self.combo_destino['values'] = self.nodos
            self.combo_intermedio['values'] = [''] + self.nodos
            
            if self.nodos:
                self.combo_origen.set(self.nodos[0])
                self.combo_destino.set(self.nodos[1] if len(self.nodos) > 1 else self.nodos[0])
            
            self.label_estado.config(
                text=f"✅ Listo: {len(self.nodos)} nodos cargados",
                foreground='green'
            )
            print(f"✅ Aplicación inicializada correctamente")
            
        except Exception as e:
            self.label_estado.config(text="❌ Error al inicializar", foreground='red')
            import traceback
            error_details = traceback.format_exc()
            print(f"\n❌ ERROR DETALLADO:\n{error_details}")
            messagebox.showerror("Error de inicialización", 
                               f"Error: {str(e)}\n\nVer consola para detalles.")

    def _cambiar_tipo_coste(self):
        """Actualiza el grafo activo según la selección del usuario"""
        pass

    def calcular_ruta(self):
        """Orquestador principal - coordina DAO + Algorithm + GUI"""
        try:
            # Obtener valores seleccionados por el usuario
            origen = self.combo_origen.get().strip()
            destino = self.combo_destino.get().strip()
            intermedio = self.combo_intermedio.get().strip() or None

            # Validaciones básicas de entrada
            if not origen or not destino:
                messagebox.showwarning("⚠️ Datos incompletos", "Selecciona origen y destino")
                return

            if origen == destino:
                messagebox.showinfo("ℹ️ Información", "Origen y destino son iguales")
                return

            # Actualizar estado visual
            self.label_estado.config(text="🔍 Calculando ruta...", foreground='blue')
            self.root.update()

            # Seleccionar el grafo según el tipo de coste elegido por el usuario
            grafo_activo = self.grafo_distancia if self.tipo_coste.get() == 'distancia' else self.grafo_tiempo

            # 1. Intentar recuperar ruta desde caché (histórico)
            historico = self.db_manager.buscar_historico(origen, destino)
            if historico is not None:
                # Comprobación de seguridad: debe ser tupla de exactamente 2 elementos
                if isinstance(historico, tuple) and len(historico) == 2:
                    coste, ruta = historico
                    unidad = "km" if self.tipo_coste.get() == 'distancia' else "min"
                    self._mostrar_resultado(
                        origen, destino, coste, ruta, unidad, desde_historico=True
                    )
                    self.label_estado.config(text="✅ Ruta recuperada desde caché", foreground='green')
                    return
                else:
                    print("Advertencia: histórico corrupto o formato inesperado → ignorando caché")

            # 2. Si no hay caché → calcular ruta nueva con Dijkstra
            intermedios = [intermedio] if intermedio else []
            print(f"\n📍 Calculando ruta: {origen} → {destino}")
            coste, ruta = dijkstra(grafo_activo, origen, destino, intermedios)

            # Determinar unidad según el tipo de coste seleccionado
            unidad = "km" if self.tipo_coste.get() == 'distancia' else "min"

            # Si no hay ruta posible
            if coste == float('inf'):
                self._mostrar_error("No existe ruta posible entre estos puntos")
                self.label_estado.config(text="⚠️ Ruta no encontrada", foreground='orange')
                return

            # 3. Mostrar la ruta óptima calculada
            self._mostrar_resultado(origen, destino, coste, ruta, unidad)

            # 4. Intentar encontrar y mostrar una ruta alternativa (si existe)
            alternativa = ruta_alternativa(grafo_activo, origen, destino, coste)
            if alternativa and es_alternativa_valida(coste, alternativa[0]):
                # Guardar la alternativa en el histórico
                self.db_manager.guardar_ruta(
                    origen, destino, alternativa[0],
                    self.tipo_coste.get(), alternativa[1], True
                )
                self._mostrar_alternativa(alternativa[0], alternativa[1], coste, unidad)

            # 5. Guardar la ruta óptima en el histórico
            self.db_manager.guardar_ruta(
                origen, destino, coste,
                self.tipo_coste.get(), ruta
            )

            # Actualizar estado final
            self.label_estado.config(text="✅ Ruta calculada y guardada", foreground='green')

        except ValueError as ve:
            # Errores comunes de unpacking o conversión
            self.label_estado.config(text="❌ Error en datos o formato", foreground='red')
            messagebox.showerror("Error de datos", f"Problema con los valores:\n{str(ve)}")

        except Exception as e:
            # Captura general de cualquier otro error
            self.label_estado.config(text="❌ Error en cálculo", foreground='red')
            messagebox.showerror("Error", f"Error al calcular la ruta:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def _mostrar_resultado(self, origen: str, destino: str, coste: float, 
                          ruta: List[str], unidad: str, desde_historico: bool = False):
        """Muestra la ruta óptima en formato legible"""
        texto = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    RUTA ÓPTIMA {'(desde caché)' if desde_historico else ''} ║
╚═══════════════════════════════════════════════════════════════╝

📍 ORIGEN:     {origen}
📍 DESTINO:    {destino}
📍 INTERMEDIOS: {'Ninguno' if not ruta[1:-1] else ' → '.join(ruta[1:-1])}

✅ COSTE TOTAL: {coste:.2f} {unidad}

🛣️  RUTA COMPLETA ({len(ruta)-1} tramos):
"""
        
        for i, nodo in enumerate(ruta):
            flecha = " → " if i < len(ruta)-1 else ""
            texto += f"  {i+1:2d}. {nodo:<20}{flecha}\n"
        
        texto += f"\n📊 RESUMEN: {len(ruta)-1} tramos, {coste:.2f} {unidad}"
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, texto)

    def _mostrar_alternativa(self, coste_alt: float, ruta_alt: List[str], 
                            coste_optimo: float, unidad: str):
        """Muestra información sobre la ruta alternativa"""
        diferencia = ((coste_alt - coste_optimo) / coste_optimo) * 100
        
        texto = f"""
╔═══════════════════════════════════════════════════════════════╗
║                 RUTA ALTERNATIVA DISPONIBLE (±15%)           ║
╚═══════════════════════════════════════════════════════════════╝

⚠️  COSTE:     {coste_alt:.2f} {unidad}
📈 DIFERENCIA: {diferencia:+.1f}% ({coste_alt-coste_optimo:+.2f} {unidad})

🛣️  RUTA ALTERNATIVA ({len(ruta_alt)-1} tramos):
"""
        
        for i, nodo in enumerate(ruta_alt):
            flecha = " → " if i < len(ruta_alt)-1 else ""
            texto += f"  {i+1:2d}. {nodo:<20}{flecha}\n"
        
        self.text_resultados.insert(tk.END, texto)

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error en el área de resultados"""
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, f"❌ {mensaje}\n\n")
        self.text_resultados.insert(tk.END, "💡 Prueba con otros nodos o verifica la conexión.")

    def limpiar_resultados(self):
        """Borra todo el contenido del área de resultados"""
        self.text_resultados.delete(1.0, tk.END)

    def copiar_resultados(self):
        """Copia el contenido del área de resultados al portapapeles"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_resultados.get(1.0, tk.END))
        messagebox.showinfo("Copiado", "¡Resultados copiados al portapapeles!")

    def recargar_mapa(self):
        """Recarga los datos desde el archivo CSV (botón 'Recargar Mapa')"""
        if not self.db_manager:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return

        self.label_estado.config(text="🔄 Recargando mapa...", foreground='orange')
        self.root.update()

        if not self.csv_path.is_file():
            messagebox.showerror("Archivo no encontrado", 
                               f"No se encuentra el mapa en:\n{self.csv_path}")
            return

        try:
            # Forzamos recarga (sobrescribe datos existentes)
            self.db_manager.cargar_csv(str(self.csv_path))

            # Volvemos a cargar nodos y grafos
            self.nodos = self.db_manager.obtener_nodos()
            self.grafo_distancia = self.db_manager.construir_grafo('distancia')
            self.grafo_tiempo = self.db_manager.construir_grafo('tiempo')

            # Actualizamos los combobox
            self.combo_origen['values'] = self.nodos
            self.combo_destino['values'] = self.nodos
            self.combo_intermedio['values'] = [''] + self.nodos

            self.label_estado.config(
                text=f"🔄 Mapa recargado: {len(self.nodos)} nodos",
                foreground='green'
            )
            messagebox.showinfo("Éxito", f"Mapa recargado correctamente.\n{len(self.nodos)} nodos cargados.")

        except Exception as e:
            self.label_estado.config(text="❌ Error al recargar mapa", foreground='red')
            messagebox.showerror("Error", f"No se pudo recargar el mapa:\n{str(e)}")

    def run(self):
        """Inicia el bucle principal de la interfaz gráfica"""
        self.root.mainloop()


# Configurar estilos globales de la aplicación
def configurar_estilos():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))