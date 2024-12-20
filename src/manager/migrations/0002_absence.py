# Generated by Django 4.2 on 2023-05-31 08:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Absence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], default='pending', max_length=10)),
                ('absence_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absences', to='manager.remoteday')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
