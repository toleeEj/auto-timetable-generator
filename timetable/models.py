from django.db import models

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    hours_per_week = models.PositiveIntegerField(default=1, help_text="Required hours per week for this course")

    def __str__(self):
        return f"{self.code}: {self.name}"

class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField()
    is_lab = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    day = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.day} {self.start_time:%H:%M}–{self.end_time:%H:%M}"

    class Meta:
        unique_together = ('day', 'start_time', 'end_time')

class FacultyAvailability(models.Model):
    faculty = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    time_slot = models.ForeignKey('timetable.TimeSlot', on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.faculty.username} - {self.time_slot}"

    class Meta:
        unique_together = ('faculty', 'time_slot')

class Class(models.Model):
    CLASS_TYPES = (
        ('theory', 'Theory'),
        ('lab', 'Lab'),
    )
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE)
    room = models.ForeignKey('timetable.Room', on_delete=models.CASCADE)
    time_slot = models.ForeignKey('timetable.TimeSlot', on_delete=models.CASCADE)
    faculty = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    section = models.CharField(max_length=10, blank=True)
    is_manual = models.BooleanField(default=False)
    class_type = models.CharField(max_length=10, choices=CLASS_TYPES, default='theory')

    class Meta:
        unique_together = ('room', 'faculty', 'time_slot')
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f"{self.course.code} ({self.section}) - {self.time_slot}"

class Enrollment(models.Model):
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE)
    section = models.CharField(max_length=10)  # Removed blank=True to require section

    def __str__(self):
        return f"{self.student.username} - {self.course.code} ({self.section})"

    class Meta:
        unique_together = ('student', 'course', 'section')

class ConflictReport(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    classes = models.ManyToManyField('timetable.Class', related_name='conflict_reports')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Conflict reported by {self.user.username} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']

class PotentialConflict(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role__in': ['student', 'faculty']})
    classes = models.ManyToManyField('timetable.Class', related_name='potential_conflicts')
    description = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Potential conflict for {self.user.username} on {self.detected_at}"

    class Meta:
        ordering = ['-detected_at']

class FacultyCourse(models.Model):
    faculty = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('faculty', 'course')
        verbose_name = 'Faculty Course'
        verbose_name_plural = 'Faculty Courses'

    def __str__(self):
        return f"{self.faculty.username} - {self.course.code}"

class FailedSchedule(models.Model):
    course = models.ForeignKey('timetable.Course', on_delete=models.CASCADE)
    section = models.CharField(max_length=10, blank=True)
    class_type = models.CharField(max_length=10, choices=Class.CLASS_TYPES, default='theory')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Failed: {self.course.code} ({self.section}, {self.class_type})"