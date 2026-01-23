import pytest
import os

@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Cleanup automático de bases de datos de test"""
    yield
    # Eliminar archivos DB de test al final
    for db_file in ['tests/test_gps.db', 'tests/test_dijkstra.db', 'tests/reqs.db', 'tests/integracion.db']:
        if os.path.exists(db_file):
            os.remove(db_file)
