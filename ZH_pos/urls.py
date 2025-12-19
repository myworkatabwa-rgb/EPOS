from django.urls import path
from ZH_pos import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pos/", views.pos_view, name="pos"),
    path("pos/checkout/", views.pos_checkout, name="pos_checkout"),
    path("returns/<str:order_id>/", views.process_return, name="process_return"),
]
