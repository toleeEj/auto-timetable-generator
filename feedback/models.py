from django.db import models
from users.models import CustomUser
from timetable.models import Class

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    related_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.user.username}: {self.message}"

    class Meta:
        ordering = ['-created_at']