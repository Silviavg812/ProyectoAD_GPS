# GPS Laberinto (simple) - FIX Windows imports

## Ejecutar
En PowerShell / terminal, dentro de la carpeta del proyecto:

```powershell
python -m src.cli
```

## Probar rápido
- Origen: 0
- Destino: 4
- Intermedios: (ENTER)

Debe salir una ruta y un coste.

## Integración con SQLite
Tu compañero crea un DAO con:
`get_neighbors(node) -> Iterable[Edge]`
y lo pasáis al `DAOGraphAdapter`.
