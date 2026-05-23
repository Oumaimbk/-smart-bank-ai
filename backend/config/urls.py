from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/anomalies/', include('apps.anomalies.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
]
