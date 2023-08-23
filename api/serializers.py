from rest_framework import serializers
from django.contrib.auth.models import User
from . import models



class UserSignupWithCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserLoginWithCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductImage
        fields = '__all__'



class RelatedProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    category = serializers.CharField()

    class Meta:
        model = models.Product
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)
    category = serializers.CharField()
    
    related_products = RelatedProductSerializer(many=True)

    class Meta:
        model = models.Product
        fields = '__all__'



class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    product_info = ProductSerializer(source='product', read_only=True)
    user_info = UserSerializer(source='user', read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    total_commission = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = models.Cart
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductSerializer(read_only=True, source='product')
    class Meta:
        model = models.OrderItems
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_item_info = OrderItemSerializer(read_only=True, many=True, source='order_item')
    state_name = StateSerializer(read_only=True, source='state')
    is_arrived_name = serializers.CharField(read_only=True, source='is_arrived')
    
    class Meta:
        model = models.Order
        fields = '__all__'

class CategorySerizlizer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


class ShippedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Shipped
        fields = '__all__'






