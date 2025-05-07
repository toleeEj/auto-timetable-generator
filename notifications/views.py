from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    if request.user.role not in ['student', 'faculty']:
        return render(request, 'timetable/error.html', {'message': 'Only students and faculty can view notifications.'})
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'notifications': notifications,
        'user_role': request.user.role,
    }
    return render(request, 'notifications/notification_list.html', context)