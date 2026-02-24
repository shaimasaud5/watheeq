from django.db import models
from project.models import Meeting


class Transcript(models.Model):
    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name="transcript"
    )
    raw_text = models.TextField()
    processed_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for Meeting #{self.meeting.id}"
