from django.contrib import admin
from .models import UserProfile, EmergencyAlert, Notification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'theme', 'is_first_login', 'created_at')
    list_filter = ('theme', 'is_first_login')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'severity', 'status', 'created_at')
    list_filter = ('status', 'severity', 'category', 'created_at')
    search_fields = ('user__username', 'message', 'location_name')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Alert Details', {
            'fields': ('category', 'message', 'severity')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at', 'resolved_at')
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

    from django.contrib import admin
from .models import EmergencyAlert

