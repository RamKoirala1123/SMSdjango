from asyncore import read
from rest_framework import serializers

from courses.models import Courses, StudentJoinedCourses
from department.models import DepartmentAssigns, Sections
from department.models import Department
from mcq.serializers import MCQSerializer
from assignments.serializers import AssignmentsSerializer


class StudentJoinedCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentJoinedCourses
        fields = '__all__'
        extra_kwargs = {'accepted': {'write_only': True}}


class CoursesSerializer(serializers.ModelSerializer):
    section = serializers.CharField(required=True,source='section.name')
    students = StudentJoinedCoursesSerializer(many=True, read_only=True)
    assignments = serializers.SerializerMethodField(
        method_name='get_assignments')
    mcq = serializers.SerializerMethodField(method_name='get_mcq')

    class Meta:
        model = Courses
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        request = self.context.get('request')
        section = validated_data.pop('section')
        try:
            section = Sections.objects.get(name=section.get('name'))
            department = section.department
            department = DepartmentAssigns.objects.get(
                user=request.user, department=department)
        except Sections.DoesNotExist or DepartmentAssigns.DoesNotExist:
            raise serializers.ValidationError(
                'Section does not exist')
        # instance =(CoursesSerializer, self).create(validated_data)
        instance = Courses(**validated_data)
        instance.section = section
        instance.teacher = request.user
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance = super(CoursesSerializer, self).update(
            instance, validated_data)
        instance.save()
        return instance

    def get_mcq(self, obj):
        data = obj.mcq_set.all()
        request = self.context.get('request')
        serializer = MCQSerializer(
            data, context={"request": request, "parent": True}, many=True)
        return serializer.data

    def get_assignments(self, obj):
        data = obj.assignment_set.all()
        request = self.context.get('request')
        serializer = AssignmentsSerializer(
            data, context={"request": request}, many=True)
        return serializer.data

    def to_representation(self, instance):
        data = super(CoursesSerializer, self).to_representation(instance)
        search = self.context.get("search", None)
        if search:
            data.pop("students")
            data.pop("assignemnts")
            data.pop("mcq")
            data.pop("link")
        return data
