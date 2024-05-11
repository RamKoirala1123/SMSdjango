from ast import Assign
from django.contrib import admin

# Register your models here.

from assignments.models import Assignment, StudentSubmitsAssignment
admin.site.register(Assignment)
admin.site.register(StudentSubmitsAssignment)