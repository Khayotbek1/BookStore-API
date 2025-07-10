from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from main.views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Book Store API",
        default_version='v1',
        description="",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('accounts/register/', RegisterAPIView.as_view()),
    path('accounts/me/', AccountRetrieveUpdateDestroyAPIView.as_view()),
    path('accounts/wishlist/', MyWishListAPIView.as_view()),
    path('accounts/wishlist/add-book/<int:pk>/', MyWishListAddBookAPIView.as_view()),
    path('accounts/wishlist/remove-book/<int:pk>/', MyWishListRemoveBookAPIView.as_view()),
]

urlpatterns += [
    path('books/', BookListCreateAPIView.as_view()),
    path('books/<int:pk>/', BookRetrieveUpdateDestroyAPIView.as_view()),
    path('books/<int:pk>/mark-sold/', BookMarkSoldAPIView.as_view()),
    path('books/mine/', MyBooksList.as_view()),
]


urlpatterns += [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += [
    path('token/', token_obtain_pair, name='token'),
    path('token/refresh/', token_refresh, name='token-refresh'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

