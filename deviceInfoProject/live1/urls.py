from django.urls import path
from . import views

app_name = 'live1'

urlpatterns = [
    path('video_feed/<int:stream_id>/', views.video_feed, name='video_feed'),
    path('control_stream/<int:stream_id>/<str:action>/', views.control_stream, name='control_stream'),
    path('live_stream_page/<int:page_num>/', views.live_stream_page, name='live_stream_page'),
    
]
