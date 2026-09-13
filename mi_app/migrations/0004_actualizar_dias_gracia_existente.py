from django.db import migrations


def actualizar_dias_gracia(apps, schema_editor):
    Configuracion = apps.get_model('mi_app', 'Configuracion')
    # Solo actualiza si sigue en el valor viejo (5) — si alguien ya lo
    # cambió a mano a otra cosa, no lo pisamos.
    Configuracion.objects.filter(dias_gracia_mora=5).update(dias_gracia_mora=2)


def revertir(apps, schema_editor):
    Configuracion = apps.get_model('mi_app', 'Configuracion')
    Configuracion.objects.filter(dias_gracia_mora=2).update(dias_gracia_mora=5)


class Migration(migrations.Migration):

    dependencies = [
        ('mi_app', '0003_pago_capital_antes_pago_capital_despues_and_more'),
    ]

    operations = [
        migrations.RunPython(actualizar_dias_gracia, revertir),
    ]
