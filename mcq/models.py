from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from courses.models import Courses, StudentJoinedCourses
from authentication.models import User
from django.db import transaction


class MCQ(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    name = models.CharField(
        _('Name of MCQ'), max_length=100, blank=True, null=False)
    description = models.CharField(
        _('Description '), max_length=200, blank=True, null=False)
    start_time = models.DateTimeField(
        _('MCQ start_time'), null=False, blank=False)
    end_time = models.DateTimeField(
        _('MCQ end_time'), null=False, blank=False)
    visibility = models.BooleanField(
        _('Can read Answers)'), default=False, blank=True)

    def __str__(self):
        return self.course.course_name + ' ' + self.name

    @property
    def total_marks(self) -> int:
        return self.mcq_question_set.all().aggregate(models.Sum('marks'))['marks__sum']

    @property
    def total_time(self) -> int:
        total_seconds = (self.end_time - self.start_time).total_seconds()
        return total_seconds
        # hours = total_seconds // 3600
        # minutes = (total_seconds % 3600) // 60
        # seconds = (total_seconds % 3600) % 60
        # return {
        #     'hours': hours,
        #     'minutes': minutes,
        #     'seconds': seconds
        # }


class MCQ_Question(models.Model):
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE)
    index = models.IntegerField(_('Question Index'), null=False, blank=False)
    question = models.CharField(
        _('MCQ Question'), max_length=200, blank=False, null=False)
    options = models.JSONField(
        _('MCQ Options'), default=dict, null=False, blank=False)
    marks = models.IntegerField(
        _('Marks'), null=False, blank=False)
    answer = models.IntegerField(_('answer number'), null=False, blank=False)

    class Meta:
        unique_together = ('mcq', 'index')

    def __str__(self):
        return self.mcq.name + ' ' + self.question

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.index is None:
            self.index = self.mcq.mcq_question_set.all().count() + 1

        if not self.studentanswers_set.filter().exists():
            with transaction.atomic():
                course = self.mcq.course
                super().save(force_insert, force_update, using, update_fields)
                studentsjoined = StudentJoinedCourses.objects.filter(
                    course=course, accepted=True)
                for records in studentsjoined:
                    student = StudentAnswers(mcq=self, student=records.student)
                    student.save()
        else:
            super().save(force_insert, force_update, using, update_fields)


class StudentAnswers(models.Model):
    mcq = models.ForeignKey(MCQ_Question, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.IntegerField(
        _('MCQ Answer'), null=True, blank=True)

    class Meta:
        unique_together = ('mcq', 'student')

    def __str__(self):
        return self.mcq.mcq.name + ' ' + self.student.username

    @property
    def mark_obtained(self) -> int:
        return self.mcq.marks if self.mcq.answer == self.answer else 0
