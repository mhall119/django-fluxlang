from django.contrib import admin
from .models import HostInfo
# Register your models here.
class HostAdmin(admin.ModelAdmin):
    list_display = ("host", "ip_addr", "site")
admin.site.register(HostInfo, HostAdmin)
