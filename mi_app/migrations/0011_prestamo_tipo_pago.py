# Generated migration for new tipo_pago field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mi_app', '0010_fix_interes_calculation'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestamo',
            name='tipo_pago',
            field=models.CharField(
                choices=[('QUINCENAL', 'Quincenal'), ('MENSUAL', 'Mensual')],
                default='QUINCENAL',
                max_length=20
            ),
        ),
    ]
