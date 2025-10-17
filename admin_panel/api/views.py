from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Node, Website
from .serializers import NodeSerializer, WebsiteSerializer
from .authentication import ApiKeyAuthentication

class RegisterNodeView(APIView):
    def post(self, request):
        """
        Register a new node. The IP address is taken from the request.
        A new node is created with an 'offline' status and a unique API key.
        """
        ip_address = request.META.get('REMOTE_ADDR')
        if not ip_address:
            return Response({"error": "Could not determine IP address."}, status=status.HTTP_400_BAD_REQUEST)

        node, created = Node.objects.get_or_create(ip_address=ip_address)

        if created:
            serializer = NodeSerializer(node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # If node already exists, just return its data without creating a new one.
            serializer = NodeSerializer(node)
            return Response(serializer.data, status=status.HTTP_200_OK)

class ConfigView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def get(self, request):
        """
        Provides the configuration for a node.
        This includes the list of all websites to be served.
        The node is identified by its API key.
        """
        # The authenticated node is available via request.user
        node = request.user
        node.status = 'online'
        node.save()

        websites = Website.objects.all()
        websites_serializer = WebsiteSerializer(websites, many=True)

        config_data = {
            "websites": websites_serializer.data
        }
        return Response(config_data)

    def post(self, request):
        """
        Allows a node to update its status.
        For example, sending a heartbeat.
        """
        node = request.user
        new_status = request.data.get('status')
        if new_status:
            node.status = new_status
            node.save()
            return Response({"status": f"Status updated to {new_status}"}, status=status.HTTP_200_OK)
        return Response({"error": "Status not provided"}, status=status.HTTP_400_BAD_REQUEST)