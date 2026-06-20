from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Auth
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Alerts
    path('save-alert/', views.save_alert, name='save_alert'),
    path('get-user-alerts/', views.get_user_alerts, name='get_user_alerts'),
    path('get-all-alerts/', views.get_all_alerts, name='get_all_alerts'),
    path('alert/<int:alert_id>/update-status/', views.update_alert_status, name='update_alert_status'),
    path('alert/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),
    
    # Profile
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/update-theme/', views.update_theme, name='update_theme'),
    
    # Notifications
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Stats
    path('stats/dashboard/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('stats/admin/', views.get_admin_stats, name='get_admin_stats'),
]