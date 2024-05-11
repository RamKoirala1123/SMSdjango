from rest_framework import serializers
from department.models import Department
from student.models import Student


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username', read_only=True)
    department_name = serializers.SerializerMethodField(
        method_name='get_department_name')

    class Meta:
        model = Student
        fields = ('username', 'current_semester', 'bio',
                  'section', 'department_name')
        read_only_fields = ('current_semester',)

    def create(self, validated_data):
        try:
            user = Student.objects.get(
                user__username=validated_data.pop('username', None))
        except Student.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'User does not exist'})

        student = Student.objects.create(user=user, **validated_data)
        return student

    def get_section_name(self, obj):
        return obj.section.name

    def get_department_name(self, obj):
        return obj.section.department.name if obj.section else None
