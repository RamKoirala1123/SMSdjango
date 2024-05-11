from django.contrib import admin

# Register your models here.
from mcq.models import MCQ, MCQ_Question, StudentAnswers

admin.site.register(MCQ)
admin.site.register(MCQ_Question)
admin.site.register(StudentAnswers)
