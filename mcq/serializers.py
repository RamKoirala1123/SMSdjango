from django.utils import timezone
from rest_framework import serializers
import re

from mcq.models import MCQ, MCQ_Question, StudentAnswers
from authentication.models import User
from courses.models import Courses, StudentJoinedCourses


class MCQQuestionsSerializer(serializers.ModelSerializer):
    mcq = serializers.IntegerField(source="mcq.id")

    class Meta:
        model = MCQ_Question
        fields = ('id', 'index', 'mcq', 'question',
                  'options', 'marks', 'answer')
        read_only_fields = ('id', 'index', 'question',
                            'options', 'marks',)
        extra_kwargs = {'answer': {'write_only': True}}

    def __init__(self, *args, **kwargs):
        super(MCQQuestionsSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.user.usertype == 'teacher':
            for i in ('marks', 'question', 'options', 'index'):
                self.fields[i].read_only = False
            self.fields['answer'].write_only = False
            self.fields['answer'].read_only = False
        elif request and request.user.usertype == 'student':
            if request.method == 'PUT' and self.is_valid(raise_exception=True):
                id = self.validated_data.get('id', None)
                try:
                    mcq_question = MCQ_Question.objects.get(id=id)
                    if mcq_question.mcq.visibility:
                        self.fields['answer'].write_only = False
                        self.fields['answer'].read_only = True
                except MCQ_Question.DoesNotExist:
                    raise serializers.ValidationError(
                        'MCQ_Question does not exist')

    def create(self, validated_data):
        options = validated_data.pop('options', None)
        mcqname = validated_data.pop('mcq', None)
        try:
            mcq = MCQ.objects.get(id=mcqname.get("id"))
        except MCQ.DoesNotExist:
            raise serializers.ValidationError("Mcq does not exist")

        # instance = super(MCQQuestionsSerializer, self).create(
        #     validated_data)
        instance = MCQ_Question(**validated_data)
        instance.mcq = mcq
        if options:
            for key, value in options.items():
                if re.match(r"option[1|2|3|4]{1}", key):
                    instance.options[key] = value
                else:
                    raise serializers.ValidationError(
                        "Invalid options key and should be in format option{1..4}")
        instance.save()
        return instance

    def update(self, instance, validated_data):
        options = validated_data.pop('options', None)
        mcq = validated_data.pop('mcq', None)

        if options:
            for key, value in options.items():
                if re.match(r"option[1|2|3|4]{1}", key):
                    instance.options[key] = value
                else:
                    raise serializers.ValidationError(
                        "Invalid options key and should be in format option{1..4}")
        return super(MCQQuestionsSerializer, self).update(instance, validated_data)


class MCQSerializer(serializers.ModelSerializer):
    mcq_questions = serializers.SerializerMethodField(
        method_name='get_mcq_questions')
    course = serializers.IntegerField(source='course.id')

    class Meta:
        model = MCQ
        fields = ('id', 'name', 'description', 'start_time', 'course',
                  'end_time', 'total_time', 'total_marks', 'visibility', 'mcq_questions')
        read_only_fields = ('total_marks', 'total_time', 'id')
        # extra_kwargs = {"course":{"required":True}}

    def __init__(self, *args, **kwargs):
        super(MCQSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request.user.usertype == 'teacher':
            for field in self.Meta.fields:
                self.fields[field].read_only = True if field in MCQSerializer.Meta.read_only_fields else False
        else:
            for field in self.Meta.fields:
                if field not in MCQSerializer.Meta.read_only_fields:
                    self.fields[field].read_only = True

    def create(self, validated_data):
        # print(validated_data)
        coursename = validated_data.pop('course', None)
        try:
            course = Courses.objects.get(id=coursename.get("id"))
        except Courses.DoesNotExist:
            raise serializers.ValidationError("Course doesn't exist")
        mcq = MCQ.objects.create(course=course, **validated_data)
        mcq.save()
        return mcq

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def get_mcq_questions(self, obj):
        mcqquestions = obj.mcq_question_set.all()
        request = self.context.get("request")
        serializer = MCQQuestionsSerializer(
            mcqquestions, context={"request": request}, many=True)
        return serializer.data

    def to_representation(self, instance):
        ret = super(MCQSerializer, self).to_representation(instance)
        request = self.context.get("request")
        parent = self.context.get("parent")
        if (request.user.usertype == 'student' and instance.start_time > timezone.now()) or parent:
            ret.pop('mcq_questions')
        return ret


class StudentAnswersSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.username')
    mcq = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MCQ_Question
        fields = ('id', 'mcq', 'answer', 'student')

    def create(self, validated_data):
        username = validated_data.pop('student')
        mcqid = validated_data.pop('mcq')
        try:
            mcq = MCQ_Question.objects.get(id=mcqid)
        except MCQ_Question.DoesNotExist:
            raise serializers.ValidationError("MCQ does not exist")

        instance = super(StudentAnswersSerializer, self).create(validated_data)
        try:
            user = User.objects.get(username=username)
            instance.student = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User Doesn't exist")
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if instance.mcq.mcq.start_time <= timezone.now() and instance.mcq.mcq.end_time >= timezone.now():
            instance.answer = validated_data.get('answer', instance.answer)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "You can't update answers before the start time or after the end time")
