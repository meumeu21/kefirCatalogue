from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.kefir_list, name='home'),
    path('about/', views.about, name='about'),
    path('kefir/<int:pk>/', views.kefir_detail, name='kefir_detail'),

    path('kefir/add/', views.add_kefir, name='add_kefir'),
    path('kefir/edit/<int:pk>/', views.edit_kefir, name='edit_kefir'),
    path('kefir/delete-selected/', views.delete_selected_kefirs, name='delete_selected_kefirs'),
    path('kefir/delete/<int:pk>/', views.delete_kefir, name='delete_kefir'),

    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('accounts/signup/', views.signup, name='signup'),

    path('checkout/', views.checkout, name='checkout'),

    path('search/', views.search_kefir, name='search_kefir'),
]
