from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.view_login, name='login'),
    path('do_logout', views.do_logout, name='do_logout'),
    path('list', views.list, name='list'),
    # path('add', views.add, name='add'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('delete_sale_item/<int:id>', views.delete_sale_item, name='delete_sale_item'),
    path('delete_return_item/<int:id>/<str:sale_id>', views.delete_return_item, name='delete_return_item'),
    path('edit/<int:id>', views.edit, name='edit'),
    path('sale', views.sale, name='sale'),
    path('checkout', views.checkout, name='checkout'),
    path('checkout_return/<str:sale_id>/', views.checkout_return, name='checkout_return'),
    path('clear_sale', views.clear_sale, name='clear_sale'),
    path('clear_return/<str:sale_id>/', views.clear_return, name='clear_return'),
    path('sale_list', views.sale_list, name='sale_list'),
    path('reorder', views.reorder, name='reorder'),
    path('toggle_payment_status/<str:sale_id>/', views.toggle_payment_status, name='toggle_payment_status'),
    path('generate_bill/<str:sale_id>/', views.generate_bill, name='generate_bill'),
    path('generate_return_bill/<str:sale_id>/', views.generate_return_bill, name='generate_return_bill'),
    path('bill/<str:sale_id>.pdf', views.serve_pdf, name='serve_pdf'),
    path('add_customer_info', views.add_customer_info, name='add_customer_info'),
    path('view-charts/', views.view_charts, name='view_charts'),
    path('return_items/<str:sale_id>/', views.return_items, name='return_items'),
]
