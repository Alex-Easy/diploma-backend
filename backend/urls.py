from django.urls import path

from .import_products import ProductImportAPIView
from .views import RegisterUserView, LoginView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('import_products/', ProductImportAPIView.as_view(), name='import_products'),
]
