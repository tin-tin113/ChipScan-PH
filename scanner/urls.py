from django.urls import path
from scanner import views

urlpatterns = [
    # SPA Shell
    path('', views.spa_shell, name='spa_shell'),
    
    # API endpoints
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    
    path('api/chips/', views.api_chips, name='api_chips'),
    path('api/chips/<str:code>/delete/', views.api_delete_chip, name='api_delete_chip'),
    path('api/chips/<str:code>/check/', views.api_check_chip, name='api_check_chip'),
    
    path('api/prices/', views.api_prices, name='api_prices'),
    
    path('api/scan/history/', views.api_scan_history, name='api_scan_history'),
    path('api/scan/image/', views.api_scan_image, name='api_scan_image'),
    path('api/scan/manual/', views.api_scan_manual, name='api_scan_manual'),
    
    path('api/approvals/submit/', views.api_submit_approval, name='api_submit_approval'),
    path('api/approvals/', views.api_approvals, name='api_approvals'),
    
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/stats/', views.api_stats, name='api_stats'),
    
    path('camera/stream/', views.camera_stream, name='camera_stream'),
]
