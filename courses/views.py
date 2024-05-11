from functools import partial
from django.http import JsonResponse
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.

from courses.permissions import IsTeacherOrStudent
from courses.serializers import CoursesSerializer, StudentJoinedCoursesSerializer
from courses.models import Courses, StudentJoinedCourses
from authentication.models import User
from django_filters import rest_framework as filters


class CoursesView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)

    def post(self, request, *args, **kwargs):
        if request.user.usertype == "teacher":
            courses = request.user.courses_set.all()
            serializer = CoursesSerializer(
                courses, many=True, context={'request': request})
            return JsonResponse(serializer.data, safe=False)
        else:
            studentcourses = StudentJoinedCourses.objects.filter(
                student=request.user, accepted=True)
            data = []
            for record in studentcourses:
                data.append(CoursesSerializer(record.course,
                                          many=False, context={'request': request}).data)
            return JsonResponse(data, safe=False)

    def put(self, request, *args, **kwargs):
        if request.user.usertype == 'teacher':
            serializer = CoursesSerializer(data=request.data, context={
                                           'request': request}, many=False)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            else:
                return JsonResponse(serializer.errors, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)


class CoursesDetailView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)

    def put(self, request, course_id, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                user = request.user
                course = user.courses_set.get(id=course_id)
                serializer = CoursesSerializer(
                    course, data=request.data, context={"request": request}, many=False)
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=200)
                else:
                    return JsonResponse(serializer.errors, status=400)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)

    def delete(self, request, course_id, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                user = request.user
                course = user.courses_set.get(id=course_id)
                course.delete()
                return JsonResponse({'message': 'Course deleted successfully'}, status=200)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)

    def post(self, request, course_id):
        try:
            course = Courses.objects.get(id=course_id)
            serializer = CoursesSerializer(
                course, context={"request": request}, many=False)
            return JsonResponse(serializer.data, status=200)
        except:
            return JsonResponse({'error': 'Course does not exist'}, status=400)


class StudentJoinedCoursesDetailView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)

    def get(self, request, course_id, username):
        if request.user and request.user.is_authenticated:
            if request.user.usertype == "teacher":
                courses = StudentJoinedCourses.objects.filter(
                    student__username=username, course__id=course_id)
            else:
                courses = StudentJoinedCourses.objects.filter(
                    student=request.user, course__id=course_id)
            if courses.exists():
                serializer = StudentJoinedCoursesSerializer(courses)
                return JsonResponse(serializer.data, status=200)
            return JsonResponse({'error': 'Course does not exist'}, status=404)
        return JsonResponse({'error': 'You are not authorized to perform this action'}, status=404)

    def post(self, request, course_id, username):
        if request.user.usertype == "teacher":
            coursejoin = StudentJoinedCourses.objects.filter(
                course__id=course_id)
            if not coursejoin.exists():
                return JsonResponse({'error': 'Course does not exist or none have join this course'}, status=404)
        else:
            coursejoin = StudentJoinedCoursesSerializer.filter(
                student=request.user, accepted=True)
            if not coursejoin.exists():
                return JsonResponse({'error': 'You have not joined courses'}, status=404)
        serializer = StudentJoinedCoursesSerializer(coursejoin, many=True)
        return JsonResponse(serializer.data, safe=False)

    def put(self, request, course_id, username):
        if request.user.usertype == "student":
            request.data.pop('accepted')
        try:
            coursejoin = StudentJoinedCourses.objects.get(
                course__id=course_id, student__username=username)
            serializer = StudentJoinedCoursesSerializer(
                coursejoin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)
        except StudentJoinedCourses.DoesNotExist:
            user = User.objects.filter(username__iexact=username)
            data = None
            if not user.exists():
                data = {'error': 'User does not exist'}
            course = Courses.objects.filter(id=course_id)
            if not course.exists():
                data = {'error': 'Course does not exist'}
            if data:
                return JsonResponse(data, status=404)
            serializer = StudentJoinedCoursesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(course=course[0], student=user[0])
                return JsonResponse(serializer.data, status=200)
            return JsonResponse(serializer.errors, status=400)

    def delete(self, request, course_id, username):
        try:
            if request.user.usertype == "teacher":
                coursejoin = StudentJoinedCourses.objects.get(
                    course__id=course_id, student__username=username)
            else:
                coursejoin = StudentJoinedCourses.objects.get(
                    student=request.user, course__id=course_id)
            coursejoin.delete()
            return JsonResponse({'success': 'Course deleted successfully'}, status=200)
        except StudentJoinedCourses.DoesNotExist:
            return JsonResponse({'error': 'Course or user does not exist'}, status=404)


class CourseFilter(filters.FilterSet):
    class Meta:
        model = Courses
        fields = ['course_name', 'semester', 'year']


class SearchCoursesView(APIView):
    permissions_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        courses = Courses.objects.all()
        courses = CourseFilter(request.GET, queryset=courses)
        serializer = CoursesSerializer(
            courses.qs, context={"search": True, "request":request}, many=True)
        return JsonResponse(serializer.data, safe=False)
