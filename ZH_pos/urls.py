from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),
    path("pos/checkout/", pos_checkout, name="pos_checkout"),
]
