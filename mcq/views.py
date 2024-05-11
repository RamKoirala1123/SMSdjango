from json import JSONEncoder
import re
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.

from mcq.permissions import IsTeacherOrStudent
from mcq.models import MCQ, MCQ_Question
from mcq.serializers import MCQSerializer, MCQQuestionsSerializer, StudentAnswersSerializer
from courses.models import Courses, StudentJoinedCourses
from authentication.models import User
from rest_framework.parsers import JSONParser


class MCQView(APIView):
    permissions_classes = (IsAuthenticated, IsTeacherOrStudent)
    parser_classes = (JSONParser,)

    def post(self, request, course_id, *args, **kwargs):
        user = request.user
        if request.user.usertype == 'teacher':
            try:
                course = user.courses_set.get(id=course_id)
                mcqs = course.mcq_set.all()
                serializer = MCQSerializer(
                    mcqs, context={'request': request, "parent": True}, many=True)
                return JsonResponse(serializer.data, safe=False)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        else:
            try:
                studentcourse = StudentJoinedCourses.objects.get(
                    course__id=course_id, student=user)
                course = studentcourse.course
                mcqs = course.mcq_set.all()
                serializer = MCQSerializer(
                    mcqs, context={'request': request, "parent": True}, many=True)
                return JsonResponse(serializer.data, safe=False)
            except StudentJoinedCourses.DoesNotExist:
                return JsonResponse({'error': 'You are not affiliated to this course'}, status=400)

    def put(self, request, course_id, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
                if course_id != int(request.data.get('course')):
                    return JsonResponse({'error': 'Course id does not match'}, status=400)

                serializer = MCQSerializer(data=request.data, context={
                    'request': request, "parent": False})
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=201)
                return JsonResponse(serializer.errors, status=400)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)


class MCQDetailView(APIView):
    permissions_classes = (IsAuthenticated, IsTeacherOrStudent)

    def post(self, request, course_id, mcqid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
                mcq = course.mcq_set.get(id=mcqid)
                serializer = MCQSerializer(
                    mcq, context={'request': request, "parent": False}, many=False)
                return JsonResponse(serializer.data, safe=False)
            except Courses.DoesNotExist or MCQ.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        else:
            try:
                studentcourse = StudentJoinedCourses.objects.get(
                    course__id=course_id, student=request.user)
                course = studentcourse.course
                mcq = course.mcq_set.get(id=mcqid)
                serializer = MCQSerializer(
                    mcq, context={'request': request, "parent": False})
                return JsonResponse(serializer.data, safe=False)
            except StudentJoinedCourses.DoesNotExist or MCQ.DoesNotExist:
                return JsonResponse({'error': 'You are not affiliated to this course or mcq doesnt exist'}, status=400)

    def put(self, request, course_id, mcqid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
                mcq = course.mcq_set.get(id=mcqid)
                if course_id != int(request.data.get('course')):
                    return JsonResponse({'error': 'Course id does not match'}, status=400)

                serializer = MCQSerializer(mcq, data=request.data, context={
                    'request': request, "parent": False})
                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data, status=201)
                else:
                    return JsonResponse(serializer.errors, status=400)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)

    def delete(self, request, course_id, mcqid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
                mcq = course.mcq_set.get(id=mcqid)
                mcq.delete()
                return JsonResponse({'message': 'MCQ deleted'}, status=200)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)


class MCQQuestionsView(APIView):
    permissions_classes = (IsAuthenticated, IsTeacherOrStudent)

    def post(self, request, course_id, mcqid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
                mcq = course.mcq_set.get(id=mcqid)
                questions = mcq.mcq_question_set.all()
                serializer = MCQQuestionsSerializer(
                    questions, context={'request': request, "parent": True}, many=True)
                return JsonResponse(serializer.data, safe=False)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'Course does not exist'}, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)

    def put(self, request, course_id, mcqid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            course = request.user.courses_set.get(id=course_id)
            try:
                mcq = course.mcq_set.get(id=mcqid, course=course)
            except MCQ.DoesNotExist:
                return JsonResponse({'error': 'MCQ does not exist'}, status=400)
            serializer = MCQQuestionsSerializer(
                data=request.data, context={'request': request, "parent": False})
            print("hellp")
            if serializer.is_valid():
                serializer.save()
                print("hello")
                return JsonResponse(serializer.data, status=201)
            print(serializer.errors)
            return JsonResponse(serializer.errors, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)


class MCQQuestionsDetailView(APIView):
    permissions_classes = (IsAuthenticated, IsTeacherOrStudent)

    def post(self, request, course_id, mcqid, questionid, *args, **kwargs):
        try:
            if request.user.usertype == 'teacher':
                course = request.user.courses_set.get(id=course_id)
            else:
                user = request.user
                courses = StudentJoinedCourses.objects.filter(
                    student=user, course__id=course_id)
                if not courses.exists():
                    return JsonResponse({'error': 'You are not affiliated to this course'}, status=400)
                course = courses.first()
        except Courses.DoesNotExist:
            return JsonResponse({'error': 'MCQ does not exist'}, status=400)

        try:
            mcq = course.mcq_set.get(id=mcqid, course=course)
        except MCQ.DoesNotExist:
            return JsonResponse({'error': 'MCQ does not exist'}, status=400)

        try:
            question = mcq.mcq_question_set.get(id=questionid)
            serializer = MCQQuestionsSerializer(question, many=False)
            return JsonResponse(serializer.data, status=200)
        except MCQ_Question.DoesNotExist:
            return JsonResponse({'error': 'Question does not exist'}, status=400)

    def put(self, request, course_id, mcqid, questionid, *args, **kwargs):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'MCQ does not exist'}, status=400)
            try:
                mcqquestions = MCQ_Question.objects.get(
                    id=questionid, mcq__id=mcqid, mcq__course=course)
            except MCQ_Question.DoesNotExist:
                return JsonResponse({'error': 'Question does not exist'}, status=400)

            serializer = MCQQuestionsSerializer(
                mcqquestions, request.data, context={'request': request, "parent": False}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)

    def delete(self, request, course_id, mcqid, questionid):
        if request.user.usertype == 'teacher':
            try:
                course = request.user.courses_set.get(id=course_id)
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'MCQ does not exist'}, status=400)

            try:
                mcqquestions = MCQ_Question.objects.get(
                    id=questionid, mcq__id=mcqid, mcq__course=course)
            except MCQ_Question.DoesNotExist:
                return JsonResponse({'error': 'Question does not exist'}, status=400)

            mcqquestions.delete()
            return JsonResponse({'message': 'Question deleted'}, status=200)
        return JsonResponse({'error': 'Only Course Teacher is Authorized'}, status=400)


class MCQAnswerView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrStudent)

    def post(self, request, course_id, mcqid, questionid, username, *args, **kwargs):
        if request.user.usertype == "teacher":
            try:
                user = User.objects.get(username=username)
            except:
                return JsonResponse({'error': 'Student does not exist'}, status=400)
        else:
            user = request.user

        try:
            studentcourse = StudentJoinedCourses.objects.get(
                student=user, course__id=course_id)
            course = studentcourse.course
        except StudentJoinedCourses.DoesNotExist:
            return JsonResponse({'error': 'Student is not affiliated to this course'}, status=400)

        try:
            mcq_question = MCQ_Question.objects.get(
                id=questionid, mcq__id=mcqid, mcq__course=course)
            mcq_answers = mcq_question.studentanswers_set.filter(student=user)
            if mcq_answers.exists():
                serializer = StudentAnswersSerializer(
                    mcq_answers.first(), many=False)
                return JsonResponse(serializer.data, status=200)
            return JsonResponse({'error': 'Answer does not exist'}, status=400)

        except MCQ_Question.DoesNotExist:
            return JsonResponse({'error': 'Question does not exist'}, status=400)

    def put(self, request, course_id, mcqid, questionid, *args, **kwargs):
        if request.user.usertype == 'student':
            try:
                user = request.user
                courses = StudentJoinedCourses.objects.filter(
                    student=user, course__id=course_id)
                if not courses.exists():
                    return JsonResponse({'error': 'You are not affiliated to this course'}, status=400)
                course = courses.first().course
            except Courses.DoesNotExist:
                return JsonResponse({'error': 'You are not affiliated to this course'}, status=400)

            try:
                mcq = course.mcq_set.get(id=mcqid)
            except MCQ.DoesNotExist:
                return JsonResponse({'error': 'MCQ does not exist'}, status=400)

            try:
                mcq = MCQ_Question.objects.get(id=questionid, mcq=mcq)
            except MCQ_Question.DoesNotExist:
                return JsonResponse({'error': 'MCQ Question does not exist'}, status=400)

            mcqanswer = mcq.studentanswers_set.get(student=user)
            serializer = StudentAnswersSerializer(instance=mcqanswer, data=request.data, context={
                                                  'request': request, "parent": False}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        return JsonResponse({'error': 'Only Student is Authorized'}, status=400)
