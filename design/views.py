# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from design.exceptions.exceptions import SubmissionError
from design.services import research_question_services
from .serializers import DraftQuestionVersionSerializer, QuestionSubmissionSerializer, QuestionVersionResponseSerializer

class SubmitQuestionVersionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id: int):
        serializer = QuestionSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_version = research_question_services.submit_question_for_review(
                    researcher=request.user,
                    question_id=question_id,
                    **serializer.validated_data
                )
                return Response({'version_id': new_version.id, 'status': new_version.status}, status=status.HTTP_201_CREATED)

            except research_question_services.SubmissionError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaveDraftAPIView(APIView):
    """Maneja las peticiones PUT para el guardado automático de borradores."""
    permission_classes = [IsAuthenticated]

    def put(self, request, question_id: int):
        serializer = DraftQuestionVersionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            draft_version = research_question_services.save_question_draft(
                researcher=request.user,
                question_id=question_id,
                **serializer.validated_data
            )
            data = serializer.validated_data
            print("hola")
            print(data)
            response_serializer = QuestionVersionResponseSerializer(draft_version) # Reutilizamos el serializer si aplica
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except SubmissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)