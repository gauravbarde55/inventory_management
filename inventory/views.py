import logging
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache

from .models import Item
from .serializers import ItemSerializer, UserSerializer

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    # You can customize token response here if needed.
    pass

class ItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Item created: {serializer.data}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'Item creation failed: {serializer.errors}')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        item = cache.get(f'item_{pk}')
        if not item:
            try:
                item = Item.objects.get(pk=pk)
                cache.set(f'item_{pk}', item)
            except Item.DoesNotExist:
                logger.error(f'Item not found: {pk}')
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            serializer = ItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Item updated: {serializer.data}')
                return Response(serializer.data)
            logger.error(f'Item update failed: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Item.DoesNotExist:
            logger.error(f'Item not found for update: {pk}')
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            item.delete()
            logger.info(f'Item deleted: {pk}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Item.DoesNotExist:
            logger.error(f'Item not found for deletion: {pk}')
            return Response(status=status.HTTP_404_NOT_FOUND)