from pathlib import Path
import re

urls = Path('mi_app/urls.py').read_text(encoding='utf-8')
route_names = re.findall(r"name='([^']+)'", urls)

base = Path('mi_app/templates/mi_app/base.html').read_text(encoding='utf-8')
base_links = set(re.findall(r"\{\% url '([^']+)'", base))

inicio_path = Path('mi_app/templates/mi_app/inicio.html')
inicio = inicio_path.read_text(encoding='utf-8') if inicio_path.exists() else ''
inicio_links = set(re.findall(r"\{\% url '([^']+)'", inicio))

linked = base_links | inicio_links
missing = [n for n in route_names if n not in linked and not n.startswith('api_')]

print('TOTAL_ROUTES', len(route_names))
print('LINKED_NAV_OR_HOME', len(linked))
print('MISSING')
for n in missing:
    print('-', n)
