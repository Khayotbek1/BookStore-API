from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny

from .serializers import *

class BooksPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000

class RegisterAPIView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['cover', 'account', 'sold']
    search_fields = ['title']
    ordering_fields = ['title', 'price', 'created']
    pagination_class = BooksPagination


    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name='sold',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description='Filter books by sold status',
        ),
        openapi.Parameter(
            name='cover',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Filter books by cover status',
        ),
        openapi.Parameter(
            name='account',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Filter books by account status',
        ),
    ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BookSerializer
        return BookPostSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)