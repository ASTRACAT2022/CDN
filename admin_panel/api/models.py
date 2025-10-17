import uuid
from django.db import models

class Node(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    status = models.CharField(max_length=20, default="offline")
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ip_address} ({self.status})"

class Website(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    origin_server = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain