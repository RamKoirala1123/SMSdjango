from teacher.views import TeacherView


from django.urls import path

urlpatterns = [
    path('', TeacherView.as_view(), name='teacher_home')
]
