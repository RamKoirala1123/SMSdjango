from functools import partial
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
# Create your views here.

from department.serializers import DepartmentAssignsSerializer, DepartmentSerializer, SectionSerializer
from department.models import Department, Sections, DepartmentAssigns
from department.permissions import IsTeacherOrStaff


class DepartmentsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        department = Department.objects.all()
        serializer = DepartmentSerializer(
            department, context={'request': request}, many=True)
        return JsonResponse(serializer.data, status=200, safe=False)


class DepartmentDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, name):
        try:
            department = Department.objects.get(name=name)
            serializer = DepartmentSerializer(
                department, context={'request': request})
            return JsonResponse(serializer.data, status=200, safe=False)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department does not exist'}, status=404)


class SectionDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, name):
        if name.lower() == 'all':
            sections = Sections.objects.all()
            serializer = SectionSerializer(sections, many=True)
            return JsonResponse(serializer.data, status=200, safe=False)
        else:
            try:
                section = Sections.objects.get(name=name)
                serializer = SectionSerializer(section, many=False)
                return JsonResponse(serializer.data, status=200, safe=True)
            except Sections.DoesNotExist:
                return JsonResponse({'error': 'Section does not exist'}, status=404)


# class SectionsView(APIView):
#     permission_classes = (AllowAny,)

#     def get(self, request):
#         sections = Sections.objects.all()
#         serializer = SectionSerializer(
#             sections, context={'request': request}, many=True)
#         return JsonResponse(serializer.data, status=200, safe=True)


class AssignTeacherView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStaff)
    parser_classes = (JSONParser,)

    def post(self, request, departname):
        if request.user.usertype == 'staff':
            try:
                department_assigns = DepartmentAssigns.objects.filter(
                    department__name=departname)
                if department_assigns.exists():
                    serializer = DepartmentAssignsSerializer(
                        department_assigns, many=True)
                    return JsonResponse(serializer.data, status=200, safe=False)
                else:
                    return JsonResponse({'error': 'Department does not exist'}, status=404)

            except DepartmentAssigns.DoesNotExist:
                return JsonResponse({'error': 'Department has no assigned teachers'}, status=404)
        else:
            user = request.user
            teacherassigned = DepartmentAssigns.objects.filter(
                user=user).exclude(enddate__lt=(timezone.now().date() + timezone.timedelta(days=-1)))
            if teacherassigned.exists():
                serializer = DepartmentAssignsSerializer(
                    teacherassigned, many=True)
                return JsonResponse(serializer.data, status=200, safe=False)
            else:
                return JsonResponse({'error': 'You are not assigned to any department'}, status=404)

    def put(self, request, departname):
        if request.user.usertype == 'staff':
            try:
                departmentname = request.data.get('departmentname')
                user = request.data.get('username')
                department = DepartmentAssigns.objects.get(
                    department__name=departmentname, user__username=user)
                serializer = DepartmentAssignsSerializer(
                    department, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=200, safe=False)
                return JsonResponse(serializer.errors, status=400)
            except DepartmentAssigns.DoesNotExist:
                department = DepartmentAssignsSerializer(
                    data=request.data)
                if department.is_valid():
                    department.save()
                    return JsonResponse(department.data, status=200, safe=False)
                return JsonResponse(department.errors, status=400)
        else:
            return JsonResponse({'error': 'You are not staff'}, status=404)


class DepartmentAssignsDetailView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStaff)

    def post(self, request, departname, username):
        if request.user.usertype == 'staff':
            try:
                department_assigns = DepartmentAssigns.objects.filter(
                    department__name=departname, user__username=username)
                if department_assigns.exists():
                    serializer = DepartmentAssignsSerializer(
                        department_assigns, many=True)
                    return JsonResponse(serializer.data, status=200, safe=False)
                else:
                    return JsonResponse({'error': 'Department does not exist'}, status=404)

            except DepartmentAssigns.DoesNotExist:
                return JsonResponse({'error': 'Department has no assigned teachers'}, status=404)
        else:
            return JsonResponse({'error': 'Restricted'}, status=404)

    def delete(self, request, departname, username):
        if request.user.usertype == 'staff':
            try:
                department_assigns = DepartmentAssigns.objects.filter(
                    department__name=departname, user__username=username)
                if department_assigns.exists():
                    department_assigns.delete()
                    return JsonResponse({'message': 'Teacher has been removed from department'}, status=200, safe=True)
                else:
                    return JsonResponse({'error': 'Department does not exist'}, status=404)

            except DepartmentAssigns.DoesNotExist:
                return JsonResponse({'error': 'Department has no assigned teachers'}, status=404)
        else:
            return JsonResponse({'error': 'You are not allowed to remove teachers'}, status=404)
