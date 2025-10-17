from django.contrib import admin
from .models import Node, Website

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("ip_address",)
    readonly_fields = ("api_key", "created_at", "updated_at")

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("domain", "origin_server", "created_at")
    search_fields = ("domain",)
    readonly_fields = ("created_at", "updated_at")