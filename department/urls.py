from django.urls import path

from department.views import DepartmentsView, DepartmentDetailView, SectionDetailView, AssignTeacherView, DepartmentAssignsDetailView

urlpatterns = [
    path('', DepartmentsView.as_view(), name="departments_view"),
    path('<str:name>/', DepartmentDetailView.as_view(),
         name="department_detail_view"),
    path('sections/<str:name>/', SectionDetailView.as_view(),
         name="section_detail_view"),
    path('assign/<str:departname>/', AssignTeacherView.as_view(),
         name='assign_teacher_view'),
    path('assign/<str:departname>/<str:username>/',
         DepartmentAssignsDetailView.as_view(), name='department_assigns_detail_view')
    # path('assgin/', SectionsView.as_view(), name="sections_view"),
]
