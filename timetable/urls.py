from django.urls import path
from . import views

urlpatterns = [
    path('student-timetable/', views.student_timetable, name='student_timetable'),
    path('faculty-timetable/', views.faculty_timetable, name='faculty_timetable'),
    path('admin-timetable/', views.admin_timetable, name='admin_timetable'),
    path('generate/', views.generate_timetable, name='generate_timetable'),
    path('report-conflict/', views.report_conflict, name='report_conflict'),
    path('conflict-list/', views.conflict_list, name='conflict_list'),
    path('export-timetable/', views.export_timetable, name='export_timetable'),
]