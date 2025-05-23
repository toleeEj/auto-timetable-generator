# Generated by Django 5.2 on 2025-05-02 08:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('timetable', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conflictreport',
            name='classes',
            field=models.ManyToManyField(related_name='conflict_reports', to='timetable.class'),
        ),
        migrations.AddField(
            model_name='conflictreport',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='class',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='student',
            field=models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='facultyavailability',
            name='faculty',
            field=models.ForeignKey(limit_choices_to={'role': 'faculty'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='facultycourse',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course'),
        ),
        migrations.AddField(
            model_name='facultycourse',
            name='faculty',
            field=models.ForeignKey(limit_choices_to={'role': 'faculty'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='failedschedule',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.course'),
        ),
        migrations.AddField(
            model_name='potentialconflict',
            name='classes',
            field=models.ManyToManyField(related_name='potential_conflicts', to='timetable.class'),
        ),
        migrations.AddField(
            model_name='potentialconflict',
            name='user',
            field=models.ForeignKey(limit_choices_to={'role__in': ['student', 'faculty']}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='class',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.room'),
        ),
        migrations.AlterUniqueTogether(
            name='timeslot',
            unique_together={('day', 'start_time', 'end_time')},
        ),
        migrations.AddField(
            model_name='facultyavailability',
            name='time_slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.timeslot'),
        ),
        migrations.AddField(
            model_name='class',
            name='time_slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timetable.timeslot'),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'course', 'section')},
        ),
        migrations.AlterUniqueTogether(
            name='facultycourse',
            unique_together={('faculty', 'course')},
        ),
        migrations.AlterUniqueTogether(
            name='facultyavailability',
            unique_together={('faculty', 'time_slot')},
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('room', 'faculty', 'time_slot')},
        ),
    ]
