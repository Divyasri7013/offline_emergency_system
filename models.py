from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended User Profile with additional information"""
    
    THEME_CHOICES = [
        ('dark', 'Dark Mode'),
        ('light', 'Light Mode'),
        ('blue', 'Blue Theme'),
        ('red', 'Red Theme'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='Link to Django User'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Phone number'
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='User location'
    )
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='dark',
        help_text='UI theme preference'
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    is_first_login = models.BooleanField(
        default=True,
        help_text='First time login flag'
    )
    last_login_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last login timestamp'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Profile creation date'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last profile update'
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Profile"

    class Meta:
        db_table = 'alerts_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']


class EmergencyAlert(models.Model):
    """Emergency Alert Model with Enhanced Fields"""
    
    CATEGORY_CHOICES = [
        ('medical', '🏥 Medical Emergency'),
        ('earthquake', '🌍 Earthquake'),
        ('women_safety', '👩 Women Safety'),
        ('accident', '🚗 Accident'),
        ('fire', '🔥 Fire'),
        ('flood', '🌊 Flood'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '⏳ Pending'),
        ('in_progress', '🔄 In Progress'),
        ('resolved', '✅ Resolved'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', '🟢 Low - Minor incident'),
        ('medium', '🟡 Medium - Moderate incident'),
        ('high', '🔴 High - Serious incident'),
        ('critical', '🔥 Critical - Life-threatening'),
    ]
    
    # User Information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text='User who created alert'
    )
    
    # Required Fields
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text='Alert category'
    )
    message = models.TextField(
        help_text='Alert description and details'
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text='Alert severity level - REQUIRED'
    )
    contact_phone = models.CharField(
        max_length=15,
        help_text='Contact phone number - REQUIRED'
    )
    
    # Location Information
    latitude = models.FloatField(
        help_text='Alert latitude coordinate'
    )
    longitude = models.FloatField(
        help_text='Alert longitude coordinate'
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        help_text='Address or landmark - OPTIONAL'
    )
    
    # Additional Information
    people_affected = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        help_text='Number of people affected - OPTIONAL'
    )
    
    # Media
    image = models.ImageField(
        upload_to='alert_images/',
        blank=True,
        null=True,
        help_text='Alert evidence image'
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current alert status'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Alert creation time'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update time'
    )
    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Resolution time'
    )

    def __str__(self):
        return f"{self.get_category_display()} - {self.user.username} - {self.created_at.strftime('%d-%m-%Y')}"

    class Meta:
        db_table = 'alerts_emergencyalert'
        verbose_name = 'Emergency Alert'
        verbose_name_plural = 'Emergency Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['severity']),
        ]


class Notification(models.Model):
    """User Notification Model"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='Notification recipient'
    )
    alert = models.ForeignKey(
        EmergencyAlert,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        help_text='Related emergency alert (if any)'
    )
    title = models.CharField(
        max_length=255,
        help_text='Notification title'
    )
    message = models.TextField(
        help_text='Notification content'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Read status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Notification creation time'
    )

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        db_table = 'alerts_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        #location_name = models.CharField(max_length=255, blank=True, null=True)