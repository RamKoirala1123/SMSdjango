from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.usertype == 'teacher' or request.user.usertype == 'student'
