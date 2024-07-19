from django.urls import path
from . import views
from .views import video_feed


urlpatterns = [

    path('live_stream1/', views.live_stream1, name='live_stream'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('video_feed/<int:stream_id>/', video_feed, name='video_feed'),
    path('control_stream/<str:stream_id>/<str:action>/', views.control_stream, name='control_stream'),
    

]