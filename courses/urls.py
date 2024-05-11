from django.urls import path, include

from courses.views import CoursesView, CoursesDetailView, StudentJoinedCoursesDetailView, SearchCoursesView
urlpatterns = [
    path('', CoursesView.as_view(), name="teacher_courses"),
    path('<int:course_id>/', CoursesDetailView.as_view(),
         name="teacher_course_detail"),
    path('<int:course_id>/join/<str:username>/',
         StudentJoinedCoursesDetailView.as_view(), name="student_joined_courses_detail"),
    path('search/', SearchCoursesView.as_view(), name="search_courses"),
    path('<int:course_id>/mcq/', include('mcq.urls')),
    path('<int:course_id>/assignment/', include('assignments.urls')),
]
