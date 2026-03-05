from django.shortcuts import render
from pathlib import Path
import json
import re
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class ExtractAPIView(APIView):
   
    permission_classes = [AllowAny]

    OLLAMA_URL = "http://ollama:11434/api/generate"
    MODEL_NAME = "llama3.2" 

    def post(self, request, *args, **kwargs):
        transcript = request.data.get("transcript")
        if not transcript or not isinstance(transcript, str):
            return Response(
                {"error": "Please provide 'transcript' as a string."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        schema = self._load_schema()
        if isinstance(schema, Response):
            return schema  
        
        templet = self._empty_from_schema(schema)
        extracted=templet.copy()

        # LLM
        llm_result = self._extract_with_llm(transcript, schema)
        if llm_result is not None:
            #دمج الناتج على القالب (عشان نضمن نفس المفاتيح دائمًا)
            extracted = self._merge_into_template(extracted, llm_result)
            
            for k, v in extracted.items():
                if v == "null":
                    extracted[k] = None

        result = {
            "status": "ok",
            "received_chars": len(transcript),
            "preview": transcript[:120],
            "extracted": extracted,
        }
        return Response(result, status=status.HTTP_200_OK)

    # helpers 

    def _load_schema(self):
        schema_path = Path(__file__).parent / "schema.json"
        if not schema_path.exists():
            return Response(
                {"error": "schema.json not found in extract app folder."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            return json.loads(schema_path.read_text(encoding="utf-8"))
        except Exception as e:
            return Response(
                {"error": f"Failed to read schema.json: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _empty_from_schema(self, schema: dict) -> dict:
        
        output = {}
        properties = schema.get("properties", {})
        for key, prop in properties.items():
            t = prop.get("type")
            output[key] = [] if t == "array" else None
        return output

    def _merge_into_template(self, template: dict, llm_data: dict) -> dict:
        
        for k in template.keys():
            if k in llm_data:
                template[k] = llm_data[k]
        return template

    def _extract_with_llm(self, transcript: str, schema: dict):
        # نجيب كل المفاتيح من schema.json
        properties = schema.get("properties", {})
        required_keys = list(properties.keys())

        if not required_keys:
            # احتياط لو صار شيء غلط في السكيمة
            required_keys = ["executive_summary", "stakeholders", "risk_analysis"]

        list_fields = [
            name for name, prop in properties.items()
            if prop.get("type") == "array"
        ]

        prompt = f"""
You are a strict information extraction engine.

Extract structured data from the transcript and return JSON that matches
the top-level keys from a BRD schema.

Top-level JSON keys (MUST all be present):
{required_keys}

Array fields (MUST always be JSON arrays, even if empty):
{list_fields}

Rules:
- Return ONLY valid JSON (no markdown, no explanations).
- Use exactly the keys listed above. Do not invent new keys.
- If a field has no information, use null (or [] for array fields).
- You may return strings, objects, or arrays depending on the field.
- For array-of-objects fields, each item should be an object with
  reasonable fields based on the transcript (e.g. name, role, description, ...).

Transcript:
\"\"\"{transcript}\"\"\"

JSON:
"""
        try:
            resp = requests.post(
                self.OLLAMA_URL,
                json={
                    "model": self.MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0,
                    },
                },
                timeout=120,
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "")
        except Exception:
            return None

        json_text = self._extract_first_json_object(raw) or raw

        try:
            return json.loads(json_text)
        except Exception:
            return None


    def _extract_first_json_object(self, text: str):
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        return match.group(0) if match else None