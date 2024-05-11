from django.db import reset_queries
from rest_framework.permissions import BasePermission


class IsTeacherOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.usertype == 'teacher' or request.user.usertype == 'staff'
