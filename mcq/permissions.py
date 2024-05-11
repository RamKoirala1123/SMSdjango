from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):
    def has_permission(self, request, view):
        usertype = ('teacher', 'student')
        return request.user and request.user.is_authenticated and (request.user.usertype in usertype)
