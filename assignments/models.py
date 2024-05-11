from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from courses.models import Courses
from authentication.models import User


def filefield(instance, filename):
    return f'courses/{instance.assignment.id}/{filename}'

# Create your models here.


class Assignment(models.Model):
    assignment_name = models.CharField(
        _('Assignment name'), max_length=80, null=False, blank=False)
    file = models.FileField(
        _('Question file'), upload_to='assignment/', null=False, blank=False)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    deadline = models.DateTimeField(
        _('Deadline'), null=False, blank=True, default=timezone.now)
    description = models.TextField(_('Description'), null=False, blank=False)
    created_on = models.DateTimeField(
        _('Created on'), blank=True, null=False, default=timezone.now)
    points = models.IntegerField(
        _('Assignment Points'), default=0, blank=True, null=False)

    def __str__(self):
        return self.course.course_name + '->' + self.assignment_name


class StudentSubmitsAssignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    submitted_on = models.DateTimeField(
        _('Submitted on'), auto_now_add=True, blank=True, null=True)
    file = models.FileField(
        _('File'), upload_to=filefield, null=True, blank=True)
    points = models.IntegerField(
        _('Assignment Points'), default=0, blank=True, null=False)

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return self.student.username + ' ' + self.assignment.assignment_name

    @property
    def submission_status(self):
        if self.submitted_on > self.assignment.deadline:
            status = 'late'
        else:
            status = 'early'
        total_seconds = (self.submitted_on -
                         self.assignment.deadline).total_seconds()
        hours = int(total_seconds/3600)
        minute = (total_seconds % 3600)/60
        return f'{status} {hours}h {minute}m'
