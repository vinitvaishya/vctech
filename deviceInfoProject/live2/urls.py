from django.urls import path
from . import views



urlpatterns = [
    path('video_feed1/<int:stream_id>/', views.video_feed1, name='video_feed1'),
    path('control_stream/<int:stream_id>/<str:action>/', views.control_stream, name='control_stream'),
    path('live_stream_page/<int:page_num>/', views.live_stream_page, name='live_stream_page'),
]
