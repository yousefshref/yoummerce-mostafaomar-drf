from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.google_login),

    path('users/', views.users),

    path('categories/', views.categories),

    path('custom_home/', views.custom_home),

    path('header/', views.header),
    
    path('states/', views.get_state),

    path('status/', views.get_status),

    path('products/', views.product),
    path('products/<int:pk>', views.one_product),

    path('cart/', views.create_update_cart),
    path('cart/<int:pk>/', views.get_cart),
    path('cart/<int:pk>/delete_user_carts/', views.delete_user_carts),
    path('cart/<int:pk>/delete/', views.delete_cart),


    path('orders/<int:userpk>', views.get_user_orders),


    path('create_order/', views.create_order),
    path('create_order_item/', views.create_order_item),
]
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)