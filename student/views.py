from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.
from student.models import Student
from student.serializers import StudentSerializer


class StudentView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(student, many=False)
            return JsonResponse(serializer.data, safe=False, status=200)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student does not exist'}, status=400)

    def put(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(
                student, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student does not exist'}, status=400)
