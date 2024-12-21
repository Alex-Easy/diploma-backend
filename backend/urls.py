from django.urls import path

from .views import RegisterUserView, LoginView, ImportProductsView, ProductListView, CartView, ContactListView, \
    ContactDetailView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('import_products/', ImportProductsView.as_view(), name='import_products'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('contacts/', ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:contact_id>/', ContactDetailView.as_view(), name='contact_detail'),
]

