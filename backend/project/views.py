from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import Project, Meeting, Document
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CreateProjectSerializer
from django.shortcuts import get_object_or_404
#from .serializers import AddDocumentSerializer

@csrf_exempt
#@login_required
def create_project_meeting_brd(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
        

    data = json.loads(request.body.decode("utf-8"))

    # مؤقتًا: نخلي النوع BRD فقط
    doc_type = data.get("document_type", "BRD")
    if doc_type != "BRD":
        return JsonResponse({"error": "Only BRD is supported for now."}, status=400)

    with transaction.atomic():
        project = Project.objects.create(
            #owner=request.user,
            name=data.get("project_name", "").strip()
        )

        meeting = Meeting.objects.create(
            project=project,
            title=data.get("meeting_title", "").strip(),
        )

        document = Document.objects.create(
            project=project,
            doc_type="BRD",
            content=""
        )

    return JsonResponse({
        "project_id": project.id,
        "meeting_id": meeting.id,
        "document_id": document.id,
        "doc_type": document.doc_type
    }, status=201)




class CreateProjectAPI(APIView):
    def post(self, request):
        serializer = CreateProjectSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=201)
    


"""class AddDocumentAPI(APIView):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, owner=request.user)

        serializer = AddDocumentSerializer(
            data=request.data,
            context={"project": project}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=201)"""