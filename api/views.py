
from . import models
from .serializers import UserSerializer
from . import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def users(request):

    if request.GET.get('email'):
        user = models.User.objects.all()
        email = request.GET.get('email')
        user = user.get(email=email)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    user = models.User.objects.all()
    serializer = serializers.UserSerializer(user, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def categories(request):
    categories = models.Category.objects.all()
    serializer = serializers.CategorySerizlizer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def custom_home(request):
    if request.method == 'GET':
        carts = models.CustomHome.objects.all()
        serializer = serializers.CustomHomeSerializer(carts, many=True)
        return Response(serializer.data)

        
@api_view(['GET'])
def header(request):
    if request.method == 'GET':
        carts = models.Header.objects.all()
        serializer = serializers.HeaderSerializer(carts, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def google_login(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['GET'])
def product(request):
    # GET PRODUCT WITH CATEGORIES AND SEARCH PARAMETERS
    category_param = request.GET.get('category', '')
    search_param = request.GET.get('search', '')

    from_price_param = request.GET.get('from', '')
    to_price_param = request.GET.get('to', '')

    products = models.Product.objects.all()

    # Filter by category
    if category_param:
        products = products.filter(category__name=category_param)

    # Filter by search
    if search_param:
        products = products.filter(title__icontains=search_param)

    
    # Filter with price range
    if from_price_param and to_price_param:
        products = products.filter(sell_price__gte=from_price_param, sell_price__lte=to_price_param)

    # get all
    if not search_param and not category_param and not from_price_param and not to_price_param:
        products = models.Product.objects.all()



    serializer = serializers.ProductSerializer(products, many=True)
    return Response(serializer.data)
# http://127.0.0.1:8000/products/?search=&category=&from=&to=  


@api_view(['GET'])
def one_product(request, pk):
    product = models.Product.objects.get(id=pk)
    serializer = serializers.ProductSerializer(product)
    return Response(serializer.data)

@api_view(['POST'])
def create_update_cart(request):
    # get the user and product
    user = request.data['user']
    product = request.data['product']

    # get the cart tat have the same product and user (UPDATE QUANTITY)
    try:
        cart = models.Cart.objects.get(user=user, product=product)
        serializer = serializers.CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    # if there is no cart with this user and product (CREATE CART)
    except models.Cart.DoesNotExist:
        serializer = serializers.CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


@api_view(['GET'])
def get_state(request):
    states = models.State.objects.all()
    serializer = serializers.StateSerializer(states, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_status(request):
    status = models.Shipped.objects.all()
    serializer = serializers.ShippedSerializer(status, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_cart(request, pk):
    if request.method == 'GET':
        carts = models.Cart.objects.filter(user=pk)
        serializer = serializers.CartSerializer(carts, many=True)
        return Response(serializer.data)

@api_view(['DELETE'])
def delete_user_carts(request, pk):
    carts = models.Cart.objects.filter(user=pk)
    carts.delete()
    return Response({"DELETED":"You deleted them"})

@api_view(['DELETE'])
def delete_cart(request, pk):
    cart = models.Cart.objects.get(id=pk)
    cart.delete()
    return Response({"Success":"The Cart has been deleted"})


@api_view(['GET'])
def get_user_orders(request, userpk):

    orders = models.Order.objects.all()

    name_param = request.GET.get('name')

    status_param = request.GET.get('status')

    _from = request.GET.get('from')
    _to = request.GET.get('to')

    if name_param:
        orders = orders.filter(user=userpk, name__icontains=name_param)

    if status_param:
        orders = orders.filter(user=userpk, is_arrived__name=status_param)

    if _from and _to:
        orders = orders.filter(user=userpk, date__range=[_from, _to])

    else:
        orders = orders.filter(user=userpk)

    serializer = serializers.OrderSerializer(orders, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def create_order(request):
    serializer = serializers.OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({"Error":"Order Create Views"})


@api_view(['POST'])
def create_order_item(request):
    serializer = serializers.OrderItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({"Error":"Order Item Create Views"})

