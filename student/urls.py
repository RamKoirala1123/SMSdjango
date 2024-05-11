from django.urls import path

from student.views import StudentView
urlpatterns = [
    path('', StudentView.as_view(), name='student'),
]
