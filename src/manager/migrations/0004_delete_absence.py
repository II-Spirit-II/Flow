# Generated by Django 4.2 on 2023-05-31 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_remove_absence_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Absence',
        ),
    ]
