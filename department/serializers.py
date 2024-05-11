from tempfile import TemporaryFile
from rest_framework import serializers

from department.models import Department, DepartmentAssigns, Sections
from authentication.models import User


class SectionSerializer(serializers.ModelSerializer):
    department = serializers.CharField(
        source='department.name', read_only=True)

    class Meta:
        model = Sections
        fields = ('name', 'department', 'description')


class DepartmentSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField(method_name='get_sections')

    dean = serializers.ReadOnlyField(source='dean.username')
    department_photos = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ('name', 'phone', 'email', 'dean', 'msg',
                  'department_photos', 'sections')

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    def get_department_photos(self, obj):
        data = obj.department_photos.all()
        request = self.context.get('request')
        data = [request.build_absolute_uri(photo.image.url) for photo in data]
        return data

    def get_sections(self, obj):
        data = obj.sections_set.all()
        serializer = SectionSerializer(data, many=True)
        return serializer.data


class DepartmentAssignsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    departmentname = serializers.CharField(source='department.name')

    class Meta:
        model = DepartmentAssigns
        fields = ('id', 'username', 'departmentname',
                  'amount', 'enddate', 'assigned_date')
        read_only_fields = ('id', 'assigned_date')

    def create(self, validated_data):
        username = validated_data.pop('user')['username']
        departmentname = validated_data.pop('department')['name']
        try:
            user = User.objects.get(username=username)
            department = Department.objects.get(name=departmentname)
            if(user.usertype != 'teacher'):
                raise serializers.ValidationError(
                    {'username': 'User is not a teacher'})
            instance = super(DepartmentSerializer, self).create(validated_data)
            instance.user = user
            instance.department = department
            instance.save()
            return instance
        except Department.DoesNotExist or User.DoesNotExist as E:
            raise serializers.ValidationError(E)

    def update(self, instance, validated_data):
        username = validated_data.pop('user')['username']
        departmentname = validated_data.pop('department')['name']

        try:
            user = User.objects.get(username=username)
            department = Department.objects.get(name=departmentname)
            instance.user = user
            instance.department = department
        except:
            raise serializers.ValidationError(
                {'username': 'User does not exist', 'departmentname': 'Department does not exist'})
        return super(DepartmentAssignsSerializer, self).update(
            instance, validated_data)
