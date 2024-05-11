from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from authentication.models import User
from authentication.storage import OverwriteStorage
from department.models import Department


def upload_teacher_image(instance, filename):
    return f'userprofile/{instance.user.id}/{filename}'


class Teacher(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True,
                                help_text=_(''),
                                verbose_name="teacher user",)

    salary = models.DecimalField(
        _('salary'),
        max_digits=8,
        decimal_places=2,
        help_text=_('Max length = 8 and precision is limited to 2'), blank=True, null=True)

    qualifications = models.JSONField(
        _('qualifications'),
        help_text=_(''), blank=True, default=dict)

    bio = models.CharField(
        _('bio'),
        max_length=200,
        help_text=_('Text cannot exceed 100 characters.'), null=True, blank=True)

    image_cv = models.ImageField(_('CV'), storage=OverwriteStorage(
    ), upload_to=upload_teacher_image, blank=True, null=True)

    stream = models.CharField(
        _('Teacher Teaches'), max_length=100, blank=True, null=True)

    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
