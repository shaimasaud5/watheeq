from django.db import models

from django.conf import settings
from django.db import models


class Project(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Meeting(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="meeting")
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.name} - {self.title}"


class Document(models.Model):
    DOC_TYPES = [
        ("SRS", "SRS"),
        ("BRD", "BRD"),
        ("MOM", "MOM"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    doc_type = models.CharField(max_length=3, choices=DOC_TYPES)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "doc_type")

    def __str__(self):
        return f"{self.project.name} - {self.doc_type}"
