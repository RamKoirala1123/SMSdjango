from django.forms import ValidationError
from rest_framework import serializers
from django.db import transaction

from authentication.models import User, Notice

from student.models import Student
from teacher.models import Teacher


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(allow_blank=True, allow_null=True)
    usertype = serializers.CharField(allow_blank=True, allow_null=True)
    image_url = serializers.SerializerMethodField(method_name='get_image_url')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'is_staff',
                  'date_joined', 'is_active', 'gender', 'usertype', 'email_from_work', 'dob', 'image_url')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('date_joined', 'is_active', 'image_url')

    def create(self, validated_data):
        try:
            password = validated_data.pop("password")
            instance = super(UserSerializer, self).create(validated_data)
            instance.set_password(password)
            with transaction.atomic():
                instance.save()
                try:
                    if instance.usertype == 'student':
                        Student.objects.create(user=instance)
                    elif (instance.usertype == 'teacher'):
                        Teacher.objects.create(user=instance)
                except Exception as e:
                    raise ValidationError("Usertype is not valid")

            return instance

        except Exception as e:
            raise serializers.ValidationError(detail=e)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if obj.image else None

class NoticeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields='__all__'