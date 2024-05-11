from django.urls import path

from assignments.views import AssignmentView, AssignmentDetailView, StudentSubmitsAssignmentView
urlpatterns = [
    path('', AssignmentView.as_view(), name="assignment_view"),
    path('<int:assignment_id>/',
         AssignmentDetailView.as_view(), name="assignment_detail_view"),
    path('<int:assignment_id>/<str:username>/',
         StudentSubmitsAssignmentView.as_view(), name="student_submits_detail_view"),
]
