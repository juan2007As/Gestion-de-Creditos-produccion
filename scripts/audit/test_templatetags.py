#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto_john.settings")
django.setup()

from django.template import Template, Context

# Test si el templatetag se carga correctamente
try:
    template_string = "{% load numeros_colombianos %}{{ 1234567.89|formato_colombiano }}"
    template = Template(template_string)
    result = template.render(Context({}))
    print(f"✅ TemplateTag cargado correctamente")
    print(f"   Resultado: {result}")
    print()
    
    # Test dinero colombiano
    template_string2 = "{% load numeros_colombianos %}{{ 1234567|formato_dinero_colombiano }}"
    template2 = Template(template_string2)
    result2 = template2.render(Context({}))
    print(f"✅ Formato dinero funcionando")
    print(f"   Resultado: {result2}")
    print()
    
    # Test porcentaje
    template_string3 = "{% load numeros_colombianos %}{{ 15.5|formato_porcentaje_colombiano }}"
    template3 = Template(template_string3)
    result3 = template3.render(Context({}))
    print(f"✅ Formato porcentaje funcionando")
    print(f"   Resultado: {result3}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
