# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import csrf_exempt
# from django.utils import timezone
# import json

# from .models import UserProfile, EmergencyAlert, Notification


# # ============================================================
# # AUTH VIEWS
# # ============================================================

# def landing(request):
#     """Landing page - accessible to everyone"""
#     # if request.user.is_authenticated:
#     #     return redirect('alerts:dashboard')
#     return render(request, 'safenet/index.html')


# @require_http_methods(["POST"])
# def register(request):
#     """User Registration"""
#     try:
#         data = json.loads(request.body)
#         name = data.get('name', '').strip()
#         email = data.get('email', '').strip()
#         password = data.get('password', '')
        
#         if not name or not email or not password:
#             return JsonResponse({'success': False, 'error': 'All fields required'}, status=400)
        
#         if User.objects.filter(email=email).exists():
#             return JsonResponse({'success': False, 'error': 'Email already registered'}, status=400)
        
#         if len(password) < 6:
#             return JsonResponse({'success': False, 'error': 'Password must be 6+ characters'}, status=400)
        
#         username = email.split('@')[0]
#         if User.objects.filter(username=username).exists():
#             username = f"{username}_{User.objects.count()}"
        
#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             first_name=name.split()[0],
#             last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
#         )
        
#         UserProfile.objects.get_or_create(user=user, defaults={'is_first_login': True})
#         login(request, user)
        
#         return JsonResponse({
#             'success': True,
#             'message': 'Account created!',
#             'redirect': '/dashboard/'
#         })
#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @require_http_methods(["POST"])
# def user_login(request):
#     """User Login"""
#     try:
#         data = json.loads(request.body)
#         email = data.get('email', '').strip()
#         password = data.get('password', '')
        
#         if not email or not password:
#             return JsonResponse({'success': False, 'error': 'Email and password required'}, status=400)
        
#         user = User.objects.get(email=email)
#         user = authenticate(request, username=user.username, password=password)
        
#         if user is not None:
#             profile = user.profile
#             is_first_login = profile.is_first_login
#             profile.is_first_login = False
#             profile.last_login_date = timezone.now()
#             profile.save()
            
#             login(request, user)
            
#             message = "Welcome to SafeNet" if is_first_login else "Welcome Back"
#             return JsonResponse({
#                 'success': True,
#                 'message': message,
#                 'is_first_login': is_first_login,
#                 'redirect': '/dashboard/'
#             })
#         else:
#             return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
    
#     except User.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'User not found'}, status=400)
#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# def user_logout(request):
#     """User Logout"""
#     logout(request)
#     return redirect('alerts:landing')


# # ============================================================
# # DASHBOARD VIEWS
# # ============================================================

# @login_required(login_url='alerts:login')
# def dashboard(request):
#     """User Dashboard"""
#     profile = request.user.profile
#     alerts = EmergencyAlert.objects.filter(user=request.user)
#     notifications = Notification.objects.filter(user=request.user)
    
#     context = {
#         'user': request.user,
#         'profile': profile,
#         'alerts': alerts,
#         'notifications': notifications,
#         'unread_count': notifications.filter(is_read=False).count(),
#         'total_alerts': alerts.count(),
#         'pending_alerts': alerts.filter(status='pending').count(),
#         'progress_alerts': alerts.filter(status='in_progress').count(),
#         'resolved_alerts': alerts.filter(status='resolved').count(),
#     }
#     return render(request, 'safenet/dashboard.html', context)


# @login_required(login_url='alerts:login')
# def admin_dashboard(request):
#     """Admin Dashboard - Only for superusers"""
#     if not request.user.is_superuser:
#         return redirect('alerts:dashboard')
    
#     all_alerts = EmergencyAlert.objects.all()
#     all_users = User.objects.filter(is_superuser=False)
    
#     context = {
#         'all_alerts': all_alerts,
#         'all_users': all_users,
#         'total_alerts': all_alerts.count(),
#         'total_users': all_users.count(),
#         'pending_alerts': all_alerts.filter(status='pending').count(),
#         'progress_alerts': all_alerts.filter(status='in_progress').count(),
#         'resolved_alerts': all_alerts.filter(status='resolved').count(),
#         'critical_alerts': all_alerts.filter(severity='critical').count(),
#     }
#     return render(request, 'safenet/dashboard.html', context)


# # ============================================================
# # ALERT VIEWS
# # ============================================================

# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def save_alert(request):
#     """Save Emergency Alert with optional image upload"""
#     try:
#         print(f"POST Data: {request.POST}")
#         print(f"FILES: {request.FILES}")
        
#         category = request.POST.get('category', '').lower()
#         message = request.POST.get('message', '').strip()

#         # ✅ FIX: latitude/longitude empty string గా వచ్చినా crash అవ్వకుండా handle చేయడం
#         lat_raw = request.POST.get('latitude', '').strip()
#         lng_raw = request.POST.get('longitude', '').strip()

#         if not lat_raw or not lng_raw:
#             return JsonResponse(
#                 {'success': False, 'error': 'Location not detected. Please allow location access and try again.'},
#                 status=400
#             )

#         try:
#             latitude = float(lat_raw)
#             longitude = float(lng_raw)
#         except ValueError:
#             return JsonResponse(
#                 {'success': False, 'error': 'Invalid latitude/longitude format'},
#                 status=400
#             )

#         location_name = request.POST.get('location_name', '')
#         image = request.FILES.get('image', None)
        
#         print(f"Category: {category}, Message: {message}, Image: {image}")
        
#         if not category or not message:
#             return JsonResponse({'success': False, 'error': 'Category and message required'}, status=400)
        
#         if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
#             return JsonResponse({'success': False, 'error': 'Invalid coordinates'}, status=400)
        
#         severity_map = {
#             'medical': 'critical',
#             'earthquake': 'critical',
#             'women_safety': 'high',
#             'accident': 'high',
#             'fire': 'high',
#             'flood': 'medium',
#         }
#         severity = request.POST.get('severity', 'medium')
        
#         alert = EmergencyAlert.objects.create(
#             user=request.user,
#             category=category,
#             message=message,
#             latitude=latitude,
#             longitude=longitude,
#             location_name=location_name,
#             image=image,
#             severity=severity,
#             status='pending'
#         )
        
#         Notification.objects.create(
#             user=request.user,
#             alert=alert,
#             title='Alert Received',
#             message=f'Your {category.title()} alert has been received.'
#         )
        
#         admins = User.objects.filter(is_superuser=True)
#         for admin in admins:
#             Notification.objects.create(
#                 user=admin,
#                 alert=alert,
#                 title='New Emergency Alert',
#                 message=f'{request.user.first_name} reported a {category.title()} emergency.'
#             )
        
#         print(f"Alert created successfully: {alert.id}")
        
#         return JsonResponse({
#             'success': True,
#             'message': 'Emergency alert submitted successfully!',
#             'alert': {
#                 'id': alert.id,
#                 'category': alert.category,
#                 'message': alert.message,
#                 'latitude': alert.latitude,
#                 'longitude': alert.longitude,
#                 'severity': alert.severity,
#                 'status': alert.status,
#                 'created_at': alert.created_at.isoformat(),
#                 'location_name': alert.location_name,
#             }
#         })
    
#     except Exception as e:
#         print(f"Error in save_alert: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_user_alerts(request):
#     """Get user's alerts"""
#     alerts = EmergencyAlert.objects.filter(user=request.user).values(
#         'id', 'category', 'message', 'latitude', 'longitude', 'severity', 'status', 'location_name', 'created_at'
#     )
#     return JsonResponse({
#         'success': True,
#         'alerts': list(alerts)
#     })


# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_all_alerts(request):
#     """Get all alerts (admin only)"""
#     if not request.user.is_superuser:
#         return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
#     alerts = EmergencyAlert.objects.values(
#         'id', 'user__username', 'user__first_name', 'category', 'message', 
#         'latitude', 'longitude', 'severity', 'status', 'location_name', 'created_at'
#     )
#     return JsonResponse({
#         'success': True,
#         'alerts': list(alerts)
#     })


# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def update_alert_status(request, alert_id):
#     """Update alert status (admin only)"""
#     if not request.user.is_superuser:
#         return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
#     try:
#         data = json.loads(request.body)
#         status = data.get('status', '').lower()
        
#         if status not in ['pending', 'in_progress', 'resolved']:
#             return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
#         alert = EmergencyAlert.objects.get(id=alert_id)
#         alert.status = status
        
#         if status == 'resolved':
#             alert.resolved_at = timezone.now()
        
#         alert.save()
        
#         Notification.objects.create(
#             user=alert.user,
#             alert=alert,
#             title='Status Update',
#             message=f'Your {alert.category.title()} alert is now {status.replace("_", " ").title()}.'
#         )
        
#         return JsonResponse({'success': True, 'message': 'Alert updated successfully'})
    
#     except EmergencyAlert.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def delete_alert(request, alert_id):
#     """Delete alert (admin only)"""
#     if not request.user.is_superuser:
#         return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
#     try:
#         alert = EmergencyAlert.objects.get(id=alert_id)
#         alert.delete()
#         return JsonResponse({'success': True, 'message': 'Alert deleted successfully'})
    
#     except EmergencyAlert.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# # ============================================================
# # PROFILE VIEWS
# # ============================================================

# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def update_profile(request):
#     """Update User Profile with optional profile image"""
#     try:
#         first_name = request.POST.get('first_name', request.user.first_name)
#         last_name = request.POST.get('last_name', request.user.last_name)
#         email = request.POST.get('email', request.user.email)
#         phone = request.POST.get('phone', '')
#         location = request.POST.get('location', '')
#         profile_image = request.FILES.get('profile_image', None)
        
#         # Update user info
#         request.user.first_name = first_name
#         request.user.last_name = last_name
#         request.user.email = email
#         request.user.save()
        
#         # Update profile info
#         profile = request.user.profile
#         profile.phone = phone
#         profile.location = location
#         if profile_image:
#             profile.profile_image = profile_image
#         profile.save()
        
#         return JsonResponse({
#             'success': True,
#             'message': 'Profile updated successfully!',
#             'user': {
#                 'first_name': request.user.first_name,
#                 'last_name': request.user.last_name,
#                 'email': request.user.email,
#                 'phone': profile.phone,
#                 'location': profile.location,
#                 'profile_image': profile.profile_image.url if profile.profile_image else None
#             }
#         })
    
#     except Exception as e:
#         print(f"Error updating profile: {e}")
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_profile(request):
#     """Get user profile"""
#     try:
#         profile = request.user.profile
#         return JsonResponse({
#             'success': True,
#             'user': {
#                 'first_name': request.user.first_name,
#                 'last_name': request.user.last_name,
#                 'email': request.user.email,
#                 'phone': profile.phone,
#                 'location': profile.location,
#                 'profile_image': profile.profile_image.url if profile.profile_image else None,
#                 'theme': profile.theme,
#             }
#         })
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def change_password(request):
#     """Change Password"""
#     try:
#         data = json.loads(request.body)
#         old_password = data.get('old_password', '')
#         new_password = data.get('new_password', '')
#         confirm_password = data.get('confirm_password', '')
        
#         if not request.user.check_password(old_password):
#             return JsonResponse({'success': False, 'error': 'Old password is incorrect'}, status=400)
        
#         if new_password != confirm_password:
#             return JsonResponse({'success': False, 'error': 'New passwords do not match'}, status=400)
        
#         if len(new_password) < 6:
#             return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters'}, status=400)
        
#         request.user.set_password(new_password)
#         request.user.save()
        
#         return JsonResponse({'success': True, 'message': 'Password changed successfully'})
    
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def update_theme(request):
#     """Update User Theme"""
#     try:
#         data = json.loads(request.body)
#         theme = data.get('theme', 'dark')
        
#         valid_themes = ['dark', 'light', 'blue', 'red']
#         if theme not in valid_themes:
#             return JsonResponse({'success': False, 'error': 'Invalid theme'}, status=400)
        
#         profile = request.user.profile
#         profile.theme = theme
#         profile.save()
        
#         return JsonResponse({'success': True, 'message': 'Theme updated successfully', 'theme': theme})
    
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# # ============================================================
# # NOTIFICATION VIEWS
# # ============================================================

# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_notifications(request):
#     """Get user notifications"""
#     notifications = Notification.objects.filter(user=request.user).values(
#         'id', 'title', 'message', 'is_read', 'created_at'
#     )
#     return JsonResponse({
#         'success': True,
#         'notifications': list(notifications),
#         'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
#     })


# @login_required(login_url='alerts:login')
# @require_http_methods(["POST"])
# def mark_notification_read(request, notification_id):
#     """Mark notification as read"""
#     try:
#         notification = Notification.objects.get(id=notification_id, user=request.user)
#         notification.is_read = True
#         notification.save()
#         return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    
#     except Notification.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)


# # ============================================================
# # STATS VIEWS
# # ============================================================

# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_dashboard_stats(request):
#     """Get dashboard statistics"""
#     alerts = EmergencyAlert.objects.filter(user=request.user)
    
#     return JsonResponse({
#         'success': True,
#         'stats': {
#             'total_alerts': alerts.count(),
#             'pending': alerts.filter(status='pending').count(),
#             'in_progress': alerts.filter(status='in_progress').count(),
#             'resolved': alerts.filter(status='resolved').count(),
#             'critical': alerts.filter(severity='critical').count(),
#             'high': alerts.filter(severity='high').count(),
#             'medium': alerts.filter(severity='medium').count(),
#         }
#     })


# @login_required(login_url='alerts:login')
# @require_http_methods(["GET"])
# def get_admin_stats(request):
#     """Get admin statistics"""
#     if not request.user.is_superuser:
#         return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
#     all_alerts = EmergencyAlert.objects.all()
#     all_users = User.objects.filter(is_superuser=False)
    
#     return JsonResponse({
#         'success': True,
#         'stats': {
#             'total_alerts': all_alerts.count(),
#             'total_users': all_users.count(),
#             'pending': all_alerts.filter(status='pending').count(),
#             'in_progress': all_alerts.filter(status='in_progress').count(),
#             'resolved': all_alerts.filter(status='resolved').count(),
#             'critical': all_alerts.filter(severity='critical').count(),
#             'high': all_alerts.filter(severity='high').count(),
#             'resolution_rate': round((all_alerts.filter(status='resolved').count() / max(all_alerts.count(), 1)) * 100),
#         }
#     })




from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import UserProfile, EmergencyAlert, Notification


# ============================================================
# AUTH VIEWS
# ============================================================

def landing(request):
    """Landing page - accessible to everyone"""
    # if request.user.is_authenticated:
    #     return redirect('alerts:dashboard')
    return render(request, 'safenet/index.html')


@require_http_methods(["POST"])
def register(request):
    """User Registration"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not name or not email or not password:
            return JsonResponse({'success': False, 'error': 'All fields required'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already registered'}, status=400)
        
        if len(password) < 6:
            return JsonResponse({'success': False, 'error': 'Password must be 6+ characters'}, status=400)
        
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name.split()[0],
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        )
        
        UserProfile.objects.get_or_create(user=user, defaults={'is_first_login': True})
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Account created!',
            'redirect': '/dashboard/'
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def user_login(request):
    """User Login"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return JsonResponse({'success': False, 'error': 'Email and password required'}, status=400)
        
        user = User.objects.get(email=email)
        user = authenticate(request, username=user.username, password=password)
        
        if user is not None:
            profile = user.profile
            is_first_login = profile.is_first_login
            profile.is_first_login = False
            profile.last_login_date = timezone.now()
            profile.save()
            
            login(request, user)
            
            message = "Welcome to SafeNet" if is_first_login else "Welcome Back"
            return JsonResponse({
                'success': True,
                'message': message,
                'is_first_login': is_first_login,
                'redirect': '/dashboard/'
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
    
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def user_logout(request):
    """User Logout"""
    logout(request)
    return redirect('alerts:landing')


# ============================================================
# DASHBOARD VIEWS
# ============================================================

@login_required(login_url='alerts:login')
def dashboard(request):
    """User Dashboard"""
    profile = request.user.profile
    alerts = EmergencyAlert.objects.filter(user=request.user)
    notifications = Notification.objects.filter(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
        'alerts': alerts,
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
        'total_alerts': alerts.count(),
        'pending_alerts': alerts.filter(status='pending').count(),
        'progress_alerts': alerts.filter(status='in_progress').count(),
        'resolved_alerts': alerts.filter(status='resolved').count(),
    }
    return render(request, 'safenet/dashboard.html', context)


@login_required(login_url='alerts:login')
def admin_dashboard(request):
    """Admin Dashboard - Only for superusers"""
    if not request.user.is_superuser:
        return redirect('alerts:dashboard')
    
    all_alerts = EmergencyAlert.objects.all()
    all_users = User.objects.filter(is_superuser=False)
    
    context = {
        'all_alerts': all_alerts,
        'all_users': all_users,
        'total_alerts': all_alerts.count(),
        'total_users': all_users.count(),
        'pending_alerts': all_alerts.filter(status='pending').count(),
        'progress_alerts': all_alerts.filter(status='in_progress').count(),
        'resolved_alerts': all_alerts.filter(status='resolved').count(),
        'critical_alerts': all_alerts.filter(severity='critical').count(),
    }
    return render(request, 'safenet/dashboard.html', context)


# ============================================================
# ALERT VIEWS
# ============================================================

@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def save_alert(request):
    """Save Emergency Alert with optional image upload"""
    try:
        print(f"POST Data: {request.POST}")
        print(f"FILES: {request.FILES}")
        
        category = request.POST.get('category', '').lower()
        message = request.POST.get('message', '').strip()

        # latitude/longitude empty string గా వచ్చినా crash అవ్వకుండా handle చేయడం
        lat_raw = request.POST.get('latitude', '').strip()
        lng_raw = request.POST.get('longitude', '').strip()

        if not lat_raw or not lng_raw:
            return JsonResponse(
                {'success': False, 'error': 'Location not detected. Please allow location access and try again.'},
                status=400
            )

        try:
            latitude = float(lat_raw)
            longitude = float(lng_raw)
        except ValueError:
            return JsonResponse(
                {'success': False, 'error': 'Invalid latitude/longitude format'},
                status=400
            )

        # ✅ FIX: model field name is `address`, not `location_name`.
        # The form sends the field as "address" (see script.js fd.append('address', ...)),
        # so we read it with the same key Django will receive it under.
        address = request.POST.get('address', '').strip()

        # contact_phone is REQUIRED on the model (no blank=True), so validate it here
        contact_phone = request.POST.get('contact_phone', '').strip()
        if not contact_phone:
            return JsonResponse({'success': False, 'error': 'Contact phone is required'}, status=400)

        people_affected_raw = request.POST.get('people_affected', '0').strip()
        try:
            people_affected = int(people_affected_raw) if people_affected_raw else 0
        except ValueError:
            people_affected = 0

        image = request.FILES.get('image', None)
        
        print(f"Category: {category}, Message: {message}, Image: {image}")
        
        if not category or not message:
            return JsonResponse({'success': False, 'error': 'Category and message required'}, status=400)
        
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return JsonResponse({'success': False, 'error': 'Invalid coordinates'}, status=400)
        
        severity = request.POST.get('severity', 'medium')
        valid_severities = ['low', 'medium', 'high', 'critical']
        if severity not in valid_severities:
            severity = 'medium'
        
        alert = EmergencyAlert.objects.create(
            user=request.user,
            category=category,
            message=message,
            latitude=latitude,
            longitude=longitude,
            address=address,
            contact_phone=contact_phone,
            people_affected=people_affected,
            image=image,
            severity=severity,
            status='pending'
        )
        
        Notification.objects.create(
            user=request.user,
            alert=alert,
            title='Alert Received',
            message=f'Your {alert.get_category_display()} alert has been received.'
        )
        
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                alert=alert,
                title='New Emergency Alert',
                message=f'{request.user.first_name} reported a {alert.get_category_display()} emergency.'
            )
        
        print(f"Alert created successfully: {alert.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Emergency alert submitted successfully!',
            'alert': {
                'id': alert.id,
                'category': alert.category,
                'message': alert.message,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'severity': alert.severity,
                'status': alert.status,
                'created_at': alert.created_at.isoformat(),
                'address': alert.address,
            }
        })
    
    except Exception as e:
        print(f"Error in save_alert: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_user_alerts(request):
    """Get user's alerts"""
    alerts = EmergencyAlert.objects.filter(user=request.user).values(
        'id', 'category', 'message', 'latitude', 'longitude', 'severity', 'status', 'address', 'created_at'
    )
    return JsonResponse({
        'success': True,
        'alerts': list(alerts)
    })


@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_all_alerts(request):
    """Get all alerts (admin only)"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    alerts = EmergencyAlert.objects.values(
        'id', 'user__username', 'user__first_name', 'category', 'message', 
        'latitude', 'longitude', 'severity', 'status', 'address', 'created_at'
    )
    return JsonResponse({
        'success': True,
        'alerts': list(alerts)
    })


@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def update_alert_status(request, alert_id):
    """Update alert status (admin only)"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        status = data.get('status', '').lower()
        
        if status not in ['pending', 'in_progress', 'resolved']:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        alert = EmergencyAlert.objects.get(id=alert_id)
        alert.status = status
        
        if status == 'resolved':
            alert.resolved_at = timezone.now()
        
        alert.save()
        
        Notification.objects.create(
            user=alert.user,
            alert=alert,
            title='Status Update',
            message=f'Your {alert.get_category_display()} alert is now {status.replace("_", " ").title()}.'
        )
        
        return JsonResponse({'success': True, 'message': 'Alert updated successfully'})
    
    except EmergencyAlert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def delete_alert(request, alert_id):
    """Delete alert (admin only)"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        alert = EmergencyAlert.objects.get(id=alert_id)
        alert.delete()
        return JsonResponse({'success': True, 'message': 'Alert deleted successfully'})
    
    except EmergencyAlert.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Alert not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# PROFILE VIEWS
# ============================================================

@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def update_profile(request):
    """Update User Profile with optional profile image"""
    try:
        first_name = request.POST.get('first_name', request.user.first_name)
        last_name = request.POST.get('last_name', request.user.last_name)
        email = request.POST.get('email', request.user.email)
        phone = request.POST.get('phone', '')
        location = request.POST.get('location', '')
        profile_image = request.FILES.get('profile_image', None)
        
        # Update user info
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        # Update profile info
        profile = request.user.profile
        profile.phone = phone
        profile.location = location
        if profile_image:
            profile.profile_image = profile_image
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully!',
            'user': {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': profile.phone,
                'location': profile.location,
                'profile_image': profile.profile_image.url if profile.profile_image else None
            }
        })
    
    except Exception as e:
        print(f"Error updating profile: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_profile(request):
    """Get user profile"""
    try:
        profile = request.user.profile
        return JsonResponse({
            'success': True,
            'user': {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': profile.phone,
                'location': profile.location,
                'profile_image': profile.profile_image.url if profile.profile_image else None,
                'theme': profile.theme,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def change_password(request):
    """Change Password"""
    try:
        data = json.loads(request.body)
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not request.user.check_password(old_password):
            return JsonResponse({'success': False, 'error': 'Old password is incorrect'}, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'error': 'New passwords do not match'}, status=400)
        
        if len(new_password) < 6:
            return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters'}, status=400)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def update_theme(request):
    """Update User Theme"""
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'dark')
        
        valid_themes = ['dark', 'light', 'blue', 'red']
        if theme not in valid_themes:
            return JsonResponse({'success': False, 'error': 'Invalid theme'}, status=400)
        
        profile = request.user.profile
        profile.theme = theme
        profile.save()
        
        return JsonResponse({'success': True, 'message': 'Theme updated successfully', 'theme': theme})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# NOTIFICATION VIEWS
# ============================================================

@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_notifications(request):
    """Get user notifications"""
    notifications = Notification.objects.filter(user=request.user).values(
        'id', 'title', 'message', 'is_read', 'created_at'
    )
    return JsonResponse({
        'success': True,
        'notifications': list(notifications),
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })


@login_required(login_url='alerts:login')
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True, 'message': 'Notification marked as read'})
    
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# STATS VIEWS
# ============================================================

@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_dashboard_stats(request):
    """Get dashboard statistics"""
    alerts = EmergencyAlert.objects.filter(user=request.user)
    
    return JsonResponse({
        'success': True,
        'stats': {
            'total_alerts': alerts.count(),
            'pending': alerts.filter(status='pending').count(),
            'in_progress': alerts.filter(status='in_progress').count(),
            'resolved': alerts.filter(status='resolved').count(),
            'critical': alerts.filter(severity='critical').count(),
            'high': alerts.filter(severity='high').count(),
            'medium': alerts.filter(severity='medium').count(),
        }
    })


@login_required(login_url='alerts:login')
@require_http_methods(["GET"])
def get_admin_stats(request):
    """Get admin statistics"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    all_alerts = EmergencyAlert.objects.all()
    all_users = User.objects.filter(is_superuser=False)
    
    return JsonResponse({
        'success': True,
        'stats': {
            'total_alerts': all_alerts.count(),
            'total_users': all_users.count(),
            'pending': all_alerts.filter(status='pending').count(),
            'in_progress': all_alerts.filter(status='in_progress').count(),
            'resolved': all_alerts.filter(status='resolved').count(),
            'critical': all_alerts.filter(severity='critical').count(),
            'high': all_alerts.filter(severity='high').count(),
            'resolution_rate': round((all_alerts.filter(status='resolved').count() / max(all_alerts.count(), 1)) * 100),
        }
    })







