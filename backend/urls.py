from django.urls import path

from .views import RegisterUserView, LoginView, ImportProductsView, ProductListView, CartView, ContactListView, \
    ContactDetailView, OrderConfirmationView, OrderListView, OrderDetailView, OrderStatusUpdateView, ProductDetailView, \
    ConfirmEmailView, UserDetailView, UserUpdateView, PasswordResetView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('confirm-email/<uuid:token>/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('import_products/', ImportProductsView.as_view(), name='import_products'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('contacts/', ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:contact_id>/', ContactDetailView.as_view(), name='contact_detail'),
    path('orders/<int:order_id>/confirm/', OrderConfirmationView.as_view(), name='order_confirm'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
]

