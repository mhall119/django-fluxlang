from django.db import models

# Create your models here.

class HostInfo(models.Model):
    host = models.CharField(max_length=256)
    ip_addr = models.CharField(max_length=16)
    site = models.CharField(max_length=512)