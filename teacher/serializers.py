from rest_framework import serializers
from .models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    image_cv = serializers.ImageField(required=False)
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        fields = ('username', 'salary', 'qualifications',
                  'bio', 'stream', 'image_cv', 'department_name')
        model = Teacher
        extra_kwargs = {"image_cv": {"required": False}}
        read_only_fields = ('salary',)

    def create(self, validated_data):
        qualifications = validated_data.pop('qualifications', None)
        instance = super(TeacherSerializer, self).create(validated_data)

        if qualifications:
            qualification = {
                'phd': qualification.get('phd', None),
                'master': qualifications.get('masters', None),
                'bachelor': qualifications.get('bachelor', None)
            }
            instance.qualifications = qualification

        instance.save()
        return instance

    def update(self, instance, validated_data):
        qualifications = validated_data.pop('qualifications', None)
        if qualifications:
            qualification = {
                'master': qualifications.get('master', instance.qualifications.get('master', None)),
                'bachelor': qualifications.get('bachelor', instance.qualifications.get('bachelor', None)),
                'phd': qualifications.get('phd', instance.qualifications.get('phd', None))
            }
            qualification = {k: v for k,
                             v in qualification.items() if v is not None}
            instance.qualifications = qualification
        return super(TeacherSerializer, self).update(instance, validated_data)
