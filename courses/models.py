from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.models import User
from courses.validators import validate_semester
from department.models import Sections


class Courses(models.Model):
    course_name = models.CharField(
        _('Course name'), max_length=80, null=False, blank=False)
    course_code = models.CharField(
        _('Course code'), max_length=10, null=False, blank=False)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.DateField(
        _('Year'), null=False, blank=True, default=timezone.now)
    semester = models.CharField(
        _('Semester IV/I'), max_length=4, validators=(validate_semester,), null=False, blank=False)
    link = models.URLField(_('Course Tutor'), null=True, blank=True)

    class Meta:
        unique_together = ('course_code', 'section', 'year')

    def __str__(self):
        return self.course_code + '->' + str(self.section)

    def save(self, *args, **kwargs):
        self.course_code = self.course_code.upper()
        self.semester = self.semester.lower()
        super(Courses, self).save(*args, **kwargs)


class StudentJoinedCourses(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    joined_on = models.DateTimeField(
        blank=True, null=False, default=timezone.now)
    accepted = models.BooleanField(_("accepted to course"), default=False)

    def __str__(self):
        return self.student.username + ' ' + self.course.course_name

    class Meta:
        unique_together = ('student', 'course')
