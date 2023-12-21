# views.py

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password or len(password) < 6:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        user_profile = UserProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        data = {
            'user': UserProfileSerializer(user_profile).data,
            'access_token': str(access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)

class ProductListView(ListAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    page_size = 10

class ProductDetailView(APIView):
    def get(self, request, pk):   
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        return super().handle_exception(exc)

class AddProductView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EditProductView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProductView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class ToggleProductListingView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        product.is_listed = not product.is_listed 
        product.save()
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
class ProductSingleImageView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            product_image = ProductImage.objects.filter(product=product).first()
        except ProductImage.DoesNotExist:
            return Response({"detail": "No image found for the product."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data)

class ProductAllImagesView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        product_images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(product_images, many=True)
        return Response(serializer.data)

class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id):
        user = request.user
        product = Product.objects.get(pk=product_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id, action):
        cart = Cart.objects.get(user=request.user)
        product = Product.objects.get(pk=product_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if action == 'add':
            cart_item.quantity += 1
        elif action == 'minus':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
        else:
            return Response({"detail": "Invalid action. Use 'add' or 'minus'."}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, product_id):
        cart = Cart.objects.get(user=request.user)
        product = Product.objects.get(pk=product_id)
        if product in cart.products.all():
            cart.products.remove(product)
            cart.save()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        return Response({"detail": "Product not found in the cart."}, status=status.HTTP_400_BAD_REQUEST)

class GetAddressView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        latest_address = Address.objects.filter(user_profile=user_profile).order_by('-id').first()
        if latest_address:
            serializer = AddressSerializer(latest_address)
            return Response(serializer.data)
        else:
            return Response({"detail": "No address found for the user."}, status=status.HTTP_404_NOT_FOUND)

class EditAddressView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return Response({"detail": "Address not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user != address.user_profile.user:
            return Response({"detail": "You do not have permission to edit this address."}, status=status.HTTP_403_FORBIDDEN)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id):
        user = request.user
        product = Product.objects.get(pk=product_id)
        order = Order.objects.create(
            user=user,
            total_price=product.price,
        )
        order.products.add(product)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        order = Order.objects.create(
            user=user,
            total_price=cart.total_price,
        )
        for cart_item in cart_items:
            order.products.add(cart_item.product)
        cart_items.delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
class AdminOrderView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 10  
    def get(self, request):
        if request.user.userprofile.is_super_user:
            admin_orders = AdminOrder.objects.all().order_by('-id')  
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(admin_orders, request)
            serializer = AdminOrderSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response({"detail": "You do not have permission to access this resource."}, status=status.HTTP_403_FORBIDDEN)
    
class ChangeOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user != order.user:
            return Response({"detail": "You do not have permission to change the status of this order."}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status', None)
        if new_status is None:
            return Response({"detail": "Status must be provided in the request data."}, status=status.HTTP_400_BAD_REQUEST)
        if new_status not in dict(Order.STATUS_CHOICES).keys():
            return Response({"detail": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
class DeleteOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user != order.user:
            return Response({"detail": "You do not have permission to delete this order."}, status=status.HTTP_403_FORBIDDEN)
        order.delete()
        return Response({"detail": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)