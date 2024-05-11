from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from teacher.serializers import TeacherSerializer
from teacher.models import Teacher
from teacher.permissions import IsATeacher


class TeacherView(APIView):
    permission_classes = [IsAuthenticated, IsATeacher]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            teacher = Teacher.objects.get(user__id=request.user.id)
            serializer = TeacherSerializer(teacher, context={
                'request': request}, many=False)
            return JsonResponse(serializer.data, status=200)

        except Teacher.DoesNotExist:
            return JsonResponse({'error': 'Teacher does not exist'}, status=404)

    def put(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(user__id=request.user.id)
        serializer = TeacherSerializer(instance=teacher, context={
                                       'request': request}, data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200, safe=False)
        else:
            return JsonResponse(serializer.errors, status=400)

# Create your views here.
