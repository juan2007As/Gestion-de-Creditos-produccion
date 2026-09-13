# Conecta los fixtures de tests/conftest.py con mi_app/tests/, que pytest no
# resuelve solo (son directorios hermanos, no ancestro-descendiente).
pytest_plugins = ["tests.conftest"]
