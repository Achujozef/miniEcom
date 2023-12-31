# urls.py

from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),#Tested
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),#Tested
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),#Tested
    path('products/', ProductListView.as_view(), name='product-list'),#Tested
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),#Tested
    path('orders/', OrderView.as_view(), name='order-list'),#Tested
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),#Tested
    path('admin/orders/', AdminOrderView.as_view(), name='admin-order-list'),
    path('register/', RegisterView.as_view(), name='register'),#Tested
    path('orders/<int:order_id>/delete/', DeleteOrderView.as_view(), name='delete-order'),#Tested
    path('orders/<int:order_id>/change-status/', ChangeOrderStatusView.as_view(), name='change-order-status'),#Tested
    path('cart/checkout/', CartCheckoutView.as_view(), name='cart-checkout'),#Tested
    path('buy-now/<int:product_id>/', BuyNowView.as_view(), name='buy-now'),#Tested
    path('add-address/', AddAddressView.as_view(), name='add-address'),#Tested
    path('address/edit/<int:address_id>/', EditAddressView.as_view(), name='edit-address'),#Tested
    path('address/', GetAddressView.as_view(), name='latest-address'),#Tested
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add-to-cart'),#Tested
    path('cart/detail/', CartDetailView.as_view(), name='cart-detail'),#Tested
    path('cart/update/<int:product_id>/add/', UpdateCartItemView.as_view(), {'action': 'add'}, name='add-cart-item'),
    path('cart/update/<int:product_id>/minus/', UpdateCartItemView.as_view(), {'action': 'minus'}, name='minus-cart-item'),
    path('cart/remove/<int:product_id>/', RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('products/add/', AddProductView.as_view(), name='add-product'),
    path('products/edit/<int:product_id>/', EditProductView.as_view(), name='edit-product'),
    path('products/delete/<int:product_id>/', DeleteProductView.as_view(), name='delete-product'),
    path('products/toggle-listing/<int:product_id>/', ToggleProductListingView.as_view(), name='toggle-product-listing'),
    path('product/<int:product_id>/image/single/', ProductSingleImageView.as_view(), name='product-single-image'),
    path('product/<int:product_id>/image/all/', ProductAllImagesView.as_view(), name='product-all-images'),
]
