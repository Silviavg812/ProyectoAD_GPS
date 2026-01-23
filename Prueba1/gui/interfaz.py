"""
INTERFAZ GRÁFICA - Tkinter
Responsable de: mostrar GUI, recoger entrada usuario
NO contiene: SQL (usa DAO), Dijkstra (usa Algorithm)
Solo coordina capas
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Tuple, Optional
import os

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
        
        self._crear_widgets()
        self._inicializar_app()
    
    def _crear_widgets(self):
        """Crea toda la interfaz gráfica"""
        
        # Frame principal (split horizontal)
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
        
        # Selección de tipo de coste
        frame_coste = ttk.LabelFrame(self.frame_entrada, text="⚡ Optimizar por:", padding=10)
        frame_coste.grid(row=3, column=0, columnspan=2, sticky='ew', pady=15)
        
        ttk.Radiobutton(frame_coste, text="📏 Distancia (km)", variable=self.tipo_coste,
                       value='distancia', command=self._cambiar_tipo_coste).pack(anchor='w')
        ttk.Radiobutton(frame_coste, text="⏱️ Tiempo (min)", variable=self.tipo_coste,
                       value='tiempo', command=self._cambiar_tipo_coste).pack(anchor='w', pady=(5,0))
        
        # Botón principal
        self.btn_calcular = ttk.Button(self.frame_entrada, text="🚀 CALCULAR RUTA", 
                                      command=self.calcular_ruta, style='Accent.TButton')
        self.btn_calcular.grid(row=4, column=0, columnspan=2, pady=20, sticky='ew')
        
        # Estado
        self.label_estado = ttk.Label(self.frame_entrada, text="🔄 Iniciando...", foreground='orange')
        self.label_estado.grid(row=5, column=0, columnspan=2, pady=10, sticky='w')
        
        # Configurar grid weights
        self.frame_entrada.columnconfigure(1, weight=1)
        
        # Panel derecho: Resultados
        self.frame_resultados = ttk.LabelFrame(paned_window, text="📊 Resultados", padding=15)
        paned_window.add(self.frame_resultados, weight=3)
        
        # Área de texto scrollable
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
        """Inicialización completa de la aplicación"""
        try:
            self.label_estado.config(text="📥 Cargando base de datos...", foreground='orange')
            self.root.update()
            
            # Inicializar DAO
            self.db_manager = DatabaseManager()
            
            # Cargar datos
            self.db_manager.cargar_csv()
            
            # Obtener nodos y construir grafos
            self.nodos = self.db_manager.obtener_nodos()
            self.grafo_distancia = self.db_manager.construir_grafo('distancia')
            self.grafo_tiempo = self.db_manager.construir_grafo('tiempo')
            
            # Configurar combobox
            self.combo_origen['values'] = self.nodos
            self.combo_destino['values'] = self.nodos
            self.combo_intermedio['values'] = [''] + self.nodos
            
            self.label_estado.config(text=f"✅ Listo: {len(self.nodos)} nodos, {len(self.grafo_distancia)} rutas", 
                                   foreground='green')
            
        except Exception as e:
            self.label_estado.config(text="❌ Error de inicialización", foreground='red')
            messagebox.showerror("Error", f"No se pudo inicializar:\n{str(e)}")
    
    def _cambiar_tipo_coste(self):
        """Cambia grafo activo según tipo de coste"""
        tipo = self.tipo_coste.get()
        self.grafo_activo = self.grafo_distancia if tipo == 'distancia' else self.grafo_tiempo
    
    def calcular_ruta(self):
        """Orquestador principal - coordina DAO + Algorithm + GUI"""
        try:
            origen = self.combo_origen.get().strip()
            destino = self.combo_destino.get().strip()
            intermedio = self.combo_intermedio.get().strip() or None
            
            if not origen or not destino:
                messagebox.showwarning("⚠️ Datos incompletos", "Selecciona origen y destino")
                return
            
            if origen == destino:
                messagebox.showinfo("ℹ️ Información", "Origen y destino son iguales")
                return
            
            self.label_estado.config(text="🔍 Calculando ruta...", foreground='blue')
            self.root.update()
            
            # Buscar en histórico primero (caché)
            historico = self.db_manager.buscar_historico(origen, destino)
            if historico:
                coste, ruta = historico
                unidad = "km" if self.tipo_coste.get() == 'distancia' else "min"
                self._mostrar_resultado(origen, destino, coste, ruta, unidad, desde_historico=True)
                return
            
            # Calcular ruta nueva
            intermedios = [intermedio] if intermedio else []
            coste, ruta = dijkstra(self.grafo_activo, origen, destino, intermedios)
            
            unidad = "km" if self.tipo_coste.get() == 'distancia' else "min"
            
            if coste == float('inf'):
                self._mostrar_error("No existe ruta posible")
                return
            
            # Mostrar resultado principal
            self._mostrar_resultado(origen, destino, coste, ruta, unidad)
            
            # Calcular y mostrar alternativa
            alternativa = ruta_alternativa(self.grafo_activo, origen, destino, coste)
            if alternativa and es_alternativa_valida(coste, alternativa[0]):
                self.db_manager.guardar_ruta(origen, destino, alternativa[0], 
                                           self.tipo_coste.get(), alternativa[1], True)
                self._mostrar_alternativa(alternativa[0], alternativa[1], coste, unidad)
            
            # Guardar ruta óptima en histórico
            self.db_manager.guardar_ruta(origen, destino, coste, 
                                       self.tipo_coste.get(), ruta)
            
            self.label_estado.config(text="✅ Ruta calculada y guardada", foreground='green')
            
        except Exception as e:
            self.label_estado.config(text="❌ Error en cálculo", foreground='red')
            messagebox.showerror("Error", f"Error al calcular ruta:\n{str(e)}")
    
    def _mostrar_resultado(self, origen: str, destino: str, coste: float, 
                          ruta: List[str], unidad: str, desde_historico: bool = False):
        """Muestra ruta óptima formateada"""
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
        """Muestra ruta alternativa"""
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
        """Muestra mensaje de error"""
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, f"❌ {mensaje}\n\n")
        self.text_resultados.insert(tk.END, "💡 Prueba con otros nodos o verifica la conexión.")
    
    def limpiar_resultados(self):
        """Limpia área de resultados"""
        self.text_resultados.delete(1.0, tk.END)
    
    def copiar_resultados(self):
        """Copia texto al portapapeles"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text_resultados.get(1.0, tk.END))
        messagebox.showinfo("Copiado", "¡Resultados copiados al portapapeles!")
    
    def recargar_mapa(self):
        """Recarga datos desde CSV"""
        if self.db_manager:
            self.db_manager.cargar_csv()
            self._inicializar_app()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# Configurar estilos
def configurar_estilos():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
