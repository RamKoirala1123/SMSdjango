from rest_framework import permissions


class IsATeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.usertype == 'teacher'
