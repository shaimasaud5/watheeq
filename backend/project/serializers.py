from rest_framework import serializers
from django.db import transaction
from .models import Project, Meeting, Document
from transcript.models import Transcript


class CreateProjectSerializer(serializers.Serializer):
    project_name = serializers.CharField(max_length=200)
    meeting_title = serializers.CharField(max_length=200)
    document_type = serializers.ChoiceField(choices=["BRD", "SRS", "MOM"])
    transcript_raw = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]

        # الآن: نركز على BRD فقط
        if validated_data["document_type"] != "BRD":
            raise serializers.ValidationError({"document_type": "Only BRD is supported for now."})

        project = Project.objects.create(
            owner=request.user,
            name=validated_data["project_name"],
        )

        meeting = Meeting.objects.create(
            project=project,
            title=validated_data["meeting_title"],
        )

        document = Document.objects.create(
            project=project,
            doc_type="BRD",
            content="",
        )
        Transcript.objects.create(
        meeting=meeting,
        raw_text=validated_data["transcript_raw"],
        processed_text=validated_data["transcript_raw"],  # مؤقت
        )

        return {
            "project_id": project.id,
            "meeting_id": meeting.id,
            "document_id": document.id,
            "doc_type": document.doc_type,
        }
"""from rest_framework import serializers
from .models import Project, Document

class AddDocumentSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=["BRD", "SRS", "MOM"])

    def validate(self, attrs):
        project = self.context["project"]
        doc_type = attrs["document_type"]

        # ما نسمح بتكرار نفس النوع
        if Document.objects.filter(project=project, doc_type=doc_type).exists():
            raise serializers.ValidationError({"document_type": "This document type already exists for this project."})

        return attrs

    def create(self, validated_data):
        project = self.context["project"]
        doc_type = validated_data["document_type"]

        doc = Document.objects.create(
            project=project,
            doc_type=doc_type,
            content=""
        )
        return {"document_id": doc.id, "doc_type": doc.doc_type}"""