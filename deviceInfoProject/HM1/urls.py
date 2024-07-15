from django.urls import path
from . import views
from .views import display_alerts, resolve_alert






urlpatterns = [

    path('alert-dashboard/', views.alert_dashboard, name='alert_dashboard'),
    path('alerts/', views.display_alerts, name='display_alerts'),
    path('alerts/resolve/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    path('alerts/dismiss/<int:alert_id>/', views.dismiss_alert, name='dismiss_alert'),
    path('resolved_alerts/', views.resolved_alerts, name='resolved_alerts'),  # For viewing resolved alerts




    

    
]






