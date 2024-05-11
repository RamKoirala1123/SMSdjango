from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from authentication.models import User
from department.models import Sections


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(_('bio'), max_length=200, blank=True, null=False)
    section = models.ForeignKey(
        Sections, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def current_semester(self):  # needs to updata after making section
        return "I/V"
