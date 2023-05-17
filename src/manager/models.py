from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class RemoteDay(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return self.date.strftime('%Y-%m-%d')


class Employee(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_manager = models.BooleanField(default=False)
    remote_days = models.ManyToManyField(RemoteDay, blank=True)

    def __str__(self):
        return self.username


class RemoteRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    comment = models.TextField(blank=True, null=True)

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='remote_requests')
    remote_day = models.ForeignKey(RemoteDay, on_delete=models.CASCADE, related_name='remote_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
