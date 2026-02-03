# validar_grafo.py
import csv
import tkinter as tk
from collections import defaultdict

def validar_grafo(csv_path):
    nodos = set()
    aristas = []
    
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = int(row["origin"])
            v = int(row["destination"])
            nodos.add(u)
            nodos.add(v)
            aristas.append((u, v))
    
    # Contar bidireccionales vs unidireccionales
    aristas_set = set(aristas)
    bidireccionales = 0
    unidireccionales = 0
    
    contadas = set()
    for (u, v) in aristas:
        if (u, v) in contadas or (v, u) in contadas:
            continue
        
        if (v, u) in aristas_set:
            bidireccionales += 2  # cuenta como 2 aristas
            contadas.add((u, v))
            contadas.add((v, u))
        else:
            unidireccionales += 1
            contadas.add((u, v))
    
    print(f"✅ Nodos: {len(nodos)} (mínimo 40)")
    print(f"✅ Aristas totales: {len(aristas)} (mínimo 80)")
    print(f"   - Unidireccionales: {unidireccionales} (mínimo 40)")
    print(f"   - Bidireccionales: {bidireccionales}")
    
    if len(nodos) >= 40 and len(aristas) >= 80 and unidireccionales >= 40:
        print("\n🎉 El grafo cumple TODOS los requisitos mínimos")
    else:
        print("\n⚠️ El grafo NO cumple los requisitos")

if __name__ == "__main__":
    validar_grafo("data/edges_laberinto.csv")
