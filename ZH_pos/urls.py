from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),  # use views.pos_checkout
    path("pos/", views.pos_view, name="pos_view"),  # optional, for POS page
]
