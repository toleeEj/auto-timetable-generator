from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from timetable.models import Class, Course, Room, TimeSlot, FacultyAvailability, Enrollment, PotentialConflict, FacultyCourse, FailedSchedule
from users.models import CustomUser
from notifications.models import Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from timetable.models import Class, Enrollment

@login_required
def student_timetable(request):
    from timetable.models import Class, Enrollment
    if request.user.role != 'student':
        return render(request, 'timetable/error.html', {'message': 'Only students can view this page.'})
    enrollments = Enrollment.objects.filter(student=request.user)
    classes = Class.objects.filter(
        course__in=Enrollment.objects.filter(student=request.user).values('course'),
        section__in=Enrollment.objects.filter(student=request.user).values('section')
    ).distinct()
    context = {
        'classes': classes,
        'user_role': request.user.role,
    }
    return render(request, 'timetable/student_timetable.html', context)

@login_required
def faculty_timetable(request):
    from timetable.models import Class
    from users.models import CustomUser
    if request.user.role != 'faculty':
        return render(request, 'timetable/error.html', {'message': 'Only faculty can view this page.'})
    classes = Class.objects.filter(faculty=request.user)
    context = {
        'classes': classes,
        'user_role': request.user.role,
    }
    return render(request, 'timetable/faculty_timetable.html', context)

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        print(f"DEBUG: User: {request.user.username}, Role: {request.user.role}, Authenticated: {request.user.is_authenticated}")
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        return render(request, 'timetable/error.html', {'message': 'Only admins can access this page.'})
    return wrapper

@login_required
@admin_required
def generate_timetable(request):
    import random
    from datetime import datetime, date

    if request.method == 'POST':
        Class.objects.filter(is_manual=False).delete()
        PotentialConflict.objects.all().delete()
        FailedSchedule.objects.all().delete()

        courses = Course.objects.all()
        rooms = Room.objects.all()
        time_slots = TimeSlot.objects.all().order_by('start_time')
        faculty = CustomUser.objects.filter(role='faculty')
        students = CustomUser.objects.filter(role='student')

        faculty_workload = {f.id: 0 for f in faculty}
        course_sections = {}

        for course in courses:
            sections = Enrollment.objects.filter(course=course).values('section').distinct()
            course_sections[course.id] = [s['section'] for s in sections]

        for course in courses:
            sections = course_sections.get(course.id, [])
            if not sections:
                continue

            for section in sections:
                enrollment_count = Enrollment.objects.filter(course=course, section=section).count()
                enrolled_students = Enrollment.objects.filter(course=course, section=section).values_list('student', flat=True)

                required_hours = course.hours_per_week
                scheduled_hours = 0

                for time_slot in time_slots:
                    if scheduled_hours >= required_hours:
                        break

                    # Calculate slot duration
                    start_dt = datetime.combine(date.today(), time_slot.start_time)
                    end_dt = datetime.combine(date.today(), time_slot.end_time)
                    slot_duration = int((end_dt - start_dt).total_seconds() // 3600)

                    # Check if slot already has class for any student
                    student_classes = Class.objects.filter(
                        section=section,
                        time_slot=time_slot
                    )
                    if student_classes.exists():
                        continue

                    # Faculty selection
                    available_faculty_ids = FacultyAvailability.objects.filter(
                        time_slot=time_slot, is_available=True
                    ).values_list('faculty', flat=True)
                    booked_faculty_ids = Class.objects.filter(
                        time_slot=time_slot
                    ).values_list('faculty', flat=True)
                    qualified_faculty_ids = FacultyCourse.objects.filter(course=course).values_list('faculty', flat=True)

                    valid_faculty = faculty.filter(
                        id__in=set(available_faculty_ids).intersection(qualified_faculty_ids)
                    ).exclude(id__in=booked_faculty_ids)

                    if not valid_faculty.exists():
                        continue

                    # Faculty with least load
                    valid_faculty = sorted(
                        [(f, faculty_workload[f.id]) for f in valid_faculty], key=lambda x: x[1]
                    )
                    selected_faculty = valid_faculty[0][0]

                    # Room selection
                    booked_room_ids = Class.objects.filter(time_slot=time_slot).values_list('room', flat=True)
                    available_rooms = rooms.exclude(id__in=booked_room_ids).filter(
                        capacity__gte=enrollment_count,
                        is_lab=False
                    )
                    if not available_rooms.exists():
                        continue

                    selected_room = available_rooms.first()

                    # Schedule the class
                    Class.objects.create(
                        course=course,
                        room=selected_room,
                        time_slot=time_slot,
                        faculty=selected_faculty,
                        section=section,
                        is_manual=False,
                        class_type='theory'
                    )

                    faculty_workload[selected_faculty.id] += 1
                    scheduled_hours += slot_duration

                # If we couldn't finish scheduling
                if scheduled_hours < required_hours:
                    FailedSchedule.objects.create(
                        course=course,
                        section=section,
                        class_type='theory',
                        reason=f"Insufficient time slots to allocate {required_hours} hours"
                    )

        return redirect('admin_dashboard')

    return render(request, 'timetable/generate_timetable.html')






# SIGNAL TO NOTIFY ON MANUAL CLASS CREATION
@receiver(post_save, sender=Class)
def send_class_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    # Check for room conflict
    if Class.objects.filter(time_slot=instance.time_slot, room=instance.room).exclude(id=instance.id).exists():
        conflict = PotentialConflict.objects.create(
            user=instance.faculty,
            description=f"Room conflict: Room {instance.room.name} has multiple classes at {instance.time_slot}"
        )
        conflict.classes.set(Class.objects.filter(time_slot=instance.time_slot, room=instance.room))
        Notification.objects.create(
            user=instance.faculty,
            message=conflict.description,
            related_class=instance
        )

    course = instance.course
    section = instance.section
    time_slot = instance.time_slot
    room = instance.room
    class_type = instance.class_type

    if instance.faculty:
        Notification.objects.create(
            user=instance.faculty,
            message=f"You are assigned to teach {course} ({section}, {class_type}) on {time_slot} in {room}.",
            related_class=instance
        )

    enrolled_students = Enrollment.objects.filter(course=course, section=section).values_list('student', flat=True)
    for student_id in enrolled_students:
        Notification.objects.create(
            user_id=student_id,
            message=f"You have been scheduled for {course} ({section}, {class_type}) on {time_slot} in {room}.",
            related_class=instance
        )


from collections import defaultdict
@login_required
@admin_required

def admin_timetable(request):
    from timetable.models import Class
    from users.models import CustomUser

    classes = Class.objects.all().order_by('time_slot__day', 'time_slot__start_time')

    grouped_classes = defaultdict(list)
    for cls in classes:
        grouped_classes[cls.section].append(cls)

    context = {
        'classes': classes,  # retained for compatibility
        'grouped_classes': dict(grouped_classes),
        'user_role': request.user.role,
    }
    return render(request, 'timetable/admin_timetable.html', context)


@login_required
def report_conflict(request):
    from timetable.models import Class, PotentialConflict
    from timetable.forms import ConflictReportForm
    from users.models import CustomUser
    if request.user.role not in ['student', 'faculty']:
        return render(request, 'timetable/error.html', {'message': 'Only students and faculty can report conflicts.'})
    
    potential_conflicts = PotentialConflict.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ConflictReportForm(request.POST, user=request.user)
        if form.is_valid():
            conflict_report = form.save(commit=False)
            conflict_report.user = request.user
            conflict_report.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = ConflictReportForm(user=request.user)
    
    context = {
        'form': form,
        'user_role': request.user.role,
        'potential_conflicts': potential_conflicts,
    }
    return render(request, 'timetable/report_conflict.html', context)

@login_required
@admin_required
def conflict_list(request):
    from timetable.models import ConflictReport
    from users.models import CustomUser
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        if report_id:
            ConflictReport.objects.filter(id=report_id).update(is_resolved=True)
            return redirect('conflict_list')
    
    reports = ConflictReport.objects.all().order_by('-created_at')
    context = {
        'reports': reports,
        'user_role': request.user.role,
    }
    return render(request, 'timetable/conflict_list.html', context)

@login_required
def export_timetable(request):
    from timetable.models import Class, Enrollment
    from users.models import CustomUser

    if request.user.role == 'student':
        classes = Class.objects.filter(
            course__in=Enrollment.objects.filter(student=request.user).values('course'),
            section__in=Enrollment.objects.filter(student=request.user).values('section')
        ).distinct()
    elif request.user.role == 'faculty':
        classes = Class.objects.filter(faculty=request.user)
    elif request.user.role == 'admin':
        classes = Class.objects.all().order_by('time_slot__day', 'time_slot__start_time')
    else:
        return render(request, 'timetable/error.html', {'message': 'Unauthorized access.'})

    # Group classes by section
    grouped_classes = defaultdict(list)
    for cls in classes:
        grouped_classes[cls.section].append(cls)

    # Prepare the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timetable_{request.user.role}_{request.user.username}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"{request.user.role.capitalize()} Timetable - {request.user.username}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Loop through each section and create a separate table
    for section, class_list in grouped_classes.items():
        elements.append(Paragraph(f"Section: {section or 'N/A'}", styles['Heading3']))
        data = [['Course', 'Day', 'Time', 'Room', 'Faculty', 'Type']]
        
        for cls in class_list:
            data.append([
                str(cls.course),
                cls.time_slot.day,
                f"{cls.time_slot.start_time.strftime('%H:%M')} - {cls.time_slot.end_time.strftime('%H:%M')}",
                cls.room.name,
                cls.faculty.username,
                cls.class_type.capitalize()
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))  # Space between tables

    doc.build(elements)
    return response