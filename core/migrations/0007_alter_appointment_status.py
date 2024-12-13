# Generated by Django 5.0 on 2024-11-12 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_delete_patienthistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('scheduled', 'Scheduled'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20),
        ),
    ]
