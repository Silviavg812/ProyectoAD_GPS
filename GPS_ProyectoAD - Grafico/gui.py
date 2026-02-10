import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional
import sys
import os
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.sqlite_dao import SqliteDAO
from src.graph_from_dao import DAOGraphAdapter
from src.routing import route_with_stops, second_shortest_path_yen, choose_alternative_if_close
from src.dijkstra import PathResult


class HistoricoWindow:
    """Ventana modal para mostrar el histórico de rutas calculadas"""
    
    def __init__(self, parent, dao: SqliteDAO):
        self.window = tk.Toplevel(parent)
        self.window.title("📜 Histórico de Rutas")
        self.window.geometry("900x550")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.dao = dao
        
        self.create_widgets()
        self.cargar_historico()
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f5f5f5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(
            main_frame,
            text="📜 Histórico de Rutas Calculadas",
            font=('Arial', 14, 'bold'),
            bg='#f5f5f5',
            fg='#333'
        )
        title.pack(pady=(0, 15))
        
        # Frame de la tabla
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview (tabla)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Origen", "Destino", "Coste", "Fecha", "Alternativa"),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Origen", text="Origen")
        self.tree.heading("Destino", text="Destino")
        self.tree.heading("Coste", text="Coste")
        self.tree.heading("Fecha", text="Fecha/Hora")
        self.tree.heading("Alternativa", text="Alternativa")
        
        self.tree.column("ID", width=50, anchor='center')
        self.tree.column("Origen", width=80, anchor='center')
        self.tree.column("Destino", width=80, anchor='center')
        self.tree.column("Coste", width=80, anchor='center')
        self.tree.column("Fecha", width=180, anchor='center')
        self.tree.column("Alternativa", width=100, anchor='center')
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de botones
        buttons_frame = tk.Frame(main_frame, bg='#f5f5f5')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Botón ver detalles
        btn_detalles = tk.Button(
            buttons_frame,
            text="👁️ Ver Detalles",
            font=('Arial', 10),
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.ver_detalles
        )
        btn_detalles.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón limpiar histórico
        btn_limpiar = tk.Button(
            buttons_frame,
            text="🗑️ Limpiar Histórico",
            font=('Arial', 10),
            bg='#f44336',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.limpiar_historico
        )
        btn_limpiar.pack(side=tk.LEFT)
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            buttons_frame,
            text="✖️ Cerrar",
            font=('Arial', 10),
            bg='#757575',
            fg='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.window.destroy
        )
        btn_cerrar.pack(side=tk.RIGHT)
    
    def cargar_historico(self):
        """Carga las rutas del histórico desde la base de datos"""
        try:
            conn = sqlite3.connect("data/gps.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, origin, destination, cost, fecha, eligio_alternativa
                FROM historico
                ORDER BY fecha DESC
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insertar datos
            for row in rows:
                id_val, origin, dest, coste, fecha, alt = row
                alt_text = "Sí" if alt == 1 else "No"
                
                # Formatear fecha
                try:
                    fecha_obj = datetime.fromisoformat(fecha)
                    fecha_format = fecha_obj.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    fecha_format = fecha
                
                self.tree.insert("", tk.END, values=(
                    id_val, origin, dest, f"{coste:.2f}", fecha_format, alt_text
                ))
            
            if not rows:
                messagebox.showinfo(
                    "Histórico Vacío",
                    "No hay rutas guardadas en el histórico."
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar histórico:\n{e}")
    
    def ver_detalles(self):
        """Muestra los detalles completos de la ruta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecciona una ruta primero.")
            return
        
        item = self.tree.item(selection[0])
        id_ruta = item['values'][0]
        
        try:
            conn = sqlite3.connect("data/gps.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT origin, destination, coste_total, camino, fecha, eligio_alternativa
                FROM historico
                WHERE id = ?
            """, (id_ruta,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                origin, dest, coste, camino, fecha, alt = row
                alt_text = "Sí (eligió alternativa)" if alt == 1 else "No (eligió óptima)"
                
                mensaje = f"""
DETALLES DE LA RUTA

ID: {id_ruta}
Origen: {origin}
Destino: {dest}
Coste Total: {coste}

Camino Completo:
{camino.replace(',', ' → ')}

Fecha: {fecha}
Alternativa: {alt_text}
                """
                
                messagebox.showinfo("Detalles de Ruta", mensaje)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener detalles:\n{e}")
    
    def limpiar_historico(self):
        """Limpia todo el histórico tras confirmación"""
        respuesta = messagebox.askyesno(
            "Confirmar",
            "¿Estás seguro de que quieres eliminar TODO el histórico?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                conn = sqlite3.connect("data/gps.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM historico")
                conn.commit()
                conn.close()
                
                self.cargar_historico()
                messagebox.showinfo("Éxito", "Histórico eliminado correctamente.")
            
            except Exception as e:
                messagebox.showerror("Error", f"Error al limpiar histórico:\n{e}")


class GPSSimulatorGUI:
    """Interfaz gráfica principal del simulador GPS"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🗺️ Simulador GPS - Dijkstra")
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        
        # Configurar estilo
        self.setup_style()
        
        # Variables
        self.dao: Optional[SqliteDAO] = None
        self.graph: Optional[DAOGraphAdapter] = None
        self.last_best_result: Optional[PathResult] = None
        self.last_alt_result: Optional[PathResult] = None
        
        # Inicializar base de datos
        self.init_database()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar estadísticas iniciales
        self.load_statistics()
    
    def setup_style(self):
        """Configura los estilos visuales de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del sistema
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.warning_color = "#FF9800"
        self.error_color = "#f44336"
        self.visualize_color = "#00BCD4"
        
        self.root.configure(bg=self.bg_color)
        
        # Estilos personalizados
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background=self.bg_color,
                       foreground='#333')
    
    def init_database(self):
        """Inicializa la base de datos y el grafo"""
        try:
            self.dao = SqliteDAO("data/gps.db")
            self.dao.cargar_desde_csv("data/edges_laberinto.csv")
            self.graph = DAOGraphAdapter(self.dao)
        except Exception as e:
            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo inicializar la base de datos:\n{e}\n\n"
                f"Verifica que existan:\n"
                f"- Carpeta 'data/'\n"
                f"- Archivo 'data/edges_laberinto.csv'"
            )
            self.root.destroy()
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Frame principal con padding
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="🗺️ Simulador GPS - Algoritmo de Dijkstra",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de estadísticas
        self.create_stats_frame(main_frame)
        
        # Frame de entrada
        self.create_input_frame(main_frame)
        
        # Frame de botones
        self.create_buttons_frame(main_frame)
        
        # Frame de resultados
        self.create_results_frame(main_frame)
    
    def create_stats_frame(self, parent):
        """Crea el frame con estadísticas del grafo"""
        stats_frame = tk.LabelFrame(
            parent,
            text="📊 Estadísticas del Grafo",
            bg=self.bg_color,
            font=('Arial', 10, 'bold'),
            fg='#333'
        )
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg=self.bg_color)
        stats_grid.pack(padx=10, pady=10)
        
        self.stats_labels = {}
        stats_info = [
            ("nodos", "Nodos:"),
            ("aristas", "Aristas:"),
            ("unidireccionales", "Unidireccionales:"),
            ("bidireccionales", "Bidireccionales:")
        ]
        
        for i, (key, label_text) in enumerate(stats_info):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(
                stats_grid,
                text=label_text,
                font=('Arial', 9, 'bold'),
                bg=self.bg_color,
                fg='#555'
            ).grid(row=row, column=col, sticky='e', padx=(0, 5), pady=2)
            
            value_label = tk.Label(
                stats_grid,
                text="0",
                font=('Arial', 9),
                bg=self.bg_color,
                fg='#333'
            )
            value_label.grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=2)
            self.stats_labels[key] = value_label
    
    def create_input_frame(self, parent):
        """Crea el frame de entrada de datos"""
        input_frame = tk.LabelFrame(
            parent,
            text="📍 Configuración de Ruta",
            bg=self.bg_color,
            font=('Arial', 10, 'bold'),
            fg='#333'
        )
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid de inputs
        input_grid = tk.Frame(input_frame, bg=self.bg_color)
        input_grid.pack(padx=10, pady=10)
        
        # Origen
        tk.Label(
            input_grid,
            text="🚩 Origen:",
            font=('Arial', 10),
            bg=self.bg_color,
            fg='#333'
        ).grid(row=0, column=0, sticky='e', padx=(0, 10), pady=8)
        
        self.entry_origen = ttk.Entry(input_grid, width=10, font=('Arial', 10))
        self.entry_origen.grid(row=0, column=1, sticky='w', pady=8)
        
        tk.Label(
            input_grid,
            text="(nodo 0-40)",
            font=('Arial', 8),
            bg=self.bg_color,
            fg='#999'
        ).grid(row=0, column=2, sticky='w', padx=(5, 0), pady=8)
        
        # Destino
        tk.Label(
            input_grid,
            text="🏁 Destino:",
            font=('Arial', 10),
            bg=self.bg_color,
            fg='#333'
        ).grid(row=1, column=0, sticky='e', padx=(0, 10), pady=8)
        
        self.entry_destino = ttk.Entry(input_grid, width=10, font=('Arial', 10))
        self.entry_destino.grid(row=1, column=1, sticky='w', pady=8)
        
        tk.Label(
            input_grid,
            text="(nodo 0-40)",
            font=('Arial', 8),
            bg=self.bg_color,
            fg='#999'
        ).grid(row=1, column=2, sticky='w', padx=(5, 0), pady=8)
        
        # Intermedios
        tk.Label(
            input_grid,
            text="📌 Intermedios:",
            font=('Arial', 10),
            bg=self.bg_color,
            fg='#333'
        ).grid(row=2, column=0, sticky='e', padx=(0, 10), pady=8)
        
        self.entry_intermedios = ttk.Entry(input_grid, width=30, font=('Arial', 10))
        self.entry_intermedios.grid(row=2, column=1, columnspan=2, sticky='w', pady=8)
        
        tk.Label(
            input_grid,
            text="(opcional, separados por comas: 5,10,15)",
            font=('Arial', 8),
            bg=self.bg_color,
            fg='#999'
        ).grid(row=3, column=1, columnspan=2, sticky='w', pady=(0, 8))
    
    def create_buttons_frame(self, parent):
        """Crea el frame con los botones de acción"""
        buttons_frame = tk.Frame(parent, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Fila 1: Botones principales
        row1 = tk.Frame(buttons_frame, bg=self.bg_color)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        # Botón calcular ruta
        self.btn_calcular = tk.Button(
            row1,
            text="🔍 Calcular Ruta Óptima",
            font=('Arial', 11, 'bold'),
            bg=self.primary_color,
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.calcular_ruta
        )
        self.btn_calcular.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón limpiar
        self.btn_limpiar = tk.Button(
            row1,
            text="🗑️ Limpiar",
            font=('Arial', 10),
            bg='#757575',
            fg='white',
            activebackground='#616161',
            activeforeground='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=10,
            command=self.limpiar_campos
        )
        self.btn_limpiar.pack(side=tk.LEFT)
        
        # Fila 2: Botones secundarios
        row2 = tk.Frame(buttons_frame, bg=self.bg_color)
        row2.pack(fill=tk.X)
        
        # Botón visualizar grafo
        self.btn_visualizar = tk.Button(
            row2,
            text="🎨 Visualizar Grafo",
            font=('Arial', 10),
            bg=self.visualize_color,
            fg='white',
            activebackground='#0097A7',
            activeforeground='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.visualizar_grafo
        )
        self.btn_visualizar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón histórico
        self.btn_historico = tk.Button(
            row2,
            text="📜 Ver Histórico",
            font=('Arial', 10),
            bg='#9C27B0',
            fg='white',
            activebackground='#7B1FA2',
            activeforeground='white',
            cursor='hand2',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.ver_historico
        )
        self.btn_historico.pack(side=tk.LEFT)
    
    def create_results_frame(self, parent):
        """Crea el frame de resultados"""
        results_frame = tk.LabelFrame(
            parent,
            text="📊 Resultados",
            bg=self.bg_color,
            font=('Arial', 10, 'bold'),
            fg='#333'
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scroll
        self.text_resultados = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#2b2b2b',
            fg='#f5f5f5',
            insertbackground='white',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tags para colores en el texto
        self.text_resultados.tag_config('success', foreground='#4CAF50', font=('Consolas', 9, 'bold'))
        self.text_resultados.tag_config('warning', foreground='#FF9800', font=('Consolas', 9, 'bold'))
        self.text_resultados.tag_config('error', foreground='#f44336', font=('Consolas', 9, 'bold'))
        self.text_resultados.tag_config('info', foreground='#2196F3', font=('Consolas', 9, 'bold'))
        self.text_resultados.tag_config('title', foreground='#FFD700', font=('Consolas', 10, 'bold'))
    
    def load_statistics(self):
        """Carga las estadísticas del grafo desde la base de datos"""
        if not self.dao:
            return
        
        try:
            conn = sqlite3.connect("data/gps.db")
            cursor = conn.cursor()
            
            # Contar nodos
            cursor.execute("SELECT COUNT(*) FROM nodos")
            num_nodos = cursor.fetchone()[0]
            
            # Contar aristas
            cursor.execute("SELECT COUNT(*) FROM aristas")
            num_aristas = cursor.fetchone()[0]
            
            # Contar unidireccionales
            cursor.execute("""
                SELECT COUNT(*) FROM aristas a1
                WHERE NOT EXISTS (
                    SELECT 1 FROM aristas a2 
                    WHERE a2.origin = a1.destination 
                    AND a2.destination = a1.origin
                )
            """)
            num_uni = cursor.fetchone()[0]
            
            conn.close()
            
            # Actualizar labels
            self.stats_labels['nodos'].config(text=str(num_nodos))
            self.stats_labels['aristas'].config(text=str(num_aristas))
            self.stats_labels['unidireccionales'].config(text=str(num_uni))
            self.stats_labels['bidireccionales'].config(text=str((num_aristas - num_uni) // 2))
            
        except Exception as e:
            print(f"Error al cargar estadísticas: {e}")
    
    def calcular_ruta(self):
        """Calcula la ruta óptima y muestra resultados"""
        # Limpiar resultados anteriores
        self.text_resultados.delete(1.0, tk.END)
        
        try:
            # Validar y obtener datos
            origen = int(self.entry_origen.get().strip())
            destino = int(self.entry_destino.get().strip())
            
            intermedios_str = self.entry_intermedios.get().strip()
            intermedios = []
            if intermedios_str:
                intermedios = [int(x.strip()) for x in intermedios_str.split(',')]
            
            # Validar rango
            if not (0 <= origen <= 39) or not (0 <= destino <= 39):
                raise ValueError("Los nodos deben estar entre 0 y 39")
            
            for inter in intermedios:
                if not (0 <= inter <= 39):
                    raise ValueError(f"Nodo intermedio {inter} fuera de rango (0-39)")
            
            # Validar origen != destino
            if origen == destino:
                self.append_text("⚠️  Origen y destino son iguales (coste = 0)\n", 'warning')
                return
            
            self.append_text("=" * 60 + "\n", 'title')
            self.append_text("🔍 CALCULANDO RUTA ÓPTIMA\n", 'title')
            self.append_text("=" * 60 + "\n\n", 'title')
            
            # Buscar en histórico si no hay intermedios
            if not intermedios:
                self.append_text("📜 Buscando en histórico...\n", 'info')
                historico = self.dao.buscar_en_historico(origen, destino)
                
                if historico:
                    coste, camino = historico
                    self.append_text("✅ ¡Ruta encontrada en histórico!\n\n", 'success')
                    self.append_text(f"💰 Coste total: {coste}\n", 'success')
                    self.append_text(f"🛣️  Camino: {' → '.join(map(str, camino))}\n", 'info')
                    self.append_text(f"📏 Longitud: {len(camino)} nodos\n", 'info')
                    
                    # Guardar resultado para visualización
                    from src.dijkstra import PathResult
                    self.last_best_result = PathResult(path=camino, cost=coste)
                    return
                else:
                    self.append_text("ℹ️  No encontrado en histórico. Calculando...\n\n", 'info')
            
            # Calcular ruta
            resultado = route_with_stops(self.graph, origen, intermedios, destino)
            
            if resultado is None:
                self.append_text("❌ No existe ruta posible\n", 'error')
                return
            
            self.last_best_result = resultado
            
            # Mostrar resultado
            self.append_text("✅ RUTA ÓPTIMA ENCONTRADA\n\n", 'success')
            self.append_text(f"💰 Coste total: {resultado.cost}\n", 'success')
            self.append_text(f"🛣️  Camino: {' → '.join(map(str, resultado.path))}\n", 'info')
            self.append_text(f"📏 Longitud: {len(resultado.path)} nodos\n\n", 'info')
            
            # Guardar en histórico
            if not intermedios:
                self.dao.guardar_ruta(origen, destino, resultado.cost, resultado.path, False)
                self.append_text("💾 Ruta guardada en histórico\n\n", 'info')
            
            # Buscar alternativa
            if not intermedios:
                self.append_text("🔄 Buscando ruta alternativa...\n", 'info')
                alt = second_shortest_path_yen(self.graph, origen, destino)
                
                if choose_alternative_if_close(resultado, alt, 0.15):
                    self.last_alt_result = alt
                    diff_pct = ((alt.cost - resultado.cost) / resultado.cost * 100)
                    
                    self.append_text("\n" + "=" * 60 + "\n", 'warning')
                    self.append_text("⚡ RUTA ALTERNATIVA DISPONIBLE (≤15%)\n", 'warning')
                    self.append_text("=" * 60 + "\n\n", 'warning')
                    self.append_text(f"💰 Coste: {alt.cost}\n", 'warning')
                    self.append_text(f"🛣️  Camino: {' → '.join(map(str, alt.path))}\n", 'info')
                    self.append_text(f"📊 Diferencia: +{diff_pct:.1f}%\n", 'warning')
                    
                    # Preguntar si quiere usar alternativa
                    respuesta = messagebox.askyesno(
                        "Ruta Alternativa",
                        f"¿Deseas usar la ruta alternativa?\n\n"
                        f"Coste: {alt.cost} (+{diff_pct:.1f}%)\n"
                        f"Camino: {' → '.join(map(str, alt.path[:5]))}..."
                    )
                    
                    if respuesta:
                        self.dao.guardar_ruta(origen, destino, alt.cost, alt.path, True)
                        self.append_text("\n✅ Ruta alternativa seleccionada\n", 'success')
                    else:
                        self.append_text("\n✅ Manteniendo ruta óptima\n", 'info')
                else:
                    self.append_text("ℹ️  No hay alternativa válida (≤15%)\n", 'info')
        
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular ruta:\n{e}")
    
    def append_text(self, text: str, tag: str = None):
        """Añade texto al área de resultados con formato opcional"""
        if tag:
            self.text_resultados.insert(tk.END, text, tag)
        else:
            self.text_resultados.insert(tk.END, text)
        self.text_resultados.see(tk.END)
    
    def limpiar_campos(self):
        """Limpia todos los campos de entrada y resultados"""
        self.entry_origen.delete(0, tk.END)
        self.entry_destino.delete(0, tk.END)
        self.entry_intermedios.delete(0, tk.END)
        self.text_resultados.delete(1.0, tk.END)
        self.last_best_result = None
        self.last_alt_result = None
    
    def ver_historico(self):
        """Abre la ventana de histórico"""
        HistoricoWindow(self.root, self.dao)
    
    def visualizar_grafo(self):
        """Visualiza el grafo con matplotlib usando la última ruta calculada"""
        try:
            # Importar módulo de visualización
            from visualizar_grafo import visualizar_grafo
            
            if self.last_best_result:
                # Visualizar con la ruta calculada
                self.append_text("\n🎨 Abriendo visualización del grafo...\n", 'info')
                visualizar_grafo(
                    db_path="data/gps.db",
                    highlight_path=self.last_best_result.path
                )
            else:
                # Visualizar solo el grafo sin ruta
                respuesta = messagebox.askyesno(
                    "Visualizar Grafo",
                    "No hay ruta calculada.\n\n"
                    "¿Deseas visualizar el grafo completo sin ruta?"
                )
                
                if respuesta:
                    visualizar_grafo(db_path="data/gps.db")
        
        except ImportError:
            messagebox.showerror(
                "Dependencias Faltantes",
                "Para usar la visualización, instala las dependencias:\n\n"
                "pip install matplotlib networkx\n\n"
                "O añádelas a requirements.txt y ejecuta:\n"
                "pip install -r requirements.txt"
            )
        except FileNotFoundError:
            messagebox.showerror(
                "Archivo No Encontrado",
                "No se encuentra el archivo 'visualizar_grafo.py'.\n\n"
                "Asegúrate de que esté en la raíz del proyecto."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al visualizar grafo:\n{e}")


def main():
    """Función principal de la aplicación"""
    root = tk.Tk()
    app = GPSSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()