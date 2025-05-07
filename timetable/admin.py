from django.contrib import admin
from django import forms
from .models import Course, Room, TimeSlot, FacultyAvailability, Class, Enrollment, ConflictReport, PotentialConflict, FacultyCourse


class ClassAdminForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        faculty = cleaned_data.get('faculty')
        time_slot = cleaned_data.get('time_slot')
        course = cleaned_data.get('course')
        section = cleaned_data.get('section')

        # Validate faculty availability
        if faculty and time_slot:
            is_available = FacultyAvailability.objects.filter(
                faculty=faculty,
                time_slot=time_slot,
                is_available=True
            ).exists()
            if not is_available:
                raise forms.ValidationError(
                    f"Faculty {faculty.username} is not available for the selected time slot {time_slot}."
                )

        # Validate course-section uniqueness
        if course and section:
            existing_class = Class.objects.filter(
                course=course,
                section=section
            ).exclude(pk=self.instance.pk if self.instance else None).exists()
            if existing_class:
                raise forms.ValidationError(
                    f"A class for course {course.code} (section {section}) already exists."
                )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'hours_per_week']
    search_fields = ['code', 'name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_lab')
    list_filter = ('is_lab',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time')
    list_filter = ('day',)

@admin.register(FacultyAvailability)
class FacultyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'time_slot', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('faculty__username',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['course', 'section', 'time_slot', 'room', 'faculty', 'class_type', 'is_manual']
    list_filter = ['course', 'class_type', 'is_manual']
    search_fields = ['course__code', 'section']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'section')
    list_filter = ('course',)
    search_fields = ('student__username', 'course__code')

@admin.register(ConflictReport)
class ConflictReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'user__role')
    search_fields = ('user__username', 'description')
    filter_horizontal = ('classes',)



@admin.register(PotentialConflict)
class PotentialConflictAdmin(admin.ModelAdmin):
    list_display = ('user', 'detected_at')
    list_filter = ('user__role',)
    search_fields = ('user__username', 'description')
    filter_horizontal = ('classes',)




# Register FacultyCourse
@admin.register(FacultyCourse)
class FacultyCourseAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'course')
    list_filter = ('faculty', 'course')
    search_fields = ('faculty__username', 'course__code')