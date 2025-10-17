from rest_framework import serializers
from .models import Node, Website

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['ip_address', 'status', 'api_key']
        read_only_fields = ['status', 'api_key']

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['domain', 'origin_server']