from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import CustomLogoutView
from django.urls import path
from .views import video_feed, live_stream


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('charts/', views.charts, name='charts'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('register/', views.register, name='register'),  # URL for registration
    path('profile/', views.profile, name='profile'),    # URL for user profile
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    
    path('info/live_stream/', live_stream, name='live_stream'),
    path('info/video_feed/<str:stream_id>/', video_feed, name='video_feed'),

    path('api/device-info/', views.api_device_info, name='api_device_info'),

    
]
