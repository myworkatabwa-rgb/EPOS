from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from ZH_pos.woocommerce_webhook import woocommerce_webhook
from ZH_pos.views import pos_view
from .views.financial_dashboard import financial_dashboard

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("finance/", financial_dashboard, name="financial_dashboard"),

    # POS
    path("pos/", pos_view, name="pos"),

    # WooCommerce webhook
    path("webhook/woocommerce/", woocommerce_webhook),

    # App URLs (dashboard, etc.)
    path("", include("ZH_pos.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
