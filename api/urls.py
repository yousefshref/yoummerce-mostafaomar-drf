from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.google_login),

    path('logincredentials/', views.login_credentials),

    path('register_credentials/', views.register_credentials),

    path('users/', views.users),

    path('categories/', views.categories),
 
    path('states/', views.get_state),

    path('status/', views.get_status),

    path('products/', views.product),
    path('products/<int:pk>', views.one_product),

    path('cart/', views.create_update_cart),
    path('carts/', views.get_carts),
    path('cart/<int:pk>/', views.get_cart),
    path('cart/<int:pk>/delete_user_carts/', views.delete_user_carts),
    path('cart/<int:pk>/delete/', views.delete_cart),


    path('orders/<int:userpk>', views.get_user_orders),
    path('all_orders/', views.get_orders),


    path('create_order/', views.create_order),
    path('create_order_item/', views.create_order_item),


    # cancel order
    path('cancel_order/', views.cancel_order), # order_id in params and add in json { "is_arrived" : 4 }
    # cancel order
]
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)