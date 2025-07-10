from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *


class BooksPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 1000


class RegisterAPIView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save()
        Wishlist.objects.create(account=serializer.instance)


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


class BookRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return BookSerializer
        return BookPostSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        if serializer.instance.acoount != self.request.user:
            raise PermissionDenied(detail='You are not the owner of this book')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.account != self.request.user:
            raise PermissionDenied(detail='You are not the owner of this book')
        instance.delete()


class MyBooksList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sold', 'cover']
    search_fields = ['title']
    ordering_fields = ['title', 'price', 'created']
    pagination_class = BooksPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='cover',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Filter books by cover status',
            ),
            openapi.Parameter(
                name='sold',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description='Filter books by sold status',
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return Book.objects.filter(account=self.request.user)


class BookMarkSoldAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        book = get_object_or_404(Book, pk=pk, account=request.user)
        serializer = BookMarkSoldSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save(sold=True)
            response = {
                "success": True,
                "message": "Book marked sold.",
                "data": BookSerializer(book).data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyWishListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    pagination_class = BooksPagination

    def get_queryset(self):
        wishlist = Wishlist.objects.get(account=self.request.user)
        return wishlist.books.order_by('-created')


class MyWishListAddBookAPIView(APIView):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        wishlist = Wishlist.objects.get(account=request.user)
        wishlist.books.add(book)
        wishlist.save()
        response = {
            "success": True,
            "message": "Book marked added.",
        }
        return Response(response, status=status.HTTP_201_CREATED)

class MyWishListRemoveBookAPIView(APIView):
    def delete(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        wishlist = Wishlist.objects.get(account=request.user)
        wishlist.books.remove(book)
        wishlist.save()
        response = {
            "success": True,
            "message": "Book marked removed.",
        }
        return Response(response, status=status.HTTP_204_NO_CONTENT)
