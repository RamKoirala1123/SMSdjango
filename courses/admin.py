from django.contrib import admin

from courses.models import Courses, StudentJoinedCourses
# Register your models here.


admin.site.register(Courses)
admin.site.register(StudentJoinedCourses)
