"""
Visualizador del Grafo GPS
Genera una visualización gráfica del laberinto/grafo
COLUMNA CORRECTA: cost
"""

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import networkx as nx
import sqlite3


def visualizar_grafo(db_path="data/gps.db", highlight_path=None):
    """
    Visualiza el grafo completo del GPS
    
    Args:
        db_path: Ruta a la base de datos
        highlight_path: Lista de nodos para resaltar (opcional)
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ✅ CORREGIDO: Usar 'cost' en lugar de 'coste'
        cursor.execute("SELECT origin, destination, cost FROM aristas")
        edges = cursor.fetchall()
        conn.close()
        
        G = nx.DiGraph()
        
        for origin, dest, cost in edges:
            G.add_edge(origin, dest, weight=cost)
        
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        plt.figure(figsize=(16, 12))
        plt.title("Visualizacion del Grafo GPS", fontsize=20, fontweight='bold')
        
        if highlight_path:
            path_nodes = set(highlight_path)
            other_nodes = [n for n in G.nodes() if n not in path_nodes]
            
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=other_nodes,
                node_color='lightgray',
                node_size=500,
                alpha=0.6
            )
            
            colors = plt.cm.RdYlGn_r(range(len(highlight_path)))
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=highlight_path,
                node_color=colors,
                node_size=800,
                alpha=1.0
            )
            
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=[highlight_path[0]],
                node_color='green',
                node_size=1000,
                node_shape='s'
            )
            
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=[highlight_path[-1]],
                node_color='red',
                node_size=1000,
                node_shape='*'
            )
            
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                          for i in range(len(highlight_path)-1)]
            
            other_edges = [e for e in G.edges() if e not in path_edges]
            nx.draw_networkx_edges(
                G, pos,
                edgelist=other_edges,
                edge_color='gray',
                arrows=True,
                arrowsize=10,
                width=1,
                alpha=0.3
            )
            
            nx.draw_networkx_edges(
                G, pos,
                edgelist=path_edges,
                edge_color='blue',
                arrows=True,
                arrowsize=20,
                width=4,
                alpha=0.8
            )
        else:
            nx.draw_networkx_nodes(
                G, pos,
                node_color='lightblue',
                node_size=500,
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                G, pos,
                edge_color='gray',
                arrows=True,
                arrowsize=10,
                width=1,
                alpha=0.5
            )
        
        nx.draw_networkx_labels(
            G, pos,
            font_size=8,
            font_weight='bold',
            font_color='black'
        )
        
        if highlight_path:
            legend_text = f"Origen: {highlight_path[0]}\n"
            legend_text += f"Destino: {highlight_path[-1]}\n"
            legend_text += f"Longitud: {len(highlight_path)} nodos"
            plt.text(
                0.02, 0.98, legend_text,
                transform=plt.gca().transAxes,
                fontsize=12,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            )
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error al visualizar grafo: {e}")
        raise


def visualizar_con_costes(db_path="data/gps.db", highlight_path=None):
    """
    Visualiza el grafo mostrando los pesos/costes de las aristas
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin, destination, cost FROM aristas")
        edges = cursor.fetchall()
        conn.close()
        
        G = nx.DiGraph()
        for origin, dest, cost in edges:
            G.add_edge(origin, dest, weight=cost)
        
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        plt.figure(figsize=(18, 14))
        plt.title("Grafo GPS con Costes", fontsize=20, fontweight='bold')
        
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=600)
        
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                               arrowsize=10, width=1.5, alpha=0.6)
        
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels,
            font_size=7,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.6)
        )
        
        if highlight_path:
            path_edges = [(highlight_path[i], highlight_path[i+1]) 
                          for i in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(
                G, pos,
                edgelist=path_edges,
                edge_color='red',
                arrows=True,
                arrowsize=20,
                width=4
            )
            
            total_cost = sum(G[u][v]['weight'] for u, v in path_edges)
            
            legend_text = f"Origen: {highlight_path[0]}\n"
            legend_text += f"Destino: {highlight_path[-1]}\n"
            legend_text += f"Coste total: {total_cost:.2f}\n"
            legend_text += f"Nodos: {len(highlight_path)}"
            
            plt.text(
                0.02, 0.98, legend_text,
                transform=plt.gca().transAxes,
                fontsize=12,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9)
            )
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error al visualizar grafo con costes: {e}")
        raise


if __name__ == "__main__":
    print("Visualizador de Grafos GPS\n")
    print("Opciones:")
    print("1. Ver grafo completo")
    print("2. Ver grafo con costes")
    print("3. Ver con ruta de ejemplo")
    
    opcion = input("\nElige una opcion (1-3): ")
    
    try:
        if opcion == "1":
            visualizar_grafo()
        elif opcion == "2":
            visualizar_con_costes()
        elif opcion == "3":
            camino_ejemplo = [0, 8, 16, 24, 32, 39]
            visualizar_grafo(highlight_path=camino_ejemplo)
        else:
            print("Opcion no valida")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nVerifica que:")
        print("- matplotlib y networkx esten instalados")
        print("- La base de datos exista en data/gps.db")