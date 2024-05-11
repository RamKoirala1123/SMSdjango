from json import JSONEncoder
from tempfile import TemporaryFile
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from assignments.models import Assignment, StudentSubmitsAssignment

from assignments.serializers import AssignmentsSerializer, StudentAssignmentSerializer
from assignments.permissions import IsTeacherOrStudent
from courses.models import Courses, StudentJoinedCourses
from authentication.models import User
# Create your views here.


class AssignmentView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, course_id, *args, **kwargs):
        try:
            user = request.user
            if request.user.usertype == 'student':
                studentjoin = StudentJoinedCourses.objects.filter(
                    student=user, course__id=course_id)
                if not studentjoin.exists():
                    return JsonResponse({'error': 'You are not enrolled in this course'}, status=400)
            else:
                course = user.courses_set.filter(id=course_id)
                if not course.exists():
                    return JsonResponse({'error': 'You are not a teacher of this course'}, status=400)
            course = Courses.objects.get(id=course_id)
            assignments = course.assignment_set.all()
            serializer = AssignmentsSerializer(
                assignments, context={"request": request}, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'Course does not exist'}, status=400)

    def put(self, request, course_id, *args, **kwargs):
        if request.user.usertype == "teacher":
            user = request.user
            try:
                courses = user.courses_set.get(id=course_id)
                serializer = AssignmentsSerializer(
                    data=request.data, context={'request': request})
                if serializer.is_valid():
                    serializer.save(course=courses)
                    return JsonResponse(serializer.data, status=201)
                return JsonResponse(serializer.errors, status=400)
            except Courses.DoesNotExist:
                return JsonResponse({"error": "Course does not exist"}, status=400)
        return JsonResponse({'error': 'You are a student'}, status=400)


class AssignmentDetailView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, course_id, assignment_id, *args, **kwargs):
        try:
            if request.user.usertype == "student":
                course_name = request.user.studentjoinedcourses_set.get(course__id=course_id)
                course = course_name.course
            else:
                course = request.user.courses_set.get(id=course_id)
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'You are not enrolled in this course'}, status=400)

        try:
            assignment = course.assignment_set.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return JsonResponse({'error': 'Assignment does not exist'}, status=400)

        serializer = AssignmentsSerializer(
            assignment, context={'request': request})
        return JsonResponse(serializer.data, status=200)

    def put(self, request, course_id, assignment_id, *args, **kwargs):
        if request.user.usertype == "teacher":
            user = request.user
            try:
                assignment = Assignment.objects.get(
                    id=assignment_id, course__teacher=user, course_id=course_id)

                serializer = AssignmentsSerializer(
                    assignment, data=request.data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=201)
                return JsonResponse(serializer.errors, status=400)
            except Assignment.DoesNotExist:
                return JsonResponse({"error": "Assignment does not exist"}, status=400)
        return JsonResponse({'error': 'You are not a teacher'}, status=400)

    def delete(self, request, course_id, assignment_id, *args, **kwargs):
        if request.user.usertype == "teacher":
            try:
                user = request.user
                assignment = Assignment.objects.get(
                    id=assignment_id, course__teacher=user, course_id=course_id)
                assignment.delete()
                return JsonResponse({'message': 'Assignment deleted'}, status=200)
            except Assignment.DoesNotExist:
                return JsonResponse({"error": "Assignment does not exist"}, status=400)
        return JsonResponse({'error': 'You are not a teacher'}, status=400)


class StudentSubmitsAssignmentView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, course_id, assignment_id, username, *args, **kwargs):
        if request.user.usertype == 'student' and request.user.username != username:
            return JsonResponse({'error': 'You are not allowed to see assignment'}, status=400)
        try:
            user = User.objects.get(username=username)
        except User.DoesnotExist:
            return JsonResponse({'error': 'User does not exist'}, status=400)
        try:
            if request.user.usertype == "teacher":
                course = request.user.courses_set.get(id=course_id)
            else:
                try:
                    course_name = user.studentjoinedcourses_set.get(course__id=course_id)
                    course = course_name.course
                except StudentJoinedCourses.DoesNotExist:
                    return JsonResponse("Student hasnot joined this course")
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'You are not a teacher of this course'}, status=400)

        try:
            studentassignment = StudentSubmitsAssignment.objects.get(
                 assignment__id=assignment_id, student=user)
            serializer = StudentAssignmentSerializer(
                studentassignment, context={"request": request})
            return JsonResponse(serializer.data, status=200)
        except StudentSubmitsAssignment.DoesNotExist:
            return JsonResponse({'error': 'The data do not match each other'}, status=400)

    # def put(self, request, course_id, assignment_id, *args, **kwargs):
    #     if request.user.usertype == 'student':
    #         studentcourse = StudentJoinedCourses.objects.filter(
    #             course_id=course_id, student=request.user)
    #         if not studentcourse.exists():
    #             return JsonResponse({'error': 'You are not enrolled in this course'}, status=400)
    #         try:
    #             assignment = StudentSubmitsAssignment.objects.get(
    #                 assignment__id=assignment_id, student=request.user)
    #             serializer = StudentAssignmentSerializer(
    #                 instance=assignment, data=request.data, context={'request': request})
    #             if serializer.is_valid():      
    #                 serializer.save()
    #                 return JsonResponse(serializer.data, status=201)
    #             return JsonResponse(serializer.errors, status=400)
    #         except StudentSubmitsAssignment.DoesNotExist:
    #             return JsonResponse({'error': 'Assignment does not exist'}, status=400)
    #     return JsonResponse({'error': 'You are not a student'}, status=400
    def put(self, request, course_id, assignment_id, username, *args, **kwargs):
        if request.user.usertype == 'student' and request.user.username != username:
            return JsonResponse({'error': 'You are not allowed to see assignment'}, status=400)
        if request.user.usertype == 'student':
            studentcourse = StudentJoinedCourses.objects.filter(
                course_id=course_id, student=request.user)
            user = request.user
            if not studentcourse.exists():
                return JsonResponse({'error': 'You are not enrolled in this course'}, status=400)
        else:
            user = User.objects.filter(username=username)
            if not user.exists():
                return JsonResponse({'error': 'User does not exist'}, status=400)
            user = user.first()
            try:
                course = request.user.courses_set.get(id=course_id)
                assignment = course.assignment_set.get(id=assignment_id)
            except Courses.DoesNotExist or Assignment.DoesNotExist:
                return JsonResponse({'error': 'You are not a teacher of this course or owner of this assignment'}, status=400)

        try:
            assignment = StudentSubmitsAssignment.objects.get(
                assignment__id=assignment_id, student=user)
            serializer = StudentAssignmentSerializer(
                instance=assignment, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        except StudentSubmitsAssignment.DoesNotExist:
            return JsonResponse({'error': 'Assignment does not exist'}, status=400)
