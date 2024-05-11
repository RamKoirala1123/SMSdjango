from rest_framework import permissions


class IsNotAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS) or (request.user and not request.user.is_authenticated and request.method == 'POST')
