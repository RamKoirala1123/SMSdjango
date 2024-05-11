from django.db import transaction
from django.utils import timezone
from requests import request
from rest_framework import serializers

from assignments.models import Assignment, StudentSubmitsAssignment
from courses.models import Courses
from authentication.models import User

class StudentAssignmentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='student.username')
    assignment_id = serializers.IntegerField(source='assignment.id')
    file_url = serializers.SerializerMethodField(method_name='get_file_url')
    submission_status = serializers.ReadOnlyField()

    class Meta:
        model = Assignment
        fields = ('id', 'username', 'assignment_id', 'points'
                  , 'file_url', 'file', 'submission_status')
        read_only_fields = ('points',
                            'file_url')
        extra_kwargs = {'file': {"required":False}}

    def get_file_url(self, obj):
        return self.context.get('request').build_absolute_uri(obj.file.url) if obj.file else None

    def update(self, instance, validated_data):
        student_name = validated_data.pop('student')
        assignment_name = validated_data.pop('assignment')
        try:
            student = User.objects.get(username=student_name.get('username',None))
        except  User.DoesNotExist:
            raise serializers.ValidationError('User is not a student')
        instance.submitted_on = timezone.now()

        super(StudentAssignmentSerializer, self).update(
            instance, validated_data)
        return instance

    def __init__(self, *args, **kwargs):
        super(StudentAssignmentSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.usertype == 'teacher':
            self.fields['points'].read_only = False
            # self.fields['file'].read_only = True
            # self.fields['file'].write_only = False

    # def create(self,validated_data):
    #     print(validated_data)
    #     request = self.context.get('request')
    #     if request.user and request.user.usertype == 'student':
    #         validated_data.pop('username')
    #         print(validated_data)
    #         user = request.user
    #     else:
    #         raise serializers.ValidationError("Not a student")
    #     instance = super().create(validated_data)
    #     instance.student = user
    #     instance.save()
    #     return instance

class AssignmentsSerializer(serializers.ModelSerializer):
    course = serializers.IntegerField(source='course.id')
    file_url = serializers.SerializerMethodField(method_name='get_file_url')
    student_assignments = serializers.SerializerMethodField(
        method_name='get_student_assignments')

    class Meta:
        model = Assignment
        fields = ('id', 'course', 'assignment_name', 'description', 'points',
                  'deadline', 'file', 'created_on', 'file_url', 'student_assignments')
        read_only_fields = ('created_on','file_url')
        extra_kwargs = {'file': {'write_only': True}}

    def create(self, validated_data):
        print(validated_data)
        course = validated_data.get('course', None)
        try:
            with transaction.atomic():
                instance = super(AssignmentsSerializer,
                                 self).create(validated_data)
                instance.save()
                course = Courses.objects.get(id=course.id)
                studentsjoined = course.studentjoinedcourses_set.all().filter(accepted=True)
                for record in studentsjoined:
                    studentassignment = StudentSubmitsAssignment(
                      assignment=instance,  student=record.student)
                    studentassignment.save()

        except Courses.DoesNotExist:
            raise serializers.ValidationError(
                'Course does not exist')

        return instance

    def get_student_assignments(self, obj):
        data = obj.studentsubmitsassignment_set.all()
        serializer = StudentAssignmentSerializer(data, many=True, context={'request':self.context.get('request')})
        return serializer.data

    def get_file_url(self, obj):
        return self.context.get('request').build_absolute_uri(obj.file.url) if obj.file else None

    def to_representation(self, instance):
        ret = super(AssignmentsSerializer, self).to_representation(instance)
        request = self.context.get("request")
        if(request.user.usertype == "student"):
            ret.pop("student_assignments")
        return ret
