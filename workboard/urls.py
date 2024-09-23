from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from boards.views import CustomTokenObtainPairView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('boards.urls')),  # All board-related endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
